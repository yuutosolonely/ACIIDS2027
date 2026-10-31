"""Label-free cell-level baselines on the observed table (preregistration v2).

All return a score matrix (rows x eligible columns), larger = more suspicious.
- VF: -log smoothed leave-one-out frequency of the value in its column.
- PF: the same on character-class patterns (letter runs collapsed, digits kept).
- RobustZ: |x - median| / (1.4826 MAD) on numeric columns; non-parseable values get the cap.
- ColumnIF: Isolation Forest fitted per column on a 1-D encoding (value or log-frequency).
- DDCcore: simplified re-implementation of the core of DDC (Rousseeuw & Van den Bossche,
  2018) for numeric columns: robust standardisation, robust pairwise correlations, prediction
  of each standardised cell from correlated columns, standardised residual. Not the
  reference implementation (R package `cellWise` was unavailable); see the protocol.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import IsolationForest

from cric_ed.conditional import column_specs, parse_num

_LETTERS = re.compile(r"[A-Za-z]+")
CAP = 10.0


def signature(v: str) -> str:
    if v == "":
        return "<empty>"
    s = _LETTERS.sub(lambda m: "A" if m.group(0)[0].isupper() else "a", v)
    return re.sub(r"\d", "9", s)


def _loo_surprisal(values: np.ndarray, beta=0.5) -> np.ndarray:
    codes, uniq = pd.factorize(values)
    cnt = np.bincount(codes)
    c = cnt[codes] - 1
    return -np.log((c + beta) / (len(values) - 1 + beta * (len(uniq) + 1)))


def value_frequency(dirty, cols, seed=0):
    return np.column_stack([_loo_surprisal(dirty[c].values) for c in cols])


def pattern_frequency(dirty, cols, seed=0):
    return np.column_stack([_loo_surprisal(np.array([signature(v) for v in dirty[c].values], dtype=object))
                            for c in cols])


def robust_z(dirty, cols, seed=0):
    S = np.zeros((len(dirty), len(cols)))
    for j, s in enumerate(column_specs(dirty, cols)):
        if s.kind != "numeric":
            continue
        x = parse_num(dirty[s.name].values)
        med = np.nanmedian(x)
        mad = 1.4826 * np.nanmedian(np.abs(x - med))
        scale = mad if mad > 0 else (np.nanstd(x) or 1.0)
        S[:, j] = np.where(np.isfinite(x), np.minimum(np.abs(x - med) / scale, CAP), CAP)
    return S


def column_isolation_forest(dirty, cols, seed=0):
    S = np.zeros((len(dirty), len(cols)))
    for j, s in enumerate(column_specs(dirty, cols)):
        v = dirty[s.name].values
        if s.kind == "numeric":
            x = parse_num(v)
            fill = np.nanmax(np.abs(x)) * 10 + 1 if np.isfinite(x).any() else 0.0
            feat = np.where(np.isfinite(x), x, fill)
        else:
            feat = _loo_surprisal(v)
        f = IsolationForest(n_estimators=100, random_state=seed).fit(feat.reshape(-1, 1))
        S[:, j] = -f.score_samples(feat.reshape(-1, 1))
    return S


def ddc_core(dirty, cols, seed=0, cutoff=2.576, min_corr=0.5):
    specs = column_specs(dirty, cols)
    num = [j for j, s in enumerate(specs) if s.kind == "numeric"]
    S = np.zeros((len(dirty), len(cols)))
    if not num:
        return S
    Z = {}
    for j in num:
        x = parse_num(dirty[specs[j].name].values)
        med = np.nanmedian(x)
        mad = 1.4826 * np.nanmedian(np.abs(x - med))
        Z[j] = (x - med) / (mad if mad > 0 else (np.nanstd(x) or 1.0))
    clean = {j: np.where(np.abs(Z[j]) <= cutoff, Z[j], np.nan) for j in num}
    for j in num:
        preds, weights = [], []
        for h in num:
            if h == j:
                continue
            ok = np.isfinite(clean[j]) & np.isfinite(clean[h])
            if ok.sum() < 10:
                continue
            r = spearmanr(clean[j][ok], clean[h][ok]).statistic
            if not np.isfinite(r) or abs(r) < min_corr:
                continue
            slope = np.median(clean[j][ok] / np.where(clean[h][ok] == 0, np.nan, clean[h][ok]))
            slope = slope if np.isfinite(slope) else 0.0
            preds.append(slope * Z[h])
            weights.append(abs(r))
        z = Z[j]
        if preds:
            P = np.array(preds)
            W = np.array(weights)[:, None] * np.isfinite(P)
            zhat = np.nansum(np.nan_to_num(P) * W, 0) / np.where(W.sum(0) > 0, W.sum(0), np.nan)
            zhat = np.where(np.isfinite(zhat), zhat, 0.0)
        else:
            zhat = np.zeros_like(z)
        resid = z - zhat
        sc = 1.4826 * np.nanmedian(np.abs(resid - np.nanmedian(resid)))
        sc = sc if sc and sc > 0 else 1.0
        S[:, j] = np.where(np.isfinite(z), np.minimum(np.abs(resid) / sc, CAP), CAP)
    return S


BASELINES = {
    "VF": value_frequency,
    "PF": pattern_frequency,
    "RobustZ": robust_z,
    "ColumnIF": column_isolation_forest,
    "DDCcore": ddc_core,
}
