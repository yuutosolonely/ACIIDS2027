"""Post-grid verification/reporting after the recorded resume of the v2.1 grid.

Same stage order as tools/finish_v2_1_verification.py (whose run died with the original grid
process tree and whose output directory is retained as evidence). Differences: waits for the
resume status written by tools/resume_grid_v2_1.py and writes to a new directory
experiments/archive/v2_1_postprocess_resume/. No model API, paid compute, agent launch,
publication or submission.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cric_ed.v2_contract import verify_freeze  # noqa: E402

OUT = ROOT / ("experiments/archive/v2_1_postprocess_resume_"
               + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
OUT.mkdir(parents=True, exist_ok=False)
STATE = OUT / "status.json"
ARCHIVE = ROOT / "experiments/archive/v2_1_runs"


def state(stage, status="running", **extra):
    value = {"stage": stage, "status": status, "updated_utc": datetime.now(timezone.utc).isoformat(),
             "pid": os.getpid(), **extra}
    STATE.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    print(value["updated_utc"], status, stage, flush=True)


def run(stage, args):
    state(stage)
    verify_freeze(ROOT)
    env = {**os.environ, "FOR_DISABLE_CONSOLE_CTRL_HANDLER": "1"}
    with (OUT / (stage + ".log")).open("w", encoding="utf-8") as log:
        result = subprocess.run([sys.executable, *args], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if result.returncode:
        raise RuntimeError(f"{stage} exited {result.returncode}; see retained log")


try:
    identity = verify_freeze(ROOT)
    state("wait_for_resumed_grid", source_snapshot_sha256=identity["source_snapshot_sha256"])
    while True:
        statuses = sorted(ARCHIVE.glob("resume_status_*.json"))
        if statuses:
            grid = json.loads(statuses[-1].read_text())
            break
        time.sleep(60)
    if grid["status"] != "completed" or grid["completed_units"] != 60:
        raise ValueError("Resumed grid incomplete; refusing downstream acceptance")
    if list((ROOT / "experiments/runs/v2_1").glob("*.partial")):
        raise ValueError("Unresolved partial in the grid root")
    comparison = json.loads((ROOT / "experiments/validation/v2_1_replication_comparison.json").read_text())
    if comparison["status"] != "PASS_EXACT":
        raise ValueError("Verification rerun requires review")
    run("artifact_audit", ["tools/audit_v2_artifacts.py", "--runs", "experiments/runs/v2_1",
                           "--out", "experiments/archive/v2_1_artifact_audit.json"])
    run("frozen_split_audit", ["tools/check_frozen_splits.py"])
    run("analysis", ["experiments/tfm/analyze_v2.py", "--runs", "experiments/runs/v2_1",
                     "--out", "experiments/archive/v2_1_analysis"])
    run("analysis_reproduction", ["experiments/tfm/analyze_v2.py", "--runs", "experiments/runs/v2_1",
                                  "--out", "experiments/validation/v2_1_analysis_reproduction"])
    state("compare_numerical_analysis")
    first = ROOT / "experiments/archive/v2_1_analysis"
    second = ROOT / "experiments/validation/v2_1_analysis_reproduction"
    names = ["results.json", "metrics.csv", "seed_metrics.csv", "paired_deltas.csv", "costs.csv",
             "macro_descriptive.csv"]
    checks = {n: {"identical": (first / n).read_bytes() == (second / n).read_bytes(),
                  "sha256": hashlib.sha256((first / n).read_bytes()).hexdigest()} for n in names}
    (OUT / "numerical_reproduction.json").write_text(json.dumps(checks, indent=2) + "\n")
    if not all(v["identical"] for v in checks.values()):
        raise ValueError("Repeated numerical analysis differs; do not rewrite outputs")
    run("generate_paper_artifacts", ["tools/generate_paper_results.py"])
    run("prepare_empirical_draft", ["tools/write_empirical_draft.py"])
    run("build_render_draft", ["tools/build_paper.py"])
    run("markdown_companion", ["tools/sync_manuscript.py"])
    run("final_text_screen", ["tools/check_text_overlap.py", "--out",
                              "docs/review/TEXT_OVERLAP_EMPIRICAL_DRAFT_20261030.json"])
    build = json.loads((ROOT / "paper/output/build_provenance.json").read_text())
    state("ready_for_manuscript_review", status="verification_completed_review_pending",
          pages=build["pages"], length_12_to_15=12 <= build["pages"] <= 15)
except BaseException as exc:
    state("failed_or_interrupted", status="failed", error_type=type(exc).__name__, error=str(exc))
    raise
