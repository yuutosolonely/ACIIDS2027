"""Recover an interrupted v2.1 grid into fresh roots without touching old artifacts."""
from __future__ import annotations

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
from cric_ed.v2_contract import CONDITIONS, SEEDS, TABLES, validate_run_metadata, verify_freeze

OLD_RUNS = ROOT / "experiments/runs/v2_1"
OLD_ARCHIVE = ROOT / "experiments/archive/v2_1_runs"
OUT = ROOT / "experiments/runs/v2_1_recovery_20261030"
ARCHIVE = ROOT / "experiments/archive/v2_1_recovery_20261030"
INTERRUPTED = ARCHIVE / "interrupted_attempts"
WORKERS, THREADS = 4, 2


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, value: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def main() -> int:
    identity = verify_freeze(ROOT)
    if OUT.exists() or ARCHIVE.exists():
        raise FileExistsError("Recovery output roots already exist; inspect them, never overwrite")
    original_launch = json.loads((OLD_ARCHIVE / "launch.json").read_text(encoding="utf-8"))
    if original_launch["source_snapshot_sha256"] != identity["source_snapshot_sha256"]:
        raise ValueError("Original grid launch does not match current frozen source")

    OUT.mkdir(parents=True)
    ARCHIVE.mkdir(parents=True)
    (ARCHIVE / "logs").mkdir()
    expected = [(t, c, s) for c in CONDITIONS for s in SEEDS for t in TABLES]
    completed: dict[tuple[str, str, int], dict] = {}
    reused = []
    for table, condition, seed in expected:
        name = f"{table}__{condition}__s{seed}"
        source = OLD_RUNS / name
        attempt_path, meta_path = source / "attempt.json", source / "meta.json"
        if not source.is_dir() or not attempt_path.is_file() or not meta_path.is_file():
            continue
        attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if attempt.get("status") != "completed" or meta.get("status") != "completed":
            continue
        if not all((source / f).is_file() for f in ("scores.npz", "contexts.jsonl")):
            continue
        observed = validate_run_metadata(meta, identity)
        if observed != (table, condition, seed):
            raise ValueError("Run identity mismatch: " + name)
        destination = OUT / name
        shutil.copytree(source, destination)
        digests = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(destination.iterdir()) if p.is_file()}
        prior_audit = OLD_ARCHIVE / name / "artifacts_sha256.json"
        if prior_audit.is_file():
            expected_digests = json.loads(prior_audit.read_text(encoding="utf-8"))
            for filename, digest in expected_digests.items():
                if filename not in digests or digests[filename] != digest:
                    raise ValueError("Archived artifact hash mismatch: " + name + "/" + filename)
        completed[(table, condition, seed)] = {
            "run_id": name, "exit_code": 0, "reused_from": str(source.relative_to(ROOT)),
            "artifact_sha256": digests,
        }
        reused.append(name)

    INTERRUPTED.mkdir()
    preserved_partial = []
    for source in sorted(OLD_RUNS.glob("*.partial")):
        destination = INTERRUPTED / source.name
        shutil.copytree(source, destination)
        digests = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(destination.iterdir()) if p.is_file()}
        (destination / "recovery_copy_sha256.json").write_text(json.dumps(digests, indent=2) + "\n")
        preserved_partial.append({"path": str(destination.relative_to(ROOT)), "sha256": digests})

    launch = {
        "started_utc": now(), "recovery": True, "parent_launch": str((OLD_ARCHIVE / "launch.json").relative_to(ROOT)),
        "workers": WORKERS, "threads_per_process": THREADS, "python_executable": sys.executable,
        **identity, "grid": [list(x) for x in expected], "reused_completed_units": reused,
        "preserved_interrupted_attempts": preserved_partial,
    }
    atomic_json(ARCHIVE / "launch.json", launch)
    progress: dict[tuple[str, str, int], dict] = dict(completed)
    atomic_json(ARCHIVE / "progress.json", {"updated_utc": now(), "runs": list(progress.values()),
                                                   "total_completed": len(completed), "total_expected": 60})

    pending = [x for x in expected if x not in completed]
    failed = False

    def execute(unit: tuple[str, str, int]) -> dict:
        table, condition, seed = unit
        name = f"{table}__{condition}__s{seed}"
        cmd = [sys.executable, str(ROOT / "experiments/tfm/run_v2.py"), "--table", table,
               "--condition", condition, "--seeds", str(seed), "--threads", str(THREADS), "--out", str(OUT)]
        started = time.perf_counter()
        print(now(), "START", name, flush=True)
        with (ARCHIVE / "logs" / (name + ".log")).open("w", encoding="utf-8") as log:
            result = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        record = {"run_id": name, "exit_code": result.returncode,
                  "elapsed_seconds": round(time.perf_counter() - started, 3), "finished_utc": now()}
        source = OUT / name
        if result.returncode == 0:
            meta = json.loads((source / "meta.json").read_text(encoding="utf-8"))
            validate_run_metadata(meta, identity)
            digests = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in sorted(source.iterdir()) if p.is_file()}
            record["fit_failure_events"] = len(meta["failures"])
            record["artifact_sha256"] = digests
            archive_run = ARCHIVE / name
            archive_run.mkdir()
            for filename in ("attempt.json", "meta.json", "scores.npz"):
                shutil.copyfile(source / filename, archive_run / filename)
            (archive_run / "artifacts_sha256.json").write_text(json.dumps(digests, indent=2) + "\n")
        else:
            record["preserved_attempt"] = str(source.relative_to(ROOT)) if source.exists() else None
        print(now(), "END", name, "exit", result.returncode, flush=True)
        return record

    tasks = iter(pending)
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        running = {pool.submit(execute, next(tasks)) for _ in range(min(WORKERS, len(pending)))}
        while running:
            done, running = wait(running, timeout=30, return_when=FIRST_COMPLETED)
            for future in done:
                record = future.result()
                key = next(x for x in pending if f"{x[0]}__{x[1]}__s{x[2]}" == record["run_id"])
                progress[key] = record
                failed |= record["exit_code"] != 0
                atomic_json(ARCHIVE / "progress.json", {"updated_utc": now(), "runs": list(progress.values()),
                                                          "total_completed": sum(r["exit_code"] == 0 for r in progress.values()),
                                                          "total_expected": 60})
            if failed:
                continue
            for _ in done:
                unit = next(tasks, None)
                if unit is not None:
                    running.add(pool.submit(execute, unit))

    succeeded = sum(r["exit_code"] == 0 for r in progress.values())
    status = {"status": "completed" if succeeded == 60 and not failed else "incomplete",
              "finished_utc": now(), "expected_runs": 60, "completed_runs": succeeded,
              "runs": list(progress.values()), "interrupted_parent_attempts": preserved_partial}
    atomic_json(ARCHIVE / "grid_status.json", status)
    print("Recovery grid", status["status"], f"{succeeded}/60", flush=True)
    return 0 if status["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
