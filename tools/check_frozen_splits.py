"""Additional read-only check against the frozen outer splits and deterministic inner splits.

This does not amend frozen detection or analysis code. Use after complete-grid execution.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cric_ed.conditional import folds_and_bases
from cric_ed.v2_contract import verify_freeze, validate_run_grid


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--runs", type=Path, default=ROOT / "experiments/runs/v2_1")
    p.add_argument("--out", type=Path, default=ROOT / "experiments/archive/v2_1_split_audit.json")
    args = p.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    identity = verify_freeze(ROOT)
    split_path = ROOT / "prereg/v2_1_split_manifest.json"
    split = json.loads(split_path.read_text())["tables"]
    results, identities = [], []
    for directory in sorted(args.runs.glob("*__*__s*")):
        if directory.name.endswith(".partial"):
            raise ValueError("Unresolved partial: " + directory.name)
        meta = json.loads((directory / "meta.json").read_text())
        table, condition, seed = meta["table"], meta["condition"], meta["seed"]
        identities.append((table, condition, seed))
        spec = split[table]
        if meta["source_snapshot_sha256"] != identity["source_snapshot_sha256"]:
            raise ValueError("Source mismatch")
        if meta["row_ids"] != spec["source_row_ids"] or meta["eligible_columns"] != spec["eligible_columns"]:
            raise ValueError("Input/split alignment")
        plans = spec["seeds"][str(seed)]
        inner = {}
        for outer, plan in enumerate(plans["row"]):
            pool = np.setdiff1d(np.arange(meta["rows"]), plan["query"])
            qs, bs = folds_and_bases(len(pool), 5, 512, seed)
            inner[outer] = [{"query": pool[q].tolist(), "base": pool[b].tolist()} for q, b in zip(qs, bs)]
        count = 0
        with (directory / "contexts.jsonl").open() as handle:
            for line in handle:
                context = json.loads(line)
                if context["stage"] == "pass1":
                    plan = inner[context["outer_fold"]][context["fold"]]
                else:
                    key = "observed_key_leo" if context["arm"] == "raw_leo" else "row"
                    plan = plans[key][context["fold"]]
                if context["query_row_ids"] != plan["query"] or context["base_row_ids"] != plan["base"]:
                    raise ValueError("Saved context differs from frozen split: " + directory.name)
                count += 1
        results.append({"run_id": directory.name, "contexts_checked": count})
    validate_run_grid(identities)
    args.out.write_text(json.dumps({"status": "PASS", "source_snapshot_sha256": identity["source_snapshot_sha256"],
        "split_sha256": hashlib.sha256(split_path.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "runs": results}, indent=2) + "\n")
    print("Frozen outer/inner split audit PASS:", len(results), "runs")


if __name__ == "__main__":
    main()
