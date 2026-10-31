"""Coordinator action: create exact-byte v2.1 locks and deterministic dirty-only splits."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cric_ed.benchmark import ENTITY_KEYS
from cric_ed.conditional import folds_and_bases
from cric_ed.v2_contract import REQUIRED_FREEZE_FILES, TABLES, SEEDS, PREREG, verify_environment, verify_local_inputs, verify_freeze


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    freeze = ROOT / "prereg/PREREGISTRATION_V2_1.freeze.json"
    legacy = ROOT / "prereg/PREREGISTRATION_V2_1.sha256"
    split = ROOT / "prereg/v2_1_split_manifest.json"
    if any(p.exists() for p in (freeze, legacy, split)):
        raise FileExistsError("Do not overwrite a freeze or split manifest")
    versions = verify_environment(ROOT)
    records = {}
    import numpy as np
    for table in TABLES:
        verify_local_inputs(ROOT, table)
        frame = pd.read_csv(ROOT / f"data/raw/raha/{table}/dirty.csv", dtype=str, keep_default_na=False)
        eligible = [c for c in frame if not (c.lower() in {"id", "index", "tuple_id"} and frame[c].nunique() == len(frame))]
        ids = np.arange(len(frame)) if len(frame) <= 1000 else np.sort(np.random.default_rng(0).choice(len(frame), 1000, replace=False))
        capped = frame.iloc[ids]
        groups = pd.factorize(capped[ENTITY_KEYS[table]].values)[0] if table in ENTITY_KEYS else None
        seeds = {}
        for seed in SEEDS:
            value = {}
            for boundary, keys in (("row", None), ("observed_key_leo", groups)):
                if boundary == "observed_key_leo" and keys is None:
                    continue
                folds, bases = folds_and_bases(len(ids), 5, 512, seed, groups=keys)
                value[boundary] = [{"query": q.tolist(), "base": b.tolist()} for q, b in zip(folds, bases)]
            seeds[str(seed)] = value
        records[table] = {"source_row_ids": ids.tolist(), "eligible_columns": eligible,
                          "observed_key": ENTITY_KEYS.get(table), "seeds": seeds}
    split.write_text(json.dumps({"scope": "Dirty-only fixed rows and outer folds/bases; row splits shared across conditions; LEO real only",
                                 "tables": records}, indent=1) + "\n", encoding="utf-8")
    extras = ("prereg/v2_1_split_manifest.json", "tools/audit_v2_artifacts.py", "experiments/tfm/run_grid_v2_1.py",
              ".gitattributes", "experiments/validation/tfm_environment_provenance_20261030.json")
    files = {name: sha(ROOT / name) for name in REQUIRED_FREEZE_FILES + extras}
    timestamp = datetime.now(timezone.utc).isoformat()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    freeze.write_text(json.dumps({"schema_version": 1, "frozen_utc": timestamp, "source_revision": head,
                                 "working_tree": "Uncommitted integration; exact file identities below are authoritative",
                                 "authorization": "Accepted Path A and v2.1 decisions; Claude checkpoint 0aff63e; local CPU $0",
                                 "runtime_versions": versions, "files_sha256": files}, indent=2) + "\n", encoding="utf-8")
    legacy.write_text(files[PREREG] + "  PREREGISTRATION_V2_1.md\n", encoding="utf-8")
    identity = verify_freeze(ROOT)
    with (ROOT / "docs/EXPERIMENT_LOG.md").open("a", encoding="utf-8", newline="\n") as log:
        log.write(f"\n## V2.1 prospective freeze - {timestamp}\n\nSource HEAD `{head}` + exact uncommitted file map in `{freeze.relative_to(ROOT).as_posix()}`.\n")
        log.write(f"Protocol SHA256 `{identity['prereg_sha256']}`; full snapshot `{identity['source_snapshot_sha256']}`.\n")
        log.write("Dirty-only split manifest fixed before confirmatory detection; accepted row/LEO/descriptive/compute decisions apply.\n")
        log.write("Scope: 60 complete units, both models, local CPU $0. No outcome-based amendment or automatic pivot. Analysis and artifact audit remain required.\n")
    print(json.dumps({"frozen_utc": timestamp, **identity}, indent=2))


if __name__ == "__main__":
    main()
