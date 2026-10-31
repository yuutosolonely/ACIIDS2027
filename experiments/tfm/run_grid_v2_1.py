"""Execute the full frozen grid with bounded local CPU processes; retain all attempts."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from cric_ed.v2_contract import CONDITIONS, SEEDS, TABLES, verify_freeze


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--out", type=Path, default=ROOT / "experiments/runs/v2_1")
    parser.add_argument("--archive", type=Path, default=ROOT / "experiments/archive/v2_1_runs")
    args = parser.parse_args()
    if args.workers < 1 or args.threads < 1 or args.workers * args.threads > 9:
        parser.error("Use at most nine declared CPU threads total on this host")
    identity = verify_freeze(ROOT)
    if args.out.exists() or args.archive.exists():
        raise FileExistsError("Fresh grid roots required; review attempts explicitly before any retry")
    args.out.mkdir(parents=True)
    args.archive.mkdir(parents=True)
    logs = args.archive / "logs"
    logs.mkdir()
    launch = {"started_utc": now(), "workers": args.workers, "threads_per_process": args.threads,
              "python_executable": sys.executable, **identity,
              "grid": [[t, c, s] for c in CONDITIONS for s in SEEDS for t in TABLES]}
    (args.archive / "launch.json").write_text(json.dumps(launch, indent=2) + "\n")

    def execute(task):
        table, condition, seed = task
        name = f"{table}__{condition}__s{seed}"
        cmd = [sys.executable, str(ROOT / "experiments/tfm/run_v2.py"), "--table", table,
               "--condition", condition, "--seeds", str(seed), "--threads", str(args.threads),
               "--out", str(args.out)]
        t0 = time.perf_counter()
        print(now(), "START", name, flush=True)
        with (logs / (name + ".log")).open("w", encoding="utf-8") as log:
            result = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        record = {"run_id": name, "exit_code": result.returncode, "elapsed_seconds": time.perf_counter() - t0,
                  "finished_utc": now()}
        if result.returncode == 0:
            source, dest = args.out / name, args.archive / name
            dest.mkdir()
            for filename in ("attempt.json", "meta.json", "scores.npz"):
                shutil.copyfile(source / filename, dest / filename)
            # Preserve the large context file locally; archive its exact identity.
            digests = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir() if p.is_file()}
            (dest / "artifacts_sha256.json").write_text(json.dumps(digests, indent=2) + "\n")
            meta = json.loads((source / "meta.json").read_text())
            record["fit_failure_events"] = len(meta["failures"])
        print(now(), "END", name, "exit", result.returncode, flush=True)
        return record

    tasks = iter(launch["grid"])
    finished, failed = [], False
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        running = {pool.submit(execute, next(tasks)) for _ in range(args.workers)}
        while running:
            done, running = wait(running, timeout=30, return_when=FIRST_COMPLETED)
            for future in done:
                record = future.result()
                finished.append(record)
                failed |= record["exit_code"] != 0
                (args.archive / "progress.json").write_text(json.dumps({"updated_utc": now(), "runs": finished}, indent=2) + "\n")
            if failed:
                continue  # do not dispatch more; currently running attempts finish and remain intact
            for _ in done:
                task = next(tasks, None)
                if task is not None:
                    running.add(pool.submit(execute, task))
    result = {"status": "completed" if len(finished) == 60 and not failed else "incomplete",
              "finished_utc": now(), "runs": finished, "expected_runs": 60}
    (args.archive / "grid_status.json").write_text(json.dumps(result, indent=2) + "\n")
    if result["status"] != "completed":
        raise SystemExit("Grid incomplete; preserve attempts and resolve explicitly")
    print("Complete grid: 60 runs. Analysis and artifact audit still required.", flush=True)


if __name__ == "__main__":
    main()
