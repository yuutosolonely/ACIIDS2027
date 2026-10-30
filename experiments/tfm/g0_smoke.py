"""Gate G0 smoke test for TabPFN v2 (software check on synthetic data, not evidence).

Verifies that the pinned v2 checkpoints load on CPU, that the regressor returns a
per-query negative log-density for the observed value and the classifier returns
calibrated-looking class probabilities, and times one fit/predict at pilot scale.
Run with the isolated environment: .venv-tfm/Scripts/python.exe experiments/tfm/g0_smoke.py
"""
import json
import platform
import time
from pathlib import Path

import numpy as np
import torch
from importlib.metadata import version
from tabpfn import TabPFNClassifier, TabPFNRegressor

REPO = Path(__file__).resolve().parents[2]
CLF = REPO / "checkpoints/TabPFN-v2-clf/tabpfn-v2-classifier.ckpt"
REG = REPO / "checkpoints/TabPFN-v2-reg/tabpfn-v2-regressor.ckpt"


def main():
    torch.manual_seed(0)
    rng = np.random.default_rng(0)
    n_ctx, n_q, d = 500, 200, 10
    X = rng.normal(size=(n_ctx + n_q, d))
    y = X[:, 0] * 2 + X[:, 1] ** 2 + rng.normal(scale=0.3, size=n_ctx + n_q)
    y_q = y[n_ctx:].copy()
    y_q[:5] += 15.0  # five gross outliers among the queries
    out = {"python": platform.python_version(), "torch": torch.__version__, "tabpfn": version("tabpfn"),
           "threads": torch.get_num_threads(), "n_ctx": n_ctx, "n_query": n_q, "d": d, "runs": []}
    for n_est in (1, 4):
        reg = TabPFNRegressor(model_path=str(REG), device="cpu", n_estimators=n_est, random_state=0)
        t0 = time.perf_counter()
        reg.fit(X[:n_ctx], y[:n_ctx])
        full = reg.predict(X[n_ctx:], output_type="full")
        nll = full["criterion"](full["logits"], torch.as_tensor(y_q, dtype=full["logits"].dtype)).detach().numpy()
        dt = time.perf_counter() - t0
        order = np.argsort(-nll)
        out["runs"].append({"model": "regressor", "n_estimators": n_est, "seconds": round(dt, 2),
                            "nll_finite": bool(np.isfinite(nll).all()),
                            "outliers_in_top5": int(np.isin(order[:5], np.arange(5)).sum()),
                            "nll_outlier_mean": round(float(nll[:5].mean()), 2),
                            "nll_inlier_median": round(float(np.median(nll[5:])), 2)})
        yc = (X[:, 2] > 0).astype(int) + (X[:, 3] > 1).astype(int)
        clf = TabPFNClassifier(model_path=str(CLF), device="cpu", n_estimators=n_est, random_state=0)
        t0 = time.perf_counter()
        clf.fit(X[:n_ctx], yc[:n_ctx])
        proba = clf.predict_proba(X[n_ctx:])
        dt = time.perf_counter() - t0
        out["runs"].append({"model": "classifier", "n_estimators": n_est, "seconds": round(dt, 2),
                            "proba_rows_sum_to_1": bool(np.allclose(proba.sum(1), 1, atol=1e-5)),
                            "classes": clf.classes_.tolist(),
                            "accuracy": round(float((clf.classes_[proba.argmax(1)] == yc[n_ctx:]).mean()), 3)})
    path = REPO / "experiments/tfm/g0_smoke_result.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
