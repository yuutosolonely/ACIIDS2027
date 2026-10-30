"""Candidate analysis for preregistration v2. Reads experiments/runs/v2/*/ and writes
experiments/archive/v2_analysis/ (results.json, CSV/LaTeX tables, figures).

Every number in the paper must come from the files this script writes.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from cric_ed.v2_contract import (  # noqa: E402
    BASELINES, CONDITIONS, MODELS, TABLES,
    checkpoint_hashes, validate_run_grid, validate_run_metadata, verify_freeze,
)
ARMS = ("raw", "random", "purify", "oracle", "leaky")
B = 1000


def ap_fast(scores: np.ndarray, y: np.ndarray) -> float:
    """Average precision with ties grouped (equal to sklearn's average_precision_score)."""
    pos = y.sum()
    if pos == 0:
        return float("nan")
    order = np.argsort(-scores, kind="stable")
    s, t = scores[order], y[order]
    last = np.r_[np.flatnonzero(np.diff(s)), len(s) - 1]
    tp = np.cumsum(t)[last]
    n = last + 1
    dtp = np.diff(np.r_[0, tp])
    return float(np.sum((tp / n) * (dtp / pos)))


def topk_mask(scores, k):
    m = np.zeros(scores.size, dtype=bool)
    m[np.argsort(-scores.ravel(), kind="stable")[:k]] = True
    return m.reshape(scores.shape)


def rare_valid(clean_vals, errors, max_share=0.01, max_unique=0.5):
    n, d = clean_vals.shape
    m = np.zeros((n, d), dtype=bool)
    for j in range(d):
        vals, inv, cnt = np.unique(clean_vals[:, j], return_inverse=True, return_counts=True)
        if len(vals) > max_unique * n:
            continue
        m[:, j] = cnt[inv] / n <= max_share
    return m & ~errors


def validate_arrays(meta, arrs):
    """Check a complete eligible universe and every declared method before analysis."""
    n, cols = meta.get("rows"), meta.get("eligible_columns", [])
    if type(n) is not int or n < 1 or not cols or len(cols) != len(set(cols)):
        raise ValueError("Invalid eligible universe")
    shape = (n, len(cols))
    if meta.get("cells") != n * len(cols):
        raise ValueError("Cell denominator differs from eligible universe")
    row_ids = meta.get("row_ids", [])
    if len(row_ids) != n or any(type(r) is not int for r in row_ids) or len(set(row_ids)) != n:
        raise ValueError("Aligned unique row IDs are required")
    specs = meta.get("column_specs", [])
    if [s.get("name") for s in specs] != cols or any(
            s.get("kind") not in {"numeric", "categorical", "unsupported"} for s in specs):
        raise ValueError("Column specifications differ from eligible columns")
    for key in ("errors", "clean_values"):
        if key not in arrs or arrs[key].shape != shape:
            raise ValueError("Missing or misaligned " + key)
    E = arrs["errors"]
    if not np.isin(E, [0, 1]).all() or int(E.sum()) != meta.get("errors") or not E.any():
        raise ValueError("Binary error mask with positive count matching metadata required")
    required = [f"baseline__{b}" for b in BASELINES]
    arms = ("raw", "random", "purify", "oracle") + (("leaky",) if meta["condition"] == "real" else ())
    required += [f"{m}__{a}" for m in MODELS for a in arms]
    for key in required:
        if key not in arrs or arrs[key].shape != shape or not np.isfinite(arrs[key]).all():
            raise ValueError("Missing, misaligned or nonfinite scores: " + key)
        if key.split("__")[0] in MODELS:
            mask = arrs.get(key + "__nan_cells")
            if mask is None or mask.shape != shape or mask.dtype != np.bool_:
                raise ValueError("Missing or invalid failure mask: " + key)


def load(run_root: Path, expected=None):
    if expected is None:
        expected = {**verify_freeze(REPO), "checkpoint_sha256": checkpoint_hashes(REPO)}
    units = defaultdict(list)
    identities = []
    for d in sorted(run_root.glob("*__*__s*")):
        if d.name.endswith(".partial"):
            raise ValueError("Unresolved partial run: " + d.name)
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        table, condition, seed = validate_run_metadata(meta, expected)
        attempt = json.loads((d / "attempt.json").read_text(encoding="utf-8"))
        if attempt.get("status") != "completed" or any(
                attempt.get("request", {}).get(key) != meta.get(key)
                for key in ("table", "condition", "seed", "source_snapshot_sha256", "code_sha256")):
            raise ValueError("Attempt status or identity does not match completed run")
        if d.name != f"{table}__{condition}__s{seed}":
            raise ValueError("Run directory does not match its metadata: " + d.name)
        with np.load(d / "scores.npz", allow_pickle=False) as z:
            arrs = {k: z[k] for k in z.files}
        validate_arrays(meta, arrs)
        units[(table, condition)].append((meta, arrs))
        identities.append((table, condition, seed))
    validate_run_grid(identities)
    for runs in units.values():
        runs.sort(key=lambda r: r[0]["seed"])
        ref_meta, ref_arrs = runs[0]
        for meta, arrs in runs[1:]:
            if (meta["row_ids"] != ref_meta["row_ids"] or
                    meta["eligible_columns"] != ref_meta["eligible_columns"] or
                    not np.array_equal(arrs["clean_values"], ref_arrs["clean_values"])):
                raise ValueError("Row or column alignment differs across seeds")
    return units


def methods_of(arrs):
    out = [f"baseline__{b}" for b in BASELINES if f"baseline__{b}" in arrs]
    out += [f"{m}__{a}" for m in MODELS for a in ARMS if f"{m}__{a}" in arrs]
    return out


def unit_metrics(runs):
    res = defaultdict(lambda: defaultdict(list))
    for meta, arrs in runs:
        E = arrs["errors"].astype(bool)
        k = int(E.sum())
        rv = rare_valid(arrs["clean_values"], E)
        sup = np.array([s["kind"] != "unsupported" for s in meta["column_specs"]])
        for m in methods_of(arrs):
            S = arrs[m]
            r = res[m]
            r["auprc"].append(ap_fast(S.ravel(), E.ravel()))
            top = topk_mask(S, k)
            r["r_precision"].append(float(E[top].mean()))
            for frac, key in ((0.01, "p_at_1pct"), (0.05, "p_at_5pct")):
                r[key].append(float(E[topk_mask(S, max(1, int(round(frac * S.size))))].mean()))
            r["rare_valid_alarm"].append(float(top[rv].mean()) if rv.any() else float("nan"))
            if m.split("__")[0] in MODELS:
                r["nan_cells"].append(int(arrs.get(m + "__nan_cells", np.zeros(1)).sum()))
            if sup.any() and E[:, sup].any():
                r["auprc_supported_cols"].append(ap_fast(S[:, sup].ravel(), E[:, sup].ravel()))
            if meta["condition"] == "real":
                keep = E.mean(0) <= 0.5
                if E[:, keep].any():
                    r["auprc_nonmajority_cols"].append(ap_fast(S[:, keep].ravel(), E[:, keep].ravel()))
        res["_coverage"]["cells_supported"].append(float(sup.mean()))
        res["_coverage"]["errors_in_supported"].append(float(E[:, sup].sum() / max(E.sum(), 1)))
        res["_coverage"]["error_rate"].append(float(E.mean()))
    return {m: {k: float(np.nanmean(v)) for k, v in d.items()} for m, d in res.items()}


def paired_delta(runs, a, b, seed=2027):
    """Seed-averaged AUPRC(a) - AUPRC(b) with a row-cluster bootstrap shared across seeds."""
    n = runs[0][1]["errors"].shape[0]
    point = np.mean([ap_fast(r[a].ravel(), r["errors"].ravel().astype(bool)) -
                     ap_fast(r[b].ravel(), r["errors"].ravel().astype(bool)) for _, r in runs])
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(B):
        idx = rng.integers(0, n, n)
        ds = []
        for _, r in runs:
            y = r["errors"][idx].ravel().astype(bool)
            if not y.any():
                break  # discard the whole replicate, preserving the fixed seed mean
            ds.append(ap_fast(r[a][idx].ravel(), y) - ap_fast(r[b][idx].ravel(), y))
        if len(ds) == len(runs):
            boots.append(np.mean(ds))
    if not boots:
        raise ValueError("No valid bootstrap replicates for the fixed seed mean")
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"delta": float(point), "ci95": [float(lo), float(hi)], "valid": len(boots)}


def decide(deltas):
    if len(deltas) != len(TABLES) * len(CONDITIONS):
        raise ValueError("Hypothesis verdict requires all declared dataset-condition units")
    d = np.array([x["delta"] for x in deltas])
    if not np.isfinite(d).all() or any(len(x["ci95"]) != 2 or not np.isfinite(x["ci95"]).all()
                                     for x in deltas):
        raise ValueError("Hypothesis inputs must be finite paired estimates")
    pos_ci = sum(1 for x in deltas if x["ci95"][0] > 0)
    p = float(wilcoxon(d, alternative="greater").pvalue) if np.any(d != 0) else 1.0
    supported = p < 0.05 and pos_ci >= 8
    verdict = "supported" if supported else ("reversed" if np.median(d) < 0 else "not supported")
    return {"n_units": len(deltas), "median_delta": float(np.median(d)), "mean_delta": float(d.mean()),
            "units_ci_above_0": pos_ci, "wilcoxon_p_one_sided": p, "verdict": verdict}


def holm(pvals: dict):
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    out, m, running = {}, len(items), 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default=str(REPO / "experiments/runs/v2"))
    ap.add_argument("--out", default=str(REPO / "experiments/archive/v2_analysis"))
    a = ap.parse_args()
    out = Path(a.out)
    units = load(Path(a.runs))
    if out.exists():
        raise ValueError("Refusing to overwrite an existing analysis directory")
    keys = [(t, c) for t in TABLES for c in CONDITIONS]
    result = {"units": {}, "hypotheses": {}, "seeds_per_unit": {f"{t}|{c}": len(units[(t, c)]) for t, c in keys}}
    comparisons = {
        "H1_tfm_minus_lgbm": ("tabpfn-v2__raw", "lgbm__raw"),
        "H2a_oracle_minus_raw": ("tabpfn-v2__oracle", "tabpfn-v2__raw"),
        "H3_purify_minus_random": ("tabpfn-v2__purify", "tabpfn-v2__random"),
        "S_purify_minus_raw": ("tabpfn-v2__purify", "tabpfn-v2__raw"),
        "S_lgbm_purify_minus_random": ("lgbm__purify", "lgbm__random"),
    }
    deltas = defaultdict(list)
    for t, c in keys:
        runs = units[(t, c)]
        u = {"metrics": unit_metrics(runs), "paired": {}}
        for name, (x, y) in comparisons.items():
            if x in runs[0][1] and y in runs[0][1]:
                d = paired_delta(runs, x, y)
                u["paired"][name] = d
                deltas[name].append(d)
        result["units"][f"{t}|{c}"] = u
        print(f"{t}|{c}: " + ", ".join(f"{k}={v['delta']:+.3f}" for k, v in u["paired"].items()), flush=True)
    for name in ("H1_tfm_minus_lgbm", "H2a_oracle_minus_raw", "H3_purify_minus_random"):
        if deltas[name]:
            result["hypotheses"][name] = decide(deltas[name])
    if result["hypotheses"]:
        adj = holm({k: v["wilcoxon_p_one_sided"] for k, v in result["hypotheses"].items()})
        for k, v in adj.items():
            result["hypotheses"][k]["holm_p"] = v
    gaps = {}
    for t in TABLES:
        g = {c: result["units"].get(f"{t}|{c}", {}).get("paired", {}).get("H2a_oracle_minus_raw", {}).get("delta")
             for c in ("inj-random", "inj-systematic")}
        if None not in g.values():
            gaps[t] = {"gap_random": g["inj-random"], "gap_systematic": g["inj-systematic"],
                       "systematic_minus_random": g["inj-systematic"] - g["inj-random"]}
    result["H2b_descriptive"] = gaps
    out.mkdir(parents=True, exist_ok=False)  # create output only after validation/analysis
    (out / "results.json").write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    write_tables(result, out)
    write_figures(result, out)


def write_tables(result, out: Path):
    show = ["baseline__VF", "baseline__PF", "baseline__RobustZ", "baseline__ColumnIF", "baseline__DDCcore",
            "lgbm__raw", "tabpfn-v2__raw", "tabpfn-v2__random", "tabpfn-v2__purify", "tabpfn-v2__oracle"]
    rows = ["unit," + ",".join(show) + ",error_rate,cells_supported,errors_in_supported"]
    for u, v in result["units"].items():
        m = v["metrics"]
        rows.append(u + "," + ",".join(f"{m.get(s, {}).get('auprc', float('nan')):.4f}" for s in show) + "," +
                    ",".join(f"{m['_coverage'][k]:.4f}" for k in ("error_rate", "cells_supported", "errors_in_supported")))
    (out / "auprc_table.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    rows = ["unit,comparison,delta,ci_lo,ci_hi"]
    for u, v in result["units"].items():
        for k, d in v["paired"].items():
            rows.append(f"{u},{k},{d['delta']:.4f},{d['ci95'][0]:.4f},{d['ci95'][1]:.4f}")
    (out / "paired_deltas.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_figures(result, out: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    names = [("H3_purify_minus_random", "purify − random"), ("S_purify_minus_raw", "purify − raw"),
             ("H1_tfm_minus_lgbm", "TabPFN − LGBM"), ("H2a_oracle_minus_raw", "oracle − raw")]
    units = list(result["units"].keys())
    fig, axes = plt.subplots(1, len(names), figsize=(12, 0.32 * len(units) + 1.2), sharey=True)
    for ax, (k, lab) in zip(axes, names):
        for i, u in enumerate(units):
            d = result["units"][u]["paired"].get(k)
            if d:
                ax.errorbar(d["delta"], i, xerr=[[d["delta"] - d["ci95"][0]], [d["ci95"][1] - d["delta"]]],
                            fmt="o", color="#1f4e79", ms=3, capsize=2, lw=1)
        ax.axvline(0, color="#999", lw=0.8)
        ax.set_title(lab, fontsize=9)
        ax.tick_params(labelsize=7)
    axes[0].set_yticks(range(len(units)))
    axes[0].set_yticklabels(units, fontsize=7)
    axes[0].invert_yaxis()
    fig.supxlabel("Δ AUPRC (seed mean, 95% row-bootstrap CI)", fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "paired_deltas.pdf")
    fig.savefig(out / "paired_deltas.png", dpi=150)


if __name__ == "__main__":
    main()
