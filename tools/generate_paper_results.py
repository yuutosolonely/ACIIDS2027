"""Generate manuscript tables directly from frozen complete-grid analysis and inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def esc(s):
    return str(s).replace("_", r"\_").replace("%", r"\%")


def f(value, digits=3):
    return "--" if value is None or not np.isfinite(value) else f"{value:.{digits}f}"


def interval(effect):
    return f"{f(effect['delta'])} [{f(effect['ci95'][0])}, {f(effect['ci95'][1])}]"


def table(out, name, caption, heads, rows, spec=None):
    spec = spec or "l" + "r" * (len(heads) - 1)
    lines = [r"\begin{table}[t]", r"\centering\small", r"\setlength{\tabcolsep}{3.5pt}",
             "\\caption{" + caption + "}", "\\label{tab:" + name + "}",
             "\\begin{tabular}{" + spec + "}", r"\toprule", " & ".join(heads) + r" \\", r"\midrule"]
    lines += [" & ".join(map(str, row)) + r" \\" for row in rows]
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    (out / (name + ".tex")).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--analysis", type=Path, default=ROOT / "experiments/archive/v2_1_analysis")
    p.add_argument("--runs", type=Path, default=ROOT / "experiments/runs/v2_1")
    p.add_argument("--audit", type=Path, default=ROOT / "experiments/archive/v2_1_artifact_audit.json")
    args = p.parse_args()
    data = json.loads((args.analysis / "results.json").read_text())
    audit = json.loads(args.audit.read_text())
    if data["role"] != "confirmatory" or audit["status"] != "PASS" or len(audit["runs"]) != 60:
        raise ValueError("Complete confirmatory analysis and artifact audit required")
    out = ROOT / "paper/generated"
    if out.exists():
        raise FileExistsError("Archive the previous generated snapshot explicitly before regeneration")
    out.mkdir()
    tables = ("hospital", "flights", "beers", "rayyan")
    primary, baselines, coverage, cost, secondary, rare, probes = [], [], [], [], [], [], []
    failures = 0
    for t in tables:
        u = data["units"][t + "|real"]
        metrics, paired = u["metrics"], u["paired"]
        m = lambda method: metrics[method]["auprc"]
        primary.append([t, f(m("tabpfn-v2__raw")), f(m("tabpfn-v2__random")), f(m("tabpfn-v2__purify")), interval(paired["purify_minus_random"])])
        baselines.append([t] + [f(m("baseline__" + b)) for b in ("VF", "PF", "RobustZ", "ColumnIF", "DDCcore")] + [f(m("lgbm__raw"))])
        meta = json.loads((args.runs / f"{t}__real__s0/meta.json").read_text())
        with np.load(args.runs / f"{t}__real__s0/scores.npz", allow_pickle=False) as z:
            errors, clean = z["errors"], z["clean_values"]
        rv = np.zeros_like(errors, dtype=bool)
        for j in range(clean.shape[1]):
            vals, inv, cnt = np.unique(clean[:, j], return_inverse=True, return_counts=True)
            if len(vals) <= .5 * len(clean):
                rv[:, j] = (cnt[inv] / len(clean) <= .01) & ~errors[:, j]
        sup = np.array([s["kind"] != "unsupported" for s in meta["column_specs"]])
        coverage.append([t, meta["rows"], len(meta["eligible_columns"]), int(errors.sum()),
                         f(float(sup.mean()) * 100, 1), f(float(errors[:, sup].sum() / errors.sum()) * 100, 1)])
        rare.append([t, int(rv.sum())] + [f(metrics["tabpfn-v2__" + a]["rare_valid_alarm"]) for a in ("raw", "random", "purify")])
        seconds = u["cost_seconds_seed_mean"]
        cost.append([t] + [f(seconds["tabpfn-v2__" + a] / 60, 2) for a in ("raw", "random", "pass1_nested", "purify_final", "purify")])
        secondary.append([t, interval(paired["tfm_minus_lgbm_raw"]), interval(paired["oracle_minus_raw"]),
                          interval(paired["tabpfn-v2_raw_leo_minus_raw"]) if t != "rayyan" else "--"])
        for c in ("inj-random", "inj-systematic"):
            unit = data["units"][t + "|" + c]
            probes.append([t, "random" if c == "inj-random" else "systematic",
                           interval(unit["paired"]["purify_minus_random"]), interval(unit["paired"]["oracle_minus_raw"])])
    for unit in data["units"].values():
        failures += sum(len(x["events"]) for x in unit["failures"])
    table(out, "primary", "Real-error AP, averaged over all five seeds. Final column: TabPFN purification minus matched-count random, with descriptive 95\\% row-bootstrap interval. Full eligible universe; intervals condition on predictions.",
          ["Table", "Raw", "Random", "Purify", r"$\Delta$ [95\% interval]"], primary)
    table(out, "baselines", "Real-error AP for measured comparators, five-seed means. DDCcore and conditional LightGBM are separate implementations, not reference DDC or CDC.",
          ["Table", "VF", "PF", "RobustZ", "Col.IF", "DDCcore", "LGBM"], baselines)
    table(out, "coverage", "Real benchmark universe and conditional-target support. Support percentages are specific to the conditional scorer, not universal baseline coverage.",
          ["Table", "Rows", "Columns", "Errors", r"Cells supported (\%)", r"Errors supported (\%)"], coverage)
    table(out, "rare", "Rare-valid alarms in the R-precision budget on real data, five-seed means. The reference-defined denominator is shown. Rates are fractions; unavailable means no denominator.",
          ["Table", "Rare-valid cells", "TFM raw", "Random", "Purify"], rare)
    table(out, "cost", "TabPFN time in minutes per run, five-seed means on real data. Inclusive purification equals nested preparation plus final work. Concurrent local CPU jobs; no peak-memory or forward-call measurement asserted.",
          ["Table", "Raw", "Random", "Nested", "Purify final", "Purify total"], cost)
    table(out, "secondary", "Secondary real-data AP differences and descriptive row-bootstrap intervals. LEO uses observed keys and differs from the primary row boundary; rayyan has no declared key.",
          ["Table", "TFM raw $-$ LGBM", "Oracle $-$ raw", "TFM LEO $-$ raw"], secondary)
    table(out, "probes", "Injection probes: five-seed AP differences with descriptive row-bootstrap intervals. Conditions are repeated measurements within each source, not independent datasets.",
          ["Table", "Injection", "Purify $-$ random", "Oracle $-$ raw"], probes)
    for name in ("primary_deltas.pdf", "mechanism_deltas.pdf"):
        shutil.copyfile(args.analysis / name, out / name)
    macro = data["macro_descriptive"]["real|purify_minus_random"]["mean_delta"]
    (out / "numbers.tex").write_text("\\newcommand{\\PrimaryMacroDelta}{" + f(macro, 4) + "}\n" +
        "\\newcommand{\\FitFailureEvents}{" + str(failures) + "}\n", encoding="utf-8")
    provenance = {"analysis_sha256": hashlib.sha256((args.analysis / "results.json").read_bytes()).hexdigest(),
                  "audit_sha256": hashlib.sha256(args.audit.read_bytes()).hexdigest(),
                  "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  "outputs_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
    (out / "PROVENANCE.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print("Generated manuscript artifacts from verified complete-grid analysis")


if __name__ == "__main__":
    main()
