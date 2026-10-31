"""Compare saved arrays from an original frozen run and a separate verification rerun."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--replica", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    a, b = [json.loads((path / "meta.json").read_text()) for path in (args.original, args.replica)]
    keys = ("table", "condition", "seed", "models", "params", "code_sha256", "checkpoint_sha256",
            "prereg_sha256", "source_snapshot_sha256", "runtime_versions", "row_ids", "eligible_columns")
    for key in keys:
        if a[key] != b[key]:
            raise ValueError("Replication configuration mismatch: " + key)
    checks = {}
    with np.load(args.original / "scores.npz", allow_pickle=False) as first, np.load(args.replica / "scores.npz", allow_pickle=False) as second:
        if set(first.files) != set(second.files):
            raise ValueError("Array set mismatch")
        for key in first.files:
            x, y = first[key], second[key]
            numeric = np.issubdtype(x.dtype, np.number)
            checks[key] = {"exact_equal": bool(np.array_equal(x, y)),
                           "max_abs_difference": float(np.max(np.abs(x - y))) if numeric else None,
                           "allclose_1e_8": bool(np.allclose(x, y, atol=1e-8, rtol=0)) if numeric else bool(np.array_equal(x, y))}
    exact = all(c["exact_equal"] for c in checks.values())
    hashes = {label: {name: hashlib.sha256((path / name).read_bytes()).hexdigest()
                      for name in ("scores.npz", "contexts.jsonl", "meta.json", "attempt.json")}
              for label, path in (("original", args.original), ("replica", args.replica))}
    contexts_equal = hashes["original"]["contexts.jsonl"] == hashes["replica"]["contexts.jsonl"]
    record = {"status": "PASS_EXACT" if exact and contexts_equal else "DIFFERENCES_REQUIRE_REVIEW",
              "scope": "One frozen unit rerun; not independent implementation or all-grid replication",
              "arrays": checks, "contexts_exact_equal": contexts_equal, "artifacts_sha256": hashes,
              "source_snapshot_sha256": a["source_snapshot_sha256"], "params": a["params"],
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "timings_excluded_from_equality": True}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2) + "\n")
    print(record["status"], "exact arrays:", exact, "exact contexts:", contexts_equal)
    if record["status"] != "PASS_EXACT":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
