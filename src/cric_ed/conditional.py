"""Cross-fitted conditional scoring for cell-level error detection (preregistration v2).

For every eligible column j the observed value x_ij is scored by a conditional model
p(x_j | x_-j) fitted on a context of *other* rows. Rows are split into K folds; queries of
fold f are scored with a context sampled from the remaining folds, so a query row never
enters its own context (except in the labelled `leaky` diagnostic).

Every score is a negative log probability so that columns can be pooled:
- numeric column, parseable value: -log P(parseable) - log(two-sided predictive tail);
- numeric column, non-parseable token: -log P(token) from smoothed context frequencies;
- categorical column: -log of a smoothed class probability; with more than 10 classes the
  model predicts the 9 most frequent classes + OTHER and OTHER mass is split by smoothed
  within-OTHER frequencies (TabPFN v2 supports at most 10 classes).
Near-unique categorical columns (unique ratio > 0.5) are unsupported: score 0, counted in
coverage.

Context arms (shared base context per seed and fold):
- raw:            the base context;
- random:         base minus q|base| rows drawn uniformly (separate random stream);
- purify:         base minus the q|base| rows whose *target cell* has the highest raw-arm
                  score in an inner cross-fit restricted to the outer training pool;
- oracle (diag):  base rows with clean values (uses labels; never a deployable method);
- leaky (diag):   base plus the query fold itself.
"""
from __future__ import annotations

import math
import re
import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy.stats import norm

NUM_RE = re.compile(r"^\s*[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?\s*$")
MAX_CLASSES = 10
TAIL_FLOOR = 1e-12


def parse_num(values: np.ndarray) -> np.ndarray:
    out = np.full(len(values), np.nan)
    for i, v in enumerate(values):
        if NUM_RE.match(v):
            out[i] = float(v)
    return out


@dataclass
class ColumnSpec:
    name: str
    kind: str          # numeric | categorical | unsupported
    unique_ratio: float
    parse_rate: float


def column_specs(dirty: pd.DataFrame, cols: list[str], numeric_min=0.8, unique_max=0.5) -> list[ColumnSpec]:
    specs = []
    for c in cols:
        v = dirty[c].values
        nonempty = v[v != ""]
        parse_rate = float(np.isfinite(parse_num(nonempty)).mean()) if len(nonempty) else 0.0
        ur = dirty[c].nunique() / len(dirty)
        if parse_rate >= numeric_min:
            kind = "numeric"
        elif ur > unique_max:
            kind = "unsupported"
        else:
            kind = "categorical"
        specs.append(ColumnSpec(c, kind, round(ur, 4), round(parse_rate, 4)))
    return specs


class Encoder:
    """Label-free feature encoding fitted on the observed (dirty) table only."""

    def __init__(self, dirty: pd.DataFrame, specs: list[ColumnSpec]):
        self.specs = specs
        self.maps = {}
        for s in specs:
            if s.kind != "numeric":
                vc = dirty[s.name].value_counts(sort=True)
                self.maps[s.name] = {v: float(k) for k, v in enumerate(vc.index)}

    def features(self, frame: pd.DataFrame) -> np.ndarray:
        cols = []
        for s in self.specs:
            v = frame[s.name].values
            if s.kind == "numeric":
                cols.append(parse_num(v))
            else:
                m = self.maps[s.name]
                unk = float(len(m))
                cols.append(np.array([m.get(x, unk) for x in v]))
        return np.column_stack(cols)

    def categorical_idx(self, drop: int) -> list[int]:
        idx = [k for k, s in enumerate(self.specs) if s.kind != "numeric" and k != drop]
        return [k - (k > drop) for k in idx]


# ----------------------------------------------------------------- model adapters
class TabPFNModel:
    name = "tabpfn-v2"

    def __init__(self, clf_path, reg_path, n_estimators=1, seed=0, threads=3):
        from tabpfn import TabPFNClassifier, TabPFNRegressor
        self._C, self._R = TabPFNClassifier, TabPFNRegressor
        self.clf_path, self.reg_path, self.n_est, self.seed = str(clf_path), str(reg_path), n_estimators, seed
        self.threads = threads

    def class_proba(self, Xc, yc, Xq, cat_idx):
        m = self._C(model_path=self.clf_path, device="cpu", n_estimators=self.n_est, random_state=self.seed,
                    categorical_features_indices=cat_idx or None, ignore_pretraining_limits=True, n_jobs=self.threads)
        m.fit(Xc, yc)
        return m.classes_, m.predict_proba(Xq)

    def tail(self, Xc, yc, Xq, yq, cat_idx):
        import torch
        m = self._R(model_path=self.reg_path, device="cpu", n_estimators=self.n_est, random_state=self.seed,
                    categorical_features_indices=cat_idx or None, ignore_pretraining_limits=True, n_jobs=self.threads)
        m.fit(Xc, yc)
        full = m.predict(Xq, output_type="full")
        y = torch.as_tensor(yq, dtype=full["logits"].dtype).unsqueeze(-1)
        cdf = full["criterion"].cdf(full["logits"], y).detach().numpy().reshape(len(yq), -1)[:, 0]
        return 2 * np.minimum(cdf, 1 - cdf)


class LGBMModel:
    """Non-TFM conditional baseline (imputer-style, inspired by CDC; not a CDC reimplementation)."""
    name = "lgbm"

    def __init__(self, seed=0):
        import lightgbm  # noqa: F401
        self.seed = seed

    def _kw(self):
        return dict(n_estimators=100, learning_rate=0.1, num_leaves=15, min_child_samples=5,
                    random_state=self.seed, verbose=-1, n_jobs=1)

    def class_proba(self, Xc, yc, Xq, cat_idx):
        from lightgbm import LGBMClassifier
        m = LGBMClassifier(**self._kw()).fit(Xc, yc)
        return m.classes_, m.predict_proba(Xq)

    def tail(self, Xc, yc, Xq, yq, cat_idx):
        from lightgbm import LGBMRegressor
        from sklearn.model_selection import cross_val_predict
        m = LGBMRegressor(**self._kw())
        cv = min(3, len(yc))
        resid = yc - cross_val_predict(m, Xc, yc, cv=cv) if cv >= 2 else yc - yc.mean()
        sd = max(float(np.std(resid)), 1e-6)
        mu = m.fit(Xc, yc).predict(Xq)
        return 2 * norm.sf(np.abs(yq - mu) / sd)


# ----------------------------------------------------------------- scoring
def _smoothed_token_logp(ctx_tokens: np.ndarray, q_tokens: np.ndarray) -> np.ndarray:
    vals, cnt = np.unique(ctx_tokens, return_counts=True)
    lookup = dict(zip(vals, cnt))
    n, v = len(ctx_tokens), len(vals)
    return np.array([math.log((lookup.get(t, 0) + 0.5) / (n + 0.5 * (v + 1))) for t in q_tokens])


def score_column(model, spec, j, Xc, ctx_vals, Xq, q_vals, cat_idx) -> np.ndarray:
    """Negative log probability for each query value of column j given a context."""
    nq = len(q_vals)
    if spec.kind == "unsupported" or len(ctx_vals) == 0:
        return np.zeros(nq)
    if spec.kind == "numeric":
        yc, yq = parse_num(ctx_vals), parse_num(q_vals)
        okc, okq = np.isfinite(yc), np.isfinite(yq)
        n = len(ctx_vals)
        logp_parse = math.log((okc.sum() + 0.5) / (n + 1.0))
        out = np.empty(nq)
        tok = _smoothed_token_logp(ctx_vals[~okc], q_vals[~okq]) if (~okq).any() else np.array([])
        out[~okq] = -(math.log(max(n - okc.sum(), 0) + 0.5) - math.log(n + 1.0)) - tok if (~okq).any() else 0
        if okq.any():
            if okc.sum() >= 10 and np.ptp(yc[okc]) > 0:
                tail = model.tail(Xc[okc], yc[okc], Xq[okq], yq[okq], cat_idx)
            else:  # degenerate numeric context: exact-match frequency
                tail = np.array([(np.sum(yc[okc] == y) + 0.5) / (okc.sum() + 1.0) for y in yq[okq]])
            out[okq] = -logp_parse - np.log(np.maximum(tail, TAIL_FLOOR))
        return out
    # categorical
    vals, cnt = np.unique(ctx_vals, return_counts=True)
    order = np.argsort(-cnt, kind="stable")
    top = list(vals[order[: MAX_CLASSES - 1]]) if len(vals) > MAX_CLASSES else list(vals)
    other = len(vals) > MAX_CLASSES
    lab = np.array([t if t in set(top) else "\x00OTHER" for t in ctx_vals], dtype=object)
    n = len(ctx_vals)
    if len(np.unique(lab)) < 2:
        classes, proba = np.unique(lab), np.ones((nq, 1))
    else:
        codes, uniq = pd.factorize(lab)
        cls_idx, proba = model.class_proba(Xc, codes, Xq, cat_idx)
        classes = np.asarray(uniq)[cls_idx]
    col = {c: k for k, c in enumerate(classes)}
    if other:
        o_vals, o_cnt = np.unique(ctx_vals[lab == "\x00OTHER"], return_counts=True)
        o_lookup, n_o, v_o = dict(zip(o_vals, o_cnt)), int(o_cnt.sum()), len(o_vals)
    q0 = 1.0 / (len(vals) + 1)
    out = np.empty(nq)
    for i, t in enumerate(q_vals):
        if t in col:
            pt = proba[i, col[t]]
        elif other and "\x00OTHER" in col:
            pt = proba[i, col["\x00OTHER"]] * (o_lookup.get(t, 0) + 0.5) / (n_o + 0.5 * (v_o + 1))
        else:
            pt = 0.0
        out[i] = -math.log((n * pt + q0) / (n + 1.0))
    return out


@dataclass
class RunLog:
    contexts: list = field(default_factory=list)   # full final/inner dependency records
    seconds: dict = field(default_factory=dict)
    failures: list = field(default_factory=list)   # (seed, fold, column, arm, error)


def apply_penalty(S: np.ndarray) -> np.ndarray:
    """Coverage penalty: non-finite cells receive the max finite score + 1.0."""
    finite = np.isfinite(S)
    top = S[finite].max() if finite.any() else 0.0
    return np.where(finite, S, top + 1.0)


def folds_and_bases(n, k, cap, seed, groups=None):
    """Row folds (primary) or entity-group folds (`groups`, leave-entity-out secondary)."""
    if not 2 <= k <= n or cap < 1:
        raise ValueError("Need 2 <= folds <= rows and a positive context cap")
    rng = np.random.default_rng(seed)
    if groups is None:
        perm = rng.permutation(n)
        folds = [np.sort(perm[f::k]) for f in range(k)]
    else:
        groups = np.asarray(groups)
        if groups.ndim != 1 or len(groups) != n or pd.isna(groups).any():
            raise ValueError("One group key per row is required")
        uniq = rng.permutation(np.unique(groups))
        if len(uniq) < k:
            raise ValueError("Leave-entity-out needs at least as many groups as folds")
        assign = {g: i % k for i, g in enumerate(uniq)}
        fold_of = np.array([assign[g] for g in groups])
        folds = [np.flatnonzero(fold_of == f) for f in range(k)]
    bases = []
    for f in range(k):
        pool = np.setdiff1d(np.arange(n), folds[f])
        bases.append(np.sort(rng.choice(pool, min(cap, len(pool)), replace=False)))
    return folds, bases


def score_table(dirty, cols, model, arm, seed, k=5, cap=512, q=0.15, pass1=None, clean=None, log=None,
                groups=None):
    """Candidate scorer; purification isolates all pass-1 work from the outer fold.

    Global pass-1 matrices are rejected because their scores may depend on the outer
    query fold. Nested pass-1 and row-primary/LEO-secondary follow the v2.1 decisions.
    The declared transductive final-pass encoding remains visible in context logs.
    """
    t0 = time.perf_counter()  # includes typing, encoding and nested first-pass work
    if arm not in {"raw", "random", "purify", "oracle", "leaky", "raw_leo"}:
        raise ValueError("Unknown context arm: " + str(arm))
    if (arm == "raw_leo") != (groups is not None):
        raise ValueError("Entity groups are required for, and only for, the raw_leo arm")
    if pass1 is not None:
        raise ValueError("External pass1 is unsafe; purification computes an outer-fold-isolated first pass")
    if not 0 <= q < 1:
        raise ValueError("Trimming fraction must lie in [0, 1)")
    if arm == "oracle" and (clean is None or clean.shape != dirty.shape or
                            not clean.columns.equals(dirty.columns)):
        raise ValueError("Oracle requires an aligned clean table")
    if arm != "oracle" and clean is not None:
        raise ValueError("Clean values may be supplied only to the labelled oracle arm")
    if not cols or len(set(cols)) != len(cols) or any(c not in dirty for c in cols):
        raise ValueError("A nonempty unique eligible-column list is required")
    result = _score_table(dirty, cols, model, arm, seed, k, cap, q, clean, log,
                          np.arange(len(dirty)), "final", None, groups)
    if log is not None:
        log.seconds[(arm, seed)] = time.perf_counter() - t0
    return result


def _score_table(dirty, cols, model, arm, seed, k, cap, q, clean, log,
                 row_ids, stage, outer_fold, groups=None):
    specs = column_specs(dirty, cols)
    enc = Encoder(dirty, specs)
    Xd = enc.features(dirty)
    vals_d = {s.name: dirty[s.name].values for s in specs}
    if arm == "oracle":
        Xo = enc.features(clean)
        vals_o = {s.name: clean[s.name].values for s in specs}
    n = len(dirty)
    S = np.zeros((n, len(cols)))
    folds, bases = folds_and_bases(n, k, cap, seed, groups)
    for f, (qrows, base) in enumerate(zip(folds, bases)):
        inner_scores = None
        pool = np.setdiff1d(np.arange(n), qrows)
        if arm == "purify":
            # Neither preprocessing nor inner fits can see the outer query rows.
            if len(pool) < 2:
                raise ValueError("Purification requires at least two outer training rows")
            t_pass1 = time.perf_counter()
            inner, _ = _score_table(dirty.iloc[pool].reset_index(drop=True), cols, model,
                                    "raw", seed, min(k, len(pool)), cap, q, None, log,
                                    row_ids[pool], "pass1", f)
            if log is not None:  # shared first-pass cost, reported separately from the final pass
                key = ("pass1_nested", seed)
                log.seconds[key] = log.seconds.get(key, 0.0) + time.perf_counter() - t_pass1
            inner_scores = np.full_like(S, np.nan)
            inner_scores[pool] = apply_penalty(inner)
        for j, spec in enumerate(specs):
            keep = np.ones(len(cols), dtype=bool)
            keep[j] = False
            ctx = base
            removed = []
            n_rm = int(round(q * len(base)))
            if arm == "random":
                rr = np.random.default_rng([seed, f, j, 7919])
                removed = np.sort(rr.choice(base, n_rm, replace=False))
                ctx = np.setdiff1d(base, removed)
            elif arm == "purify":
                sc = inner_scores[base, j]
                order = np.lexsort((base, -sc))
                removed = np.sort(base[order[:n_rm]])
                ctx = np.setdiff1d(base, removed)
            elif arm == "leaky":
                ctx = np.union1d(base, qrows)
            Xsrc, vsrc = (Xo, vals_o) if arm == "oracle" else (Xd, vals_d)
            Xc = Xsrc[ctx][:, keep]
            Xq = Xd[qrows][:, keep]
            try:
                S[qrows, j] = score_column(model, spec, j, Xc, vsrc[spec.name][ctx], Xq, vals_d[spec.name][qrows],
                                           enc.categorical_idx(j))
                bad = int((~np.isfinite(S[qrows, j])).sum())
                if bad and log is not None:
                    log.failures.append({"seed": seed, "fold": f, "column": spec.name,
                                         "arm": arm, "stage": stage, "outer_fold": outer_fold,
                                         "nonfinite_cells": bad, "error": "Nonfinite model output"})
            except Exception as e:  # preregistered: failed cells get the coverage penalty later
                S[qrows, j] = np.nan
                if log is not None:
                    log.failures.append({"seed": seed, "fold": f, "column": spec.name,
                                         "arm": arm, "stage": stage, "outer_fold": outer_fold,
                                         "error": f"{type(e).__name__}: {str(e)[:200]}"})
            if log is not None:
                log.contexts.append({"seed": seed, "fold": f, "column": spec.name, "arm": arm,
                                     "stage": stage, "outer_fold": outer_fold,
                                     "query_row_ids": row_ids[qrows].tolist(),
                                     "base_row_ids": row_ids[base].tolist(),
                                     "active_row_ids": row_ids[ctx].tolist(),
                                     "removed_row_ids": row_ids[np.asarray(removed, dtype=int)].tolist(),
                                     "preprocessing_row_ids": row_ids.tolist()})
    return S, specs
