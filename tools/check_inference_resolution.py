"""Enumerate a design limitation; no benchmark inputs or scientific outcomes.

Under independent, equiprobable null signs, an all-positive signed-rank statistic
has one maximal assignment. Conditions sharing a table must flip together if the
table is the independent unit. This is not a proof that sign-flipping is valid
for any particular benchmark sampling design.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
from pathlib import Path


def resolution(n_tables=4, conditions_per_table=3):
    if (type(n_tables) is not int or type(conditions_per_table) is not int or
            min(n_tables, conditions_per_table) < 1 or n_tables * conditions_per_table > 20):
        raise ValueError("Positive integer dimensions with at most 20 signs required")
    n = n_tables * conditions_per_table
    ranks = list(range(1, n + 1))
    observed = sum(ranks)
    block_extreme = block_total = 0
    for signs in itertools.product((0, 1), repeat=n_tables):
        statistic = sum(rank * signs[i // conditions_per_table] for i, rank in enumerate(ranks))
        block_total += 1
        block_extreme += statistic >= observed
    naive_extreme = naive_total = 0
    for signs in itertools.product((0, 1), repeat=n):
        statistic = sum(rank * sign for rank, sign in zip(ranks, signs))
        naive_total += 1
        naive_extreme += statistic >= observed
    return {"kind": "mathematical design diagnostic; no benchmark result",
            "assumptions": "independent equiprobable signs at table level; all observed differences positive",
            "config": {"n_tables": n_tables, "conditions_per_table": conditions_per_table,
                       "rank_weights": ranks},
            "table_level": {"assignments": block_total, "extreme": block_extreme,
                            "minimum_one_sided_p": block_extreme / block_total},
            "naive_condition_level": {"assignments": naive_total, "extreme": naive_extreme,
                                      "minimum_one_sided_p": naive_extreme / naive_total}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = {"run_id": "design_resolution_20261030", **resolution(),
              "source_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip(),
              "source_state": "uncommitted working tree; script hash identifies derivation",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "primary_source": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html"}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"artifact": str(args.out), **result["table_level"]}))


if __name__ == "__main__":
    main()
