"""Resume the frozen v2.1 grid after an external interruption (not a frozen file).

The frozen launcher experiments/tfm/run_grid_v2_1.py refuses existing roots by design, so an
interrupted grid needs an explicit, recorded resume. This script:
- verifies the v2.1 freeze before doing anything;
- treats a unit as complete only if experiments/runs/v2_1/<unit>/ exists with a completed
  attempt.json AND its archive copy exists; such units are never rerun;
- moves (never deletes) every interrupted <unit>.partial directory to
  experiments/runs/v2_1_interrupted/<unit>.partial.<UTC stamp>/ and lists it in the resume record;
- runs every remaining unit with the frozen experiments/tfm/run_v2.py, the same --threads and
  output root, archiving exactly like the frozen launcher (attempt/meta/scores + SHA-256 map);
- writes experiments/archive/v2_1_runs/resume_<stamp>.json and resume_progress_<stamp>.json,
  leaving the original launch.json/progress.json untouched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cric_ed.v2_contract import CONDITIONS, SEEDS, TABLES, verify_freeze  # noqa: E402

OUT = ROOT / "experiments/runs/v2_1"
ARCHIVE = ROOT / "experiments/archive/v2_1_runs"
INTERRUPTED = ROOT / "experiments/runs/v2_1_interrupted"


def now():
    return datetime.now(timezone.utc).isoformat()


def completed(name: str) -> bool:
    run, arch = OUT / name, ARCHIVE / name
    if not (run.is_dir() and arch.is_dir()):
        return False
    attempt = json.loads((run / "attempt.json").read_text(encoding="utf-8"))
    return attempt.get("status") == "completed" and all((arch / f).is_file() for f in
                                                        ("attempt.json", "meta.json", "scores.npz",
                                                         "artifacts_sha256.json"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--threads", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.workers < 1 or a.threads < 1 or a.workers * a.threads > 9:
        ap.error("Use at most nine declared CPU threads total on this host (frozen launcher limit)")
    launch = json.loads((ARCHIVE / "launch.json").read_text(encoding="utf-8"))
    if a.threads != launch["threads_per_process"]:
        ap.error("threads per process must equal the frozen launch value")
    identity = verify_freeze(ROOT)
    if identity["source_snapshot_sha256"] != launch["source_snapshot_sha256"]:
        raise SystemExit("Source snapshot differs from the original launch")
    grid = [[t, c, s] for c in CONDITIONS for s in SEEDS for t in TABLES]
    if grid != launch["grid"]:
        raise SystemExit("Grid order/content differs from the original launch")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    done = [f"{t}__{c}__s{s}" for t, c, s in grid if completed(f"{t}__{c}__s{s}")]
    moved = []
    for p in sorted(OUT.glob("*.partial")):
        dest = INTERRUPTED / f"{p.name}.{stamp}"
        moved.append({"from": str(p.relative_to(ROOT)), "to": str(dest.relative_to(ROOT)),
                      "attempt": json.loads((p / "attempt.json").read_text(encoding="utf-8"))
                      if (p / "attempt.json").is_file() else None})
    todo = [[t, c, s] for t, c, s in grid if f"{t}__{c}__s{s}" not in done]
    for t, c, s in todo:
        if (OUT / f"{t}__{c}__s{s}").exists():
            raise SystemExit(f"Unit {t}__{c}__s{s} has an output directory but is not complete; resolve manually")
    record = {"started_utc": now(), "reason": "external interruption of the original grid process tree",
              "workers": a.workers, "threads_per_process": a.threads, "python_executable": sys.executable,
              **identity, "completed_before_resume": done, "moved_partials": moved,
              "units_to_run": [f"{t}__{c}__s{s}" for t, c, s in todo]}
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in record.items()
                      if k in ("completed_before_resume", "moved_partials", "units_to_run")}))
    if a.dry_run:
        return
    INTERRUPTED.mkdir(exist_ok=True)
    for m in moved:
        shutil.move(str(ROOT / m["from"]), str(ROOT / m["to"]))
    (ARCHIVE / f"resume_{stamp}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    logs = ARCHIVE / "logs"

    def execute(task):
        table, condition, seed = task
        name = f"{table}__{condition}__s{seed}"
        cmd = [sys.executable, str(ROOT / "experiments/tfm/run_v2.py"), "--table", table,
               "--condition", condition, "--seeds", str(seed), "--threads", str(a.threads), "--out", str(OUT)]
        t0 = time.perf_counter()
        log_path = logs / (name + ".log")
        if log_path.exists():  # keep the interrupted attempt's log
            log_path.rename(logs / f"{name}.interrupted_{stamp}.log")
        print(now(), "START", name, flush=True)
        # No console window and no Fortran console-control handler: a closed console window
        # killed the first resume (forrtl error 200, window-CLOSE event). Results are unaffected.
        env = {**os.environ, "FOR_DISABLE_CONSOLE_CTRL_HANDLER": "1"}
        with log_path.open("w", encoding="utf-8") as log:
            result = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, env=env,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        rec = {"run_id": name, "exit_code": result.returncode, "elapsed_seconds": time.perf_counter() - t0,
               "finished_utc": now()}
        if result.returncode == 0:
            source, dest = OUT / name, ARCHIVE / name
            dest.mkdir()
            for filename in ("attempt.json", "meta.json", "scores.npz"):
                shutil.copyfile(source / filename, dest / filename)
            digests = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir() if p.is_file()}
            (dest / "artifacts_sha256.json").write_text(json.dumps(digests, indent=2) + "\n")
            rec["fit_failure_events"] = len(json.loads((source / "meta.json").read_text())["failures"])
        print(now(), "END", name, "exit", result.returncode, flush=True)
        return rec

    tasks = iter(todo)
    finished, failed = [], False
    progress = ARCHIVE / f"resume_progress_{stamp}.json"
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        running = {pool.submit(execute, t) for t in [next(tasks, None) for _ in range(a.workers)] if t}
        while running:
            done_f, running = wait(running, timeout=30, return_when=FIRST_COMPLETED)
            for f in done_f:
                r = f.result()
                finished.append(r)
                failed |= r["exit_code"] != 0
                progress.write_text(json.dumps({"updated_utc": now(), "runs": finished}, indent=2) + "\n")
            if failed:
                continue
            for _ in done_f:
                t = next(tasks, None)
                if t is not None:
                    running.add(pool.submit(execute, t))
    total = len(done) + sum(r["exit_code"] == 0 for r in finished)
    status = {"status": "completed" if total == 60 and not failed else "incomplete", "finished_utc": now(),
              "completed_units": total, "expected_runs": 60, "resume_runs": finished}
    (ARCHIVE / f"resume_status_{stamp}.json").write_text(json.dumps(status, indent=2) + "\n")
    print(json.dumps({k: status[k] for k in ("status", "completed_units")}), flush=True)


if __name__ == "__main__":
    main()
