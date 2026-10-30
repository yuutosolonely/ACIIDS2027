#!/usr/bin/env python3
"""Pilot Experiment Runner (Gate G2 Feasibility & Falsification Verification).

Executes controlled multi-arm evaluation strictly on authorized local CPU:
- Arm 1: Classical Coordinate-Wise Robust Deviance (MAD / Baseline)
- Arm 2: CRIC-ED (No Trimming / Raw Context)
- Arm 3: CRIC-ED (Matched Random Removal)
- Arm 4: CRIC-ED (Influence-Aware Trimming with Rare-Valid Guard)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path
import platform
import time
from cric_ed.loader import load_dirty_benchmark_table, load_ground_truth_errors
from cric_ed.detectors.baseline_classical import RobustCoordinateDevianceDetector
from cric_ed.detectors.cric_scorer import CRICDetector
from cric_ed.evaluation.evaluator import evaluate_cell_scores, paired_bootstrap_delta

def _git_state(repo_root: Path) -> dict:
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_root, capture_output=True, text=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, capture_output=True, text=True).stdout
        return {"commit": head, "dirty_files": len(dirty.splitlines())}
    except OSError:
        return {"commit": None, "dirty_files": None}


def run_pilot(run_id: str = "run_pilot_001"):
    repo_root = Path(__file__).resolve().parent.parent
    run_dir = repo_root / "experiments" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    fixture_dir = repo_root / "data" / "fixtures" / "toy_mixed"
    dirty_path = fixture_dir / "dirty.csv"
    errors_path = fixture_dir / "errors.csv"

    print(f"[{run_id}] Loading fixture from {fixture_dir}...")
    table = load_dirty_benchmark_table(
        dirty_path,
        entity_col="entity_id",
        numeric_cols={"feature_a", "feature_b", "num_target"},
        primary_key_cols={"entity_id"}
    )
    headers, gt_mask = load_ground_truth_errors(errors_path)

    # Rare-valid mask for evaluation: category_c == 'RareDelta'
    rare_valid_mask = []
    cat_c_idx = headers.index("category_c")
    for r in range(table.num_rows):
        row_mask = [False] * table.num_cols
        if table.get_cell(r, cat_c_idx) == "RareDelta":
            row_mask[cat_c_idx] = True
        rare_valid_mask.append(row_mask)

    arms = {
        "arm1_classical_mad": RobustCoordinateDevianceDetector(),
        "arm2_cric_raw_context": CRICDetector(context_size=30, trim_ratio=0.15, trimming_mode="none", seed=42),
        "arm3_cric_matched_random": CRICDetector(context_size=30, trim_ratio=0.15, trimming_mode="matched_random", seed=42),
        "arm4_cric_influence_trimming": CRICDetector(
            context_size=30,
            trim_ratio=0.15,
            trimming_mode="influence",
            seed=42,
            rare_valid_patterns={"category_c": {"RareDelta"}}
        ),
    }

    results = {}
    timings = {}
    all_scores_flat = []

    context_rows = []
    arm_scores_by_row = {}
    for arm_name, detector in arms.items():
        print(f"[{run_id}] Executing {arm_name}...")
        if isinstance(detector, CRICDetector):
            detector.context_log = []
        t0 = time.perf_counter()
        scores = detector.score_table(table)
        elapsed = time.perf_counter() - t0
        timings[arm_name] = {
            "wall_clock_sec": round(elapsed, 4),
            "per_cell_ms": round((elapsed / len(scores)) * 1000.0, 4)
        }

        metrics = evaluate_cell_scores(
            scores,
            gt_mask,
            table.entity_ids,
            table.numeric_col_indices,
            rare_valid_mask=rare_valid_mask
        )
        results[arm_name] = metrics
        by_row = {r: [] for r in range(table.num_rows)}
        for cs in scores:
            if cs.is_eligible:
                by_row[cs.row_idx].append(cs.score)
        arm_scores_by_row[arm_name] = by_row
        for q, j, base, active in getattr(detector, "context_log", None) or []:
            context_rows.append([arm_name, q, j, " ".join(map(str, base)), " ".join(map(str, active))])

        for cs in scores:
            if cs.is_eligible:
                all_scores_flat.append([
                    arm_name, cs.row_idx, cs.col_idx, cs.col_name, cs.raw_value,
                    round(cs.score, 4), gt_mask[cs.row_idx][cs.col_idx]
                ])

    # Paired AUPRC differences on identical resampled cells (entity-cluster bootstrap)
    labels_by_row = {r: [] for r in range(table.num_rows)}
    for r in range(table.num_rows):
        for j in range(table.num_cols):
            if j not in table.primary_key_col_indices:
                labels_by_row[r].append(gt_mask[r][j])
    entity_to_rows = {}
    for r, e in enumerate(table.entity_ids):
        entity_to_rows.setdefault(e, []).append(r)
    paired = {}
    for a, b in [("arm4_cric_influence_trimming", "arm3_cric_matched_random"),
                 ("arm4_cric_influence_trimming", "arm2_cric_raw_context"),
                 ("arm2_cric_raw_context", "arm1_classical_mad")]:
        paired[f"{a} - {b}"] = paired_bootstrap_delta(
            arm_scores_by_row[a], arm_scores_by_row[b], labels_by_row, entity_to_rows)

    # Save artifacts
    print(f"[{run_id}] Emitting run artifacts to {run_dir}...")

    # 1. Config
    config = {
        "run_id": run_id,
        "dataset": "toy_mixed",
        "num_rows": table.num_rows,
        "num_cols": table.num_cols,
        "eligible_cells": results["arm1_classical_mad"]["eligible_cells"],
        "seeds": [42],
        "arms": list(arms.keys()),
        "data_role": "synthetic software fixture (not a benchmark)",
        "cric_params": {"context_size": 30, "trim_ratio": 0.15, "n_splits": 5, "seed": 42},
        "rare_valid_patterns_arm4": {"category_c": ["RareDelta"]},
        "rare_valid_patterns_source": "fixture-author oracle (not inferred by the detector)",
        "bootstrap_resamples": 1000,
        "bootstrap_unit": "entity (entity_id)",
        "git": _git_state(repo_root),
        "fixture_sha256": hashlib.sha256(dirty_path.read_bytes()).hexdigest(),
        "scorer_sha256": hashlib.sha256((repo_root / "src/cric_ed/detectors/cric_scorer.py").read_bytes()).hexdigest(),
    }
    with open(run_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    # 2. Metrics & Timings
    summary_metrics = {
        "run_id": run_id,
        "timings": timings,
        "metrics": results,
        "paired_deltas": paired
    }
    with open(run_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(summary_metrics, f, indent=2)

    # 3. Raw Predictions CSV
    with open(run_dir / "predictions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["arm", "row_idx", "col_idx", "col_name", "raw_value", "score", "ground_truth"])
        writer.writerows(all_scores_flat)

    # 4. Context IDs per query (audit trail for pairing / leakage checks)
    with open(run_dir / "context_ids.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["arm", "row_idx", "col_idx", "base_context", "active_context"])
        writer.writerows(context_rows)

    # 5. System Info
    sys_info = {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python_version": platform.python_version()
    }
    with open(run_dir / "system_info.json", "w", encoding="utf-8") as f:
        json.dump(sys_info, f, indent=2)

    print(f"[{run_id}] Finished successfully. Results summary:")
    for arm_name, m in results.items():
        print(f"  {arm_name}: Overall AUPRC={m['overall_auprc']}, Num AUPRC={m['numeric_auprc']}, Cat AUPRC={m['categorical_auprc']}, Rare-Valid FPR@k05={m['rare_valid_fpr_at_k05']}, Time={timings[arm_name]['wall_clock_sec']}s")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="run_pilot_001")
    run_pilot(ap.parse_args().run_id)
