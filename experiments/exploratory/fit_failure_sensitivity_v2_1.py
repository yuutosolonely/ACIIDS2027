"""Post hoc, exploratory sensitivity of v2.1 contrasts to the hospital/inj-random/s4 fit failures.

Written on 2026-10-31 after the confirmatory results had been inspected. It is NOT part of
the frozen v2.1 analysis and does not replace any preregistered number. It only reads saved
score arrays and failure masks; no model is run and no frozen file is modified.

Variants per contrast (A - B) on one table/condition:
  protocol      : five-seed mean on the full eligible universe (recomputed; must equal frozen analysis)
  drop_failed   : seeds without TabPFN failures unchanged; failed seeds evaluated only on cells
                  where neither arm has a failure mask (a different, label-free cell subset)
  exclude_seed  : mean over seeds with no TabPFN failure in either arm
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
RUNS = REPO / "experiments" / "runs" / "v2_1"
FROZEN = REPO / "experiments" / "archive" / "v2_1_analysis" / "seed_metrics.csv"
sys.path.insert(0, str(REPO / "experiments" / "tfm"))
from analyze_v2 import ap_fast  # noqa: E402  (frozen AP implementation, tie-grouped)

CONTRASTS = {
    "tfm_purify_minus_random": ("tabpfn-v2__purify", "tabpfn-v2__random"),
    "tfm_oracle_minus_raw": ("tabpfn-v2__oracle", "tabpfn-v2__raw"),
    "tfm_minus_lgbm_raw": ("tabpfn-v2__raw", "lgbm__raw"),
    "lgbm_purify_minus_random": ("lgbm__purify", "lgbm__random"),
}
TABLES = ("hospital", "flights", "beers", "rayyan")


def mask(z, key):
    k = key + "__nan_cells"
    return z[k] if k in z.files else np.zeros(z["errors"].shape, dtype=bool)


def main(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    frozen = {}
    with FROZEN.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["metric"] == "auprc":
                frozen[(r["table"], r["condition"], int(r["seed"]), r["method"])] = float(r["value"])
    rows, checks, failed_units = [], [], []
    for table in TABLES:
        cond = "inj-random"
        per = {name: {"protocol": [], "drop_failed": [], "exclude_seed": []} for name in CONTRASTS}
        for seed in range(5):
            d = RUNS / f"{table}__{cond}__s{seed}"
            z = np.load(d / "scores.npz")
            E = z["errors"].astype(bool)
            for name, (a, b) in CONTRASTS.items():
                ma, mb = mask(z, a), mask(z, b)
                ap_a, ap_b = ap_fast(z[a].ravel(), E.ravel()), ap_fast(z[b].ravel(), E.ravel())
                for key, v in ((a, ap_a), (b, ap_b)):
                    checks.append(abs(v - frozen[(table, cond, seed, key)]) < 1e-12)
                per[name]["protocol"].append(ap_a - ap_b)
                failed = ma | mb
                if failed.any():
                    keep = ~failed
                    da = ap_fast(z[a][keep], E[keep]) - ap_fast(z[b][keep], E[keep])
                    per[name]["drop_failed"].append(da)
                    failed_units.append({
                        "unit": d.name, "contrast": name, "failed_cells_union": int(failed.sum()),
                        "failed_cells_A": int(ma.sum()), "failed_cells_B": int(mb.sum()),
                        "errors_in_failed_cells": int(E[failed].sum()),
                        "error_rate_failed_cells": float(E[failed].mean()),
                        "error_rate_kept_cells": float(E[keep].mean()),
                        "kept_cells": int(keep.sum()), "kept_errors": int(E[keep].sum()),
                        "protocol_delta": ap_a - ap_b, "drop_failed_delta": da,
                    })
                else:
                    per[name]["drop_failed"].append(ap_a - ap_b)
                    per[name]["exclude_seed"].append(ap_a - ap_b)
        for name in CONTRASTS:
            for variant, vals in per[name].items():
                rows.append({"table": table, "condition": cond, "contrast": name, "variant": variant,
                             "n_seeds": len(vals), "mean_delta": float(np.mean(vals)),
                             "per_seed": [round(v, 6) for v in vals]})
    result = {
        "status": "EXPLORATORY_POST_HOC",
        "created": "2026-10-31",
        "note": "Not preregistered; written after inspecting confirmatory results. Protocol numbers remain primary.",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "frozen_seed_metrics_sha256": hashlib.sha256(FROZEN.read_bytes()).hexdigest(),
        "protocol_ap_matches_frozen": bool(all(checks)), "ap_checks": len(checks),
        "failed_units": failed_units, "summary": rows,
    }
    (out / "results.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("protocol_ap_matches_frozen", "ap_checks")}))
    for r in rows:
        print(r["table"], r["contrast"], r["variant"], r["n_seeds"], round(r["mean_delta"], 4), r["per_seed"])
    for f in failed_units:
        print(json.dumps(f))


if __name__ == "__main__":
    main(REPO / "experiments" / "exploratory" / "v2_1_fit_failure_sensitivity_20261031")
