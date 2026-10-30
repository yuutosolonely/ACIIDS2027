"""Runner for preregistration v2.1 (Path A, amended per author decisions 2026-10-30). Writes one artifact directory per
(table, condition, seed) under experiments/runs/v2/ and never overwrites an existing one.

Confirmatory tables require both the protocol hash and a full source freeze manifest.
The candidate's nested purification amendment must be approved before any such freeze.

Usage (isolated env): .venv-tfm/Scripts/python.exe experiments/tfm/run_v2.py --table hospital
    --condition real --seeds 0 1 2 3 4
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
import warnings
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
warnings.filterwarnings("ignore")

from cric_ed.baselines import BASELINES  # noqa: E402
from cric_ed.benchmark import CONFIRMATORY, DEVELOPMENT, entity_groups, get_table  # noqa: E402
from cric_ed.conditional import LGBMModel, RunLog, TabPFNModel, apply_penalty, column_specs, score_table  # noqa: E402
from cric_ed.run_record import run_attempt  # noqa: E402
from cric_ed.v2_contract import (  # noqa: E402
    MODELS, SEEDS, SOURCE_FILES, verify_environment, verify_freeze, verify_local_inputs,
)

CLF = REPO / "checkpoints/TabPFN-v2-clf/tabpfn-v2-classifier.ckpt"
REG = REPO / "checkpoints/TabPFN-v2-reg/tabpfn-v2-regressor.ckpt"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git_state():
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=REPO, capture_output=True, text=True).stdout
    return {"commit": head, "dirty_files": len(dirty.splitlines())}


def check_prereg(table: str):
    if table not in CONFIRMATORY + DEVELOPMENT:
        raise ValueError("Unknown table")
    if table not in CONFIRMATORY:
        return {"role": "development"}
    return {"role": "confirmatory", **verify_freeze(REPO)}


def run(table: str, condition: str, seed: int, models: list[str], out_root: Path):
    run_started = time.perf_counter()
    role = check_prereg(table)
    if condition not in {"real", "inj-random", "inj-systematic"} or type(seed) is not int:
        raise ValueError("Invalid condition or seed")
    if len(set(models)) != len(models) or not models or set(models) - set(MODELS):
        raise ValueError("Unknown, empty or duplicate model list")
    if table in CONFIRMATORY and (seed not in SEEDS or set(models) != set(MODELS)):
        raise ValueError("Confirmatory runs require both declared models and a declared seed")
    out = out_root / f"{table}__{condition}__s{seed}"
    if out.exists():
        raise FileExistsError("Refusing to reuse an existing run: " + str(out))
    request = {"table": table, "condition": condition, "seed": seed, "models": models,
               **role, "git": git_state(), "python": platform.python_version(),
               "code_sha256": {p: sha(REPO / p) for p in SOURCE_FILES}}
    with run_attempt(out, request, required=("scores.npz", "contexts.jsonl", "meta.json")) as attempt:
        attempt.phase("verify_environment")
        runtime_versions = verify_environment(REPO)
        attempt.phase("verify_inputs")
        checkpoint_ids = verify_local_inputs(REPO, table)
        meta = _execute_run(table, condition, seed, models, role, checkpoint_ids,
                            runtime_versions, run_started, attempt)
    print(f"done {out.name} errors={meta['errors']} failures={len(meta['failures'])} "
          f"time={meta['wall_clock_sec']:.0f}s", flush=True)


def _execute_run(table, condition, seed, models, role, checkpoint_ids,
                 runtime_versions, run_started, attempt):
    tmp = attempt.directory
    attempt.phase("load_table")
    t = get_table(table, condition, seed)
    cols, E = t.eligible, t.errors
    arrays = {"errors": E, "clean_values": t.clean[cols].values.astype(str)}
    timing, failures, contexts = {}, [], []
    for name, fn in BASELINES.items():
        attempt.phase("baseline:" + name)
        t0 = time.perf_counter()
        arrays[f"baseline__{name}"] = fn(t.dirty, cols, seed=seed)
        timing[f"baseline__{name}"] = round(time.perf_counter() - t0, 3)
    for mname in models:
        attempt.phase("model_setup:" + mname)
        model = TabPFNModel(CLF, REG, n_estimators=1, seed=seed) if mname == "tabpfn-v2" else LGBMModel(seed)
        log = RunLog()
        attempt.phase("score:" + mname + ":raw")
        raw, specs = score_table(t.dirty, cols, model, "raw", seed, log=log)
        arms = {"raw": raw}
        for arm in ("random", "purify", "oracle") + (("leaky",) if condition == "real" else ()):
            attempt.phase("score:" + mname + ":" + arm)
            arms[arm], _ = score_table(t.dirty, cols, model, arm, seed,
                                       clean=t.clean if arm == "oracle" else None, log=log)
        groups = entity_groups(t)
        if condition == "real" and groups is not None:
            attempt.phase("score:" + mname + ":raw_leo")
            arms["raw_leo"], _ = score_table(t.dirty, cols, model, "raw_leo", seed, log=log, groups=groups)
        for arm, S in arms.items():
            arrays[f"{mname}__{arm}__nan_cells"] = ~np.isfinite(S)
            arrays[f"{mname}__{arm}"] = apply_penalty(S)
        timing.update({f"{mname}__{a}": round(s, 3) for (a, _), s in log.seconds.items()})
        failures += [{"model": mname, **f} for f in log.failures]
        contexts += [{"model": mname, **c} for c in log.contexts]
    attempt.phase("serialize")
    np.savez_compressed(tmp / "scores.npz", **arrays)
    with open(tmp / "contexts.jsonl", "w", encoding="utf-8") as fh:
        for c in contexts:
            fh.write(json.dumps(c) + "\n")
    meta = {
        "status": "completed",
        "table": table, "condition": condition, "seed": seed, "models": models, **role,
        "rows": len(t.dirty), "eligible_columns": cols, "errors": int(E.sum()), "cells": int(E.size),
        "row_ids": t.meta.get("row_ids", list(range(len(t.dirty)))),
        "context_id_space": "subsample row positions; map to source rows using row_ids",
        "column_specs": [s.__dict__ for s in column_specs(t.dirty, cols)],
        "table_meta": t.meta, "timing_sec": timing, "failures": failures,
        "params": {"folds": 5, "context_cap": 512, "q": 0.15, "tabpfn_n_estimators": 1, "rate": 0.10,
                   "entity_key_leo": __import__("cric_ed.benchmark", fromlist=["ENTITY_KEYS"]).ENTITY_KEYS.get(table)},
        "git": git_state(), "python": platform.python_version(),
        "runtime_versions": runtime_versions,
        "code_sha256": {p: sha(REPO / p) for p in SOURCE_FILES},
        "checkpoint_sha256": checkpoint_ids,
        "finished": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "wall_clock_sec": time.perf_counter() - run_started,
    }
    if role["role"] == "confirmatory" and verify_freeze(REPO)["source_snapshot_sha256"] != role["source_snapshot_sha256"]:
        raise ValueError("Frozen source changed during execution; retaining partial run")
    (tmp / "meta.json").write_text(json.dumps(meta, indent=1, default=str) + "\n", encoding="utf-8")
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=True, choices=CONFIRMATORY + DEVELOPMENT)
    ap.add_argument("--condition", default="real", choices=["real", "inj-random", "inj-systematic"])
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    ap.add_argument("--models", nargs="+", default=["lgbm", "tabpfn-v2"])
    ap.add_argument("--out", default=str(REPO / "experiments/runs/v2"))
    a = ap.parse_args()
    if any(m not in ("lgbm", "tabpfn-v2") for m in a.models) or len(set(a.models)) != len(a.models):
        ap.error("Expected distinct models from {lgbm, tabpfn-v2}")
    if len(set(a.seeds)) != len(a.seeds):
        ap.error("Duplicate seeds are not allowed")
    for s in a.seeds:
        run(a.table, a.condition, s, a.models, Path(a.out))


if __name__ == "__main__":
    main()
