"""Read-only verification of saved predictions, context boundaries and evaluation inputs.

This checks actual run artifacts; it neither fits models nor changes research results.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments/tfm"))
from cric_ed.benchmark import entity_groups, get_table
from cric_ed.v2_contract import verify_local_inputs
from analyze_v2 import ap_fast, load, methods_of


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit_context(c, n, columns, groups, outer_queries):
    """Check set relationships without reconstructing the scorer's control flow."""
    names = ("query_row_ids", "base_row_ids", "active_row_ids",
             "removed_row_ids", "preprocessing_row_ids")
    sets = {}
    for name in names:
        ids = c[name]
        require(len(ids) == len(set(ids)), "Duplicate IDs: " + name)
        require(all(type(i) is int and 0 <= i < n for i in ids), "Invalid IDs: " + name)
        sets[name] = set(ids)
    Q, B, A, R, P = (sets[name] for name in names)
    require(c["column"] in columns and Q and B, "Invalid target or empty query/base")
    require(not Q & B, "Query entered base context")
    require(len(B) <= 512, "Base context exceeded cap")
    require((Q | A | B) <= P, "Context/query outside encoder universe")
    if c["arm"] == "leaky":
        require(c["stage"] == "final" and A == B | Q and not R, "Invalid leakage diagnostic")
    else:
        require(not Q & A, "Query entered fitted context")
        require(A == B - R and R <= B, "Removal/context identities disagree")
    if c["arm"] in {"random", "purify"}:
        require(len(R) == round(0.15 * len(B)), "Incorrect removal count")
    else:
        require(not R, "Unexpected removal outside intervention")
    if c["stage"] == "pass1":
        outer = outer_queries[c["model"], c["outer_fold"]]
        require(P == set(range(n)) - outer, "Pass-1 encoder crossed outer boundary")
        require(not (Q | A | B) & outer, "Outer query entered nested pass")
        require(c["arm"] == "raw", "Unexpected nested arm")
    else:
        require(c["stage"] == "final" and P == set(range(n)), "Wrong declared transductive encoder")
    if c["arm"] == "raw_leo":
        require(groups is not None, "LEO without declared key")
        require(not set(groups[list(Q)]) & set(groups[list(A)]), "Entity crossed LEO context")
    return Q, B, A, R


def audit_run(meta, arrays, directory):
    verify_local_inputs(ROOT, meta["table"])
    table = get_table(meta["table"], meta["condition"], meta["seed"])
    require(table.eligible == meta["eligible_columns"], "Eligibility differs from pinned input")
    require(table.meta.get("row_ids", list(range(len(table.dirty)))) == meta["row_ids"], "Row IDs differ")
    require(np.array_equal(table.errors, arrays["errors"]), "Saved error mask differs from pinned input")
    require(np.array_equal(table.clean[table.eligible].values.astype(str), arrays["clean_values"]),
            "Saved truth differs from pinned input")
    groups = entity_groups(table)
    contexts = [json.loads(line) for line in (directory / "contexts.jsonl").read_text().splitlines()]
    n, columns = meta["rows"], meta["eligible_columns"]
    outer = {(c["model"], c["fold"]): set(c["query_row_ids"]) for c in contexts
             if c["stage"] == "final" and c["arm"] == "raw" and c["column"] == columns[0]}
    require(len(outer) == 10, "Missing outer folds for both models")
    for model in meta["models"]:
        queries = [outer[model, f] for f in range(5)]
        require(sum(map(len, queries)) == n and set.union(*queries) == set(range(n)), "Outer query partition")
    records = {}
    for c in contexts:
        require(c["seed"] == meta["seed"], "Context seed mismatch")
        Q, B, A, R = audit_context(c, n, columns, groups, outer)
        key = (c["model"], c["stage"], c["outer_fold"], c["arm"], c["fold"], c["column"])
        require(key not in records, "Duplicate context record")
        records[key] = (Q, B, A, R)
    expected_arms = {"raw", "random", "purify", "oracle"}
    if meta["condition"] == "real":
        expected_arms.add("leaky")
        if groups is not None:
            expected_arms.add("raw_leo")
    for model in meta["models"]:
        for arm in expected_arms:
            for col in columns:
                qsets = []
                for fold in range(5):
                    key = (model, "final", None, arm, fold, col)
                    require(key in records, "Missing final context: " + str(key))
                    qsets.append(records[key][0])
                    if arm != "raw_leo":
                        raw_key = (model, "final", None, "raw", fold, col)
                        require(records[key][:2] == records[raw_key][:2], "Unpaired base/query")
                        other = next(m for m in meta["models"] if m != model)
                        require(records[key][:2] == records[(other, "final", None, arm, fold, col)][:2],
                                "Models used different base/query")
                require(sum(map(len, qsets)) == n and set.union(*qsets) == set(range(n)), "Final partition")
        for fold in range(5):
            for col in columns:
                qsets = []
                for inner_fold in range(5):
                    key = (model, "pass1", fold, "raw", inner_fold, col)
                    require(key in records, "Missing nested context")
                    qsets.append(records[key][0])
                pool = set(range(n)) - outer[model, fold]
                require(sum(map(len, qsets)) == len(pool) and set.union(*qsets) == pool, "Nested partition")
    expected_count = len(meta["models"]) * len(columns) * (5 * len(expected_arms) + 25)
    require(len(contexts) == expected_count, "Unexpected context count")
    for method in methods_of(arrays):
        scores, y = arrays[method].ravel(), arrays["errors"].ravel().astype(bool)
        require(abs(ap_fast(scores, y) - average_precision_score(y, scores)) < 1e-12,
                "AP disagrees with independent sklearn implementation")
    return {"table": meta["table"], "condition": meta["condition"], "seed": meta["seed"],
            "contexts_verified": len(contexts), "fit_failure_events": len(meta["failures"]),
            "final_nonfinite_cells": {k: int(v.sum()) for k, v in arrays.items() if k.endswith("__nan_cells")},
            "errors": int(arrays["errors"].sum()), "cells": meta["cells"],
            "scores_sha256": hashlib.sha256((directory / "scores.npz").read_bytes()).hexdigest()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--runs", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--development", action="store_true")
    args = p.parse_args()
    require(not args.out.exists(), "Refusing to overwrite audit")
    units = load(args.runs, development=args.development)
    reports = []
    for runs in units.values():
        for meta, arrays in runs:
            directory = args.runs / f"{meta['table']}__{meta['condition']}__s{meta['seed']}"
            reports.append(audit_run(meta, arrays, directory))
    result = {"status": "PASS", "scope": "Saved artifact consistency and information-boundary audit; not independent model replication",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "runs": reports}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Verified {len(reports)} runs and {sum(r['contexts_verified'] for r in reports)} contexts")


if __name__ == "__main__":
    main()
