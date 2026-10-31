"""EXPLORATORY ONLY (unapproved pivot probe, 2026-10-30). Not confirmatory evidence.

Runs the exploratory `cced` detectors on the designated development dataset movies_1
(real errors and injected errors). No other RAHA dataset is scored by this script.
"""
import json, platform, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from cced import detectors as D
from cced.data import load_injected, load_real, describe
from cced.metrics import summarize

def run(t):
    X, c, E = t.dirty, t.eligible, t.errors
    nonmaj = [j for j in range(len(c)) if E[:, j].mean() <= 0.5]
    arms = {k: f(X, c) for k, f in D.BASELINES.items()}
    arms["CCE"] = D.cce(X, c)
    arms["CCE-raw"] = D.cce(X, c, D.CCEConfig(views=("raw",)))
    arms["CCE+P(cell,0.05)"] = D.cce_purified(X, c, rho=0.05, mode="cell")
    arms["CCE+P(random_cell,0.05)"] = D.cce_purified(X, c, rho=0.05, mode="random_cell")
    arms["DIAG oracle-clean context"] = D.cce(X, c, context=t.clean)
    return {"table": describe(t), "results": {k: {"all": summarize(S, E), "non_majority_error_cols": summarize(S[:, nonmaj], E[:, nonmaj])} for k, S in arms.items()}}

out = {"run_id": "explore_cced_movies_001", "role": "EXPLORATORY dev probe (movies_1 only)",
       "python": platform.python_version(), "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "runs": []}
out["runs"].append(run(load_real("movies_1")))
for st in ("random", "systematic"):
    out["runs"].append(run(load_injected("movies_1", 0.05, st, 0)))
p = Path(__file__).with_name("explore_cced_movies_001.json")
p.write_text(json.dumps(out, indent=1), encoding="utf-8")
print(p)
