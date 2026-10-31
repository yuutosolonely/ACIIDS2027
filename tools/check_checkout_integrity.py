"""Check that a checkout of this repository reproduces the recorded evidence bytes.

Added 2026-10-31 as a packaging check after the v2.1 experiments: commit c3ee807 stored
several SHA-256-referenced files with normalized line endings, so a clean checkout failed
the frozen-source check. This script verifies, for any root (working tree or an export of
a commit/tree), that every recorded hash still matches. It reads files only; it never
writes or regenerates a freeze, run, analysis or manuscript artifact.

Usage: python tools/check_checkout_integrity.py [ROOT] [--json OUT]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPLAY_FILES = ("results.json", "metrics.csv", "seed_metrics.csv", "paired_deltas.csv",
                "costs.csv", "macro_descriptive.csv")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(root: Path) -> dict:
    root = root.resolve()
    sys.path.insert(0, str(root / "src"))
    from cric_ed.v2_contract import verify_freeze  # noqa: E402

    results = {}

    def record(name, ok, detail=""):
        results[name] = {"ok": bool(ok), "detail": detail}

    try:
        ident = verify_freeze(root)
        record("v2_1_freeze", True, ident["source_snapshot_sha256"])
    except Exception as exc:  # report, do not raise: every check should be visible
        record("v2_1_freeze", False, str(exc))

    archive, replay = root / "experiments/archive/v2_1_analysis", root / "experiments/validation/v2_1_analysis_reproduction"
    diffs = [f for f in REPLAY_FILES if sha(archive / f) != sha(replay / f)]
    record("analysis_replay_bytes", not diffs, "differs: " + ", ".join(diffs) if diffs else "6/6 identical")

    prov = json.loads((root / "paper/generated/PROVENANCE.json").read_text(encoding="utf-8"))
    bad = [k for k, v in prov["outputs_sha256"].items() if sha(root / "paper/generated" / k) != v]
    if sha(archive / "results.json") != prov["analysis_sha256"]:
        bad.append("analysis results.json")
    if sha(root / "experiments/archive/v2_1_artifact_audit.json") != prov["audit_sha256"]:
        bad.append("artifact audit")
    record("generated_tables_provenance", not bad, "differs: " + ", ".join(bad) if bad else "all match")

    sums = root / "experiments/archive/SHA256SUMS"
    bad = []
    for line in sums.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            if sha(sums.parent / name.lstrip("*")) != digest:
                bad.append(name)
    record("archive_SHA256SUMS", not bad, "differs: " + ", ".join(bad) if bad else "all match")

    split = json.loads((root / "experiments/archive/v2_1_split_audit.json").read_text(encoding="utf-8"))
    ok = sha(root / "prereg/v2_1_split_manifest.json") == split["split_sha256"]
    record("split_manifest_vs_split_audit", ok)

    intake = json.loads((root / "docs/handoffs/COORDINATOR_INTAKE_20261030.json").read_text(encoding="utf-8"))
    recorded = json.dumps(intake)
    ok = sha(root / "prereg/PREREGISTRATION.md") in recorded
    record("prereg_v1_vs_intake_record", ok)

    return {"root": str(root), "all_ok": all(r["ok"] for r in results.values()), "checks": results}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--json", type=Path)
    a = p.parse_args()
    out = check(a.root)
    for name, r in out["checks"].items():
        print(("PASS " if r["ok"] else "FAIL ") + name + (": " + r["detail"] if r["detail"] else ""))
    if a.json:
        a.json.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    return 0 if out["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
