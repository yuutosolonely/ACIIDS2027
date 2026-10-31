"""Per-source-table descriptive analysis for v2.1; no cross-dataset verdict."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from cric_ed.v2_contract import (  # noqa: E402
    BASELINES, CONDITIONS, MODELS, TABLES, SOURCE_FILES, sha256,
    checkpoint_hashes, validate_run_grid, validate_run_metadata, verify_freeze,
)
from cric_ed.benchmark import DEVELOPMENT, ENTITY_KEYS  # noqa: E402
ARMS = ("raw", "random", "purify", "oracle", "leaky", "raw_leo")
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
    if meta["condition"] == "real" and meta.get("table") in ENTITY_KEYS:
        arms += ("raw_leo",)
    required += [f"{m}__{a}" for m in MODELS for a in arms]
    for key in required:
        if key not in arrs or arrs[key].shape != shape or not np.isfinite(arrs[key]).all():
            raise ValueError("Missing, misaligned or nonfinite scores: " + key)
        if key.split("__")[0] in MODELS:
            mask = arrs.get(key + "__nan_cells")
            if mask is None or mask.shape != shape or mask.dtype != np.bool_:
                raise ValueError("Missing or invalid failure mask: " + key)


def load(run_root: Path, expected=None, development=False):
    if expected is None:
        expected = ({"code_sha256": {p: sha256(REPO / p) for p in SOURCE_FILES}}
                    if development else verify_freeze(REPO))
        expected = {**expected, "checkpoint_sha256": checkpoint_hashes(REPO)}
    units = defaultdict(list)
    identities = []
    for d in sorted(run_root.glob("*__*__s*")):
        if d.name.endswith(".partial"):
            raise ValueError("Unresolved partial run: " + d.name)
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        if development:
            table, condition, seed = validate_development_metadata(meta, expected)
        else:
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
    if development:
        if len(identities) != len(set(identities)) or not identities:
            raise ValueError("Empty or duplicate development runs")
        seeds = {s for _, _, s in identities}
        if set(identities) != {(DEVELOPMENT[0], c, s) for c in CONDITIONS for s in seeds}:
            raise ValueError("Development analysis requires all conditions and the same seeds")
    else:
        validate_run_grid(identities)
    for runs in units.values():
        runs.sort(key=lambda r: r[0]["seed"])
        ref_meta, ref_arrs = runs[0]
        for meta, arrs in runs[1:]:
            if (meta["row_ids"] != ref_meta["row_ids"] or
                    meta["eligible_columns"] != ref_meta["eligible_columns"] or
                    not np.array_equal(arrs["clean_values"], ref_arrs["clean_values"])):
                raise ValueError("Row or column alignment differs across seeds")
            if meta["condition"] == "real" and not np.array_equal(arrs["errors"], ref_arrs["errors"]):
                raise ValueError("Real error masks differ across seeds")
    return units


def validate_development_metadata(meta, expected):
    """The explicit development bypass can never admit a confirmatory table."""
    table, condition, seed = (meta.get(k) for k in ("table", "condition", "seed"))
    if (table not in DEVELOPMENT or meta.get("role") != "development" or
            condition not in CONDITIONS or type(seed) is not int):
        raise ValueError("Development mode accepts movies_1 development artifacts only")
    if meta.get("status") != "completed" or not isinstance(meta.get("failures"), list):
        raise ValueError("Completed status and explicit failure list required")
    models = meta.get("models", [])
    if len(models) != len(MODELS) or set(models) != set(MODELS):
        raise ValueError("Both declared models are required exactly once")
    for key in ("code_sha256", "checkpoint_sha256"):
        if key not in expected or meta.get(key) != expected[key]:
            raise ValueError("Development run differs from current " + key)
    return table, condition, seed


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
            method_sup = (np.array([s["kind"] == "numeric" for s in meta["column_specs"]])
                          if m in {"baseline__RobustZ", "baseline__DDCcore"} else
                          sup if m.split("__")[0] in MODELS else np.ones(E.shape[1], dtype=bool))
            r["supported_cells"].append(int(E.shape[0] * method_sup.sum()))
            r["supported_errors"].append(int(E[:, method_sup].sum()))
            r["rare_valid_cells"].append(int(rv.sum()))
            r["auprc"].append(ap_fast(S.ravel(), E.ravel()))
            for kind in ("numeric", "categorical"):
                selected = np.array([spec["kind"] == kind for spec in meta["column_specs"]])
                if selected.any():
                    r["auprc_" + kind].append(ap_fast(S[:, selected].ravel(), E[:, selected].ravel()))
            top = topk_mask(S, k)
            r["r_precision"].append(float(E[top].mean()))
            for frac, key in ((0.01, "p_at_1pct"), (0.05, "p_at_5pct")):
                r[key].append(float(E[topk_mask(S, max(1, int(round(frac * S.size))))].mean()))
            r["rare_valid_alarm"].append(float(top[rv].mean()) if rv.any() else float("nan"))
            if m.split("__")[0] in MODELS:
                r["nan_cells"].append(int(arrs.get(m + "__nan_cells", np.zeros(1)).sum()))
            if method_sup.any() and E[:, method_sup].any():
                r["auprc_supported_cols"].append(ap_fast(S[:, method_sup].ravel(), E[:, method_sup].ravel()))
            if meta["condition"] == "real":
                keep = E.mean(0) <= 0.5
                if E[:, keep].any():
                    r["auprc_nonmajority_cols"].append(ap_fast(S[:, keep].ravel(), E[:, keep].ravel()))
        res["_coverage"]["cells_supported"].append(float(sup.mean()))
        res["_coverage"]["errors_in_supported"].append(float(E[:, sup].sum() / max(E.sum(), 1)))
        res["_coverage"]["error_rate"].append(float(E.mean()))
        res["_coverage"]["cells"].append(int(E.size))
        res["_coverage"]["errors"].append(int(E.sum()))
        res["_coverage"]["rare_valid_cells"].append(int(rv.sum()))
        if meta["condition"] != "real":
            target = round(meta.get("params", {}).get("rate", 0.1) * E.size)
            res["_coverage"]["injection_target"].append(target)
            res["_coverage"]["injection_shortfall"].append(target - int(E.sum()))
    return {m: {k: (float(np.nanmean(v)) if np.isfinite(v).any() else float("nan"))
                for k, v in d.items()} for m, d in res.items()}


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
    return {"delta": float(point), "ci95": [float(lo), float(hi)], "valid": len(boots),
            "attempted": B, "bootstrap_seed": seed}



COMPARISONS = {
    "purify_minus_random": ("tabpfn-v2__purify", "tabpfn-v2__random"),
    "tfm_minus_lgbm_raw": ("tabpfn-v2__raw", "lgbm__raw"),
    "oracle_minus_raw": ("tabpfn-v2__oracle", "tabpfn-v2__raw"),
    "purify_minus_raw": ("tabpfn-v2__purify", "tabpfn-v2__raw"),
    "lgbm_purify_minus_random": ("lgbm__purify", "lgbm__random"),
}


def cost_metrics(runs):
    """Shared work is measured once; matched-budget totals are derived, not additive arms."""
    vals = defaultdict(list)
    for meta, _ in runs:
        timing = meta.get("timing_sec", {})
        for key, value in timing.items():
            if not np.isfinite(value) or value < 0:
                raise ValueError("Invalid nonnegative finite timing: " + key)
            vals[key].append(float(value))
        if "wall_clock_sec" in meta:
            vals["wall_clock_sec"].append(meta["wall_clock_sec"])
        for model in MODELS:
            nested = timing.get(model + "__pass1_nested")
            purify = timing.get(model + "__purify")
            random = timing.get(model + "__random")
            if None not in (nested, purify, random):
                if nested > purify + 0.002:  # serialization rounding only
                    raise ValueError("Nested cost exceeds inclusive purification time")
                vals[model + "__purify_final"].append(max(0.0, purify - nested))
                vals[model + "__random_matched_total"].append(random + nested)
    return {key: float(np.mean(values)) for key, values in vals.items()}


def analyze(units, development=False):
    result = {
        "role": "development" if development else "confirmatory",
        "reporting": "per-source-table descriptive; no cross-dataset superiority verdict",
        "uncertainty": "95% percentile row bootstrap; same rows across arms and seeds; fixed seed mean",
        "uncertainty_scope": "Conditional on these source tables and context seeds; assumes independent rows. "
                             "Repeated entities can invalidate row-bootstrap coverage; LEO does not fix this.",
        "bootstrap_replicates": B, "units": {}, "macro_descriptive": {}, "provenance": [],
        "cost_accounting": "pass1_nested is included in purify; purify_final subtracts it. "
                           "random_matched_total adds the same shared pass1 cost to random. "
                           "Do not sum these overlapping timing entries.",
    }
    macros = defaultdict(list)
    for (table, condition), runs in sorted(units.items()):
        pairs = dict(COMPARISONS)
        if condition == "real":
            for model in MODELS:
                pairs[model + "_leaky_minus_raw"] = (model + "__leaky", model + "__raw")
        if condition == "real" and table in ENTITY_KEYS:
            for model in MODELS:
                pairs[model + "_raw_leo_minus_raw"] = (model + "__raw_leo", model + "__raw")
        unit = {"seeds": [m["seed"] for m, _ in runs], "metrics": unit_metrics(runs),
                "paired": {}, "cost_seconds_seed_mean": cost_metrics(runs),
                "failures": [{"seed": m["seed"], "events": m["failures"]} for m, _ in runs]}
        unit["seed_metrics"] = [{"seed": meta["seed"], "metrics": unit_metrics([(meta, arrs)])}
                                for meta, arrs in runs]
        unit["metric_defined_seed_counts"] = {
            method: {metric: int(sum(np.isfinite(x["metrics"].get(method, {}).get(metric, float("nan")))
                                      for x in unit["seed_metrics"]))
                     for metric in measures} for method, measures in unit["metrics"].items()}
        for name, (a, b) in pairs.items():
            effect = paired_delta(runs, a, b)
            effect["category"] = (("primary" if condition == "real" else "mechanism_probe")
                                  if name == "purify_minus_random" else "secondary")
            unit["paired"][name] = effect
            macros[(condition, name)].append((table, effect["delta"]))
        result["units"][f"{table}|{condition}"] = unit
        for meta, _ in runs:
            result["provenance"].append({k: meta.get(k) for k in (
                "table", "condition", "seed", "git", "code_sha256", "checkpoint_sha256",
                "prereg_sha256", "source_snapshot_sha256", "runtime_versions", "params")})
    for (condition, name), values in sorted(macros.items()):
        result["macro_descriptive"][f"{condition}|{name}"] = {
            "mean_delta": float(np.mean([v for _, v in values])),
            "tables": [t for t, _ in values], "n_tables": len(values),
            "scope": "Unweighted descriptive mean across named source tables; no macro CI or test",
        }
    result["mechanism_oracle_gap_difference_descriptive"] = {}
    for table in sorted({t for t, _ in units}):
        random_key, systematic_key = table + "|inj-random", table + "|inj-systematic"
        if random_key in result["units"] and systematic_key in result["units"]:
            result["mechanism_oracle_gap_difference_descriptive"][table] = {
                "systematic_minus_random": (result["units"][systematic_key]["paired"]["oracle_minus_raw"]["delta"] -
                                             result["units"][random_key]["paired"]["oracle_minus_raw"]["delta"]),
                "scope": "Derived difference between seed-mean oracle gaps; descriptive, no separate CI or independent-condition test"}
    return result


def _json_safe(value):
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", default=str(REPO / "experiments/runs/v2"))
    parser.add_argument("--out", default=str(REPO / "experiments/archive/v2_1_analysis"))
    parser.add_argument("--development", action="store_true",
                        help="Only movies_1, all three conditions, same seeds; never confirmatory tables")
    args = parser.parse_args()
    out = Path(args.out)
    if out.exists():
        raise ValueError("Refusing to overwrite an existing analysis directory")
    units = load(Path(args.runs), development=args.development)
    result = analyze(units, development=args.development)
    out.mkdir(parents=True, exist_ok=False)
    (out / "results.json").write_text(json.dumps(_json_safe(result), indent=2, allow_nan=False) + "\n",
                                      encoding="utf-8")
    write_tables(result, out)
    write_figures(result, out)
    print(f"Wrote {result['role']} descriptive analysis to {out}", flush=True)


def _write_table(out, name, fields, rows):
    with (out / (name + ".csv")).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(fields)
        writer.writerows(rows)
    def tex(value):
        if isinstance(value, float):
            return f"{value:.6f}" if np.isfinite(value) else "--"
        return str(value).replace("\\", r"\textbackslash{}").replace("_", r"\_").replace("%", r"\%")
    lines = [r"\begin{tabular}{" + "l" * len(fields) + "}", r"\hline",
             " & ".join(map(tex, fields)) + r" \\", r"\hline"]
    lines += [" & ".join(map(tex, row)) + r" \\" for row in rows]
    lines += [r"\hline", r"\end{tabular}"]
    (out / (name + ".tex")).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_tables(result, out):
    metrics, paired, costs, macros, seed_metrics = [], [], [], [], []
    for unit, values in result["units"].items():
        table, condition = unit.split("|")
        for method, measures in values["metrics"].items():
            for metric, value in measures.items():
                metrics.append([table, condition, method, metric, value])
        for name, effect in values["paired"].items():
            paired.append([table, condition, effect["category"], name, effect["delta"],
                           *effect["ci95"], effect["valid"], len(values["seeds"])])
        for component, seconds in values["cost_seconds_seed_mean"].items():
            costs.append([table, condition, component, seconds])
        for seed in values.get("seed_metrics", []):
            for method, measures in seed["metrics"].items():
                for metric, value in measures.items():
                    seed_metrics.append([table, condition, seed["seed"], method, metric, value])
    for key, values in result["macro_descriptive"].items():
        condition, name = key.split("|")
        macros.append([condition, name, values["mean_delta"], values["n_tables"]])
    _write_table(out, "metrics", ["table", "condition", "method", "metric", "seed_mean"], metrics)
    _write_table(out, "seed_metrics", ["table", "condition", "seed", "method", "metric", "value"], seed_metrics)
    _write_table(out, "paired_deltas", ["table", "condition", "category", "comparison", "delta", "ci_lo",
                                       "ci_hi", "bootstrap_valid", "seeds"], paired)
    _write_table(out, "costs", ["table", "condition", "component", "seconds_seed_mean"], costs)
    _write_table(out, "macro_descriptive", ["condition", "comparison", "mean_delta", "tables"], macros)


def write_figures(result, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for category, conditions in (("primary", ("real",)), ("mechanism", CONDITIONS[1:])):
        selected = [(key, val["paired"]["purify_minus_random"])
                    for key, val in result["units"].items() if key.split("|")[1] in conditions]
        fig, ax = plt.subplots(figsize=(7, max(2.5, 0.4 * len(selected) + 1)))
        for i, (_, effect) in enumerate(selected):
            lo, hi = effect["ci95"]
            # A percentile CI need not contain the original point estimate.
            ax.plot([lo, hi], [i, i], color="#1f4e79", lw=1.5)
            ax.plot(effect["delta"], i, "o", color="#1f4e79", ms=4)
        ax.axvline(0, color="#999999", lw=0.8)
        ax.set_yticks(range(len(selected)), [key for key, _ in selected])
        ax.invert_yaxis()
        ax.set_xlabel("TabPFN purify - random AUPRC (seed mean, 95% row-bootstrap CI)")
        ax.set_title(result["role"] + ": " + category + " descriptive effects")
        fig.tight_layout()
        for suffix in ("pdf", "png"):
            fig.savefig(out / f"{category}_deltas.{suffix}", dpi=150)
        plt.close(fig)


if __name__ == "__main__":
    main()
