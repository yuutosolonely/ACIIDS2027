"""Unsupervised cell-level error detectors.

All detectors map an observed table (pandas, string cells) to a score matrix of shape
(rows, eligible columns); larger means more suspicious. Detectors never receive clean
values or error masks. The only exception is `cce(..., context=<clean frame>)`, which
is the explicitly labelled oracle diagnostic used to measure the contamination gap.

Information boundary of CCE: the score of cell (i, j) is computed from counts over
all *other* rows (exact leave-one-row-out), optionally further excluding the query's
entity group (leave-entity-out ablation) and any context cells removed by
purification. The query cell's own value never enters its own evidence.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

_LETTERS = re.compile(r"[A-Za-z]+")


def signature(v: str) -> str:
    """Character-class pattern: letter runs collapse to one symbol, digits keep length."""
    if v == "":
        return "<empty>"
    s = _LETTERS.sub(lambda m: "A" if m.group(0)[0].isupper() else "a", v)
    return re.sub(r"\d", "9", s)


def _codes(frames: list[pd.DataFrame], cols: list[str], view: str = "raw") -> list[np.ndarray]:
    """Jointly factorise columns of several frames so equal strings share a code."""
    outs = [np.empty((len(f), len(cols)), dtype=np.int64) for f in frames]
    for j, c in enumerate(cols):
        vals = [f[c].values for f in frames]
        if view == "sig":
            vals = [np.array([signature(x) for x in v], dtype=object) for v in vals]
        allv = np.concatenate(vals)
        codes, _ = pd.factorize(allv)
        off = 0
        for o, v in zip(outs, vals):
            o[:, j] = codes[off:off + len(v)]
            off += len(v)
    return outs


def _lookup(ctx_keys: np.ndarray, q_keys: np.ndarray) -> np.ndarray:
    """Counts of each query key among context keys."""
    if len(ctx_keys) == 0:
        return np.zeros(len(q_keys), dtype=np.int64)
    u, cnt = np.unique(ctx_keys, return_counts=True)
    pos = np.searchsorted(u, q_keys)
    pos = np.clip(pos, 0, len(u) - 1)
    return np.where(u[pos] == q_keys, cnt[pos], 0)


@dataclass
class CCEConfig:
    alpha: float = 1.0        # Dirichlet strength of the marginal prior in p(x_j | x_k)
    beta: float = 0.5         # additive smoothing of the marginal
    top_m: int = 0            # 0 = all experts, else keep the m most informative per column
    views: tuple = ("raw", "sig")
    combine: str = "sum"      # how per-view surprisals are combined: sum | max
    query_purify: bool = True  # drop experts whose conditioning cell is flagged


class _Engine:
    """Leave-one-out conditional evidence for one representation view."""

    def __init__(self, q_tgt, ctx_tgt, q_cond, ctx_cond, keep, groups, cfg: CCEConfig):
        self.qt, self.ct, self.qc, self.cc = q_tgt, ctx_tgt, q_cond, ctx_cond
        self.keep, self.groups, self.cfg = keep, groups, cfg
        self.n, self.d = q_tgt.shape

    def _marg(self, j):
        keep = self.keep[:, j]
        ctx = self.ct[keep, j]
        cnt = _lookup(ctx, self.qt[:, j])
        tot = np.full(self.n, keep.sum(), dtype=np.float64)
        self_in = keep & (self.ct[:, j] == self.qt[:, j])
        cnt = cnt - self_in
        tot = tot - keep
        if self.groups is not None:
            gk, gc = self._group_counts(self.ct[:, j], keep, self.qt[:, j])
            cnt, tot = cnt - (gc - self_in), tot - (gk - keep)
        vocab = len(np.unique(ctx)) + 1
        q = (cnt + self.cfg.beta) / (tot + self.cfg.beta * vocab)
        return q

    def _group_counts(self, ctx_col, keep, q_col, ctx_cond=None, q_cond=None):
        """Counts contributed by the query row's own entity group (incl. itself)."""
        g = self.groups
        gk = _lookup(g[keep], g)
        key_c = g * (ctx_col.max() + 1 + q_col.max() + 1) + ctx_col
        key_q = g * (ctx_col.max() + 1 + q_col.max() + 1) + q_col
        if ctx_cond is not None:
            base = max(ctx_cond.max(), q_cond.max()) + 1
            key_c = key_c * base + ctx_cond
            key_q = key_q * base + q_cond
        gc = _lookup(key_c[keep], key_q)
        return gk.astype(np.float64), gc.astype(np.float64)

    def _pair(self, j, k, qj):
        keep = self.keep[:, j] & self.keep[:, k]
        a_c, b_c = self.ct[:, j], self.cc[:, k]
        a_q, b_q = self.qt[:, j], self.qc[:, k]
        base = int(max(b_c.max(), b_q.max())) + 1
        nab = _lookup((a_c * base + b_c)[keep], a_q * base + b_q).astype(np.float64)
        nb = _lookup(b_c[keep], b_q).astype(np.float64)
        self_b = keep & (b_c == b_q)
        self_ab = self_b & (a_c == a_q)
        nab, nb = nab - self_ab, nb - self_b
        if self.groups is not None:
            # remove the other rows of the query's entity group that share b / (a, b)
            g = self.groups
            gkb = _lookup((g * base + b_c)[keep], g * base + b_q)
            kb2 = int(max(a_c.max(), a_q.max())) + 1
            gkab = _lookup(((g * base + b_c) * kb2 + a_c)[keep], (g * base + b_q) * kb2 + a_q)
            nab = nab - (gkab - self_ab)
            nb = nb - (gkb - self_b)
        p = (nab + self.cfg.alpha * qj) / (nb + self.cfg.alpha)
        return p

    def surprisal(self, flagged: np.ndarray | None) -> np.ndarray:
        S = np.zeros((self.n, self.d))
        for j in range(self.d):
            qj = self._marg(j)
            ll0 = -np.log(qj)
            rows = self.keep[:, j]
            ce0 = ll0[rows].mean() if rows.any() else 0.0
            experts = []
            for k in range(self.d):
                if k == j:
                    continue
                pk = self._pair(j, k, qj)
                llk = -np.log(pk)
                both = self.keep[:, j] & self.keep[:, k]
                if not both.any() or ce0 <= 0:
                    continue
                w = max(0.0, 1.0 - llk[both].mean() / ce0)
                if w > 0:
                    experts.append((w, k, llk))
            if self.cfg.top_m:
                experts = sorted(experts, key=lambda e: -e[0])[: self.cfg.top_m]
            wmax = max((e[0] for e in experts), default=0.0)
            w0 = max(1.0 - wmax, 0.05)
            num = w0 * ll0
            den = np.full(self.n, w0)
            for w, k, llk in experts:
                use = np.ones(self.n, dtype=bool)
                if flagged is not None and self.cfg.query_purify:
                    use = ~flagged[:, k]
                num = num + np.where(use, w * llk, 0.0)
                den = den + np.where(use, w, 0.0)
            S[:, j] = num / den
        return S


def cce(dirty: pd.DataFrame, cols: list[str], cfg: CCEConfig | None = None,
        keep: np.ndarray | None = None, flagged: np.ndarray | None = None,
        context: pd.DataFrame | None = None, groups: np.ndarray | None = None) -> np.ndarray:
    """Cross-fitted Conditional Evidence score.

    keep: boolean (rows, cols) mask of context cells (False = removed by purification).
    context: alternative context values (oracle diagnostic only); queries stay `dirty`.
    groups: integer entity ids for the leave-entity-out ablation.
    """
    cfg = cfg or CCEConfig()
    ctx = dirty if context is None else context
    n = len(dirty)
    keep = np.ones((n, len(cols)), dtype=bool) if keep is None else keep
    out = []
    for view in cfg.views:
        q_raw, c_raw = _codes([dirty, ctx], cols, "raw")
        if view == "raw":
            qt, ct = q_raw, c_raw
        else:
            qt, ct = _codes([dirty, ctx], cols, "sig")
        out.append(_Engine(qt, ct, q_raw, c_raw, keep, groups, cfg).surprisal(flagged))
    if len(out) == 1:
        return out[0]
    return np.sum(out, axis=0) if cfg.combine == "sum" else np.max(out, axis=0)


def top_cells(scores: np.ndarray, frac: float) -> np.ndarray:
    k = int(round(frac * scores.size))
    flag = np.zeros(scores.size, dtype=bool)
    if k > 0:
        flag[np.argsort(-scores, kind="stable")[:k]] = True
    return flag.reshape(scores.shape)


def cce_purified(dirty, cols, cfg=None, rho=0.05, mode="cell", seed=0, iters=1, groups=None):
    """Two-pass CCE. mode: cell | row | random_cell | random_row.

    Pass 1 scores every cell with the full leave-one-out context. The rho fraction of
    most suspicious cells (mode=cell) is removed from the context and, at query time,
    from the conditioning evidence; pass 2 rescores all cells. Random modes remove the
    same number of cells (or rows) uniformly at random: the matched controls that
    separate the effect of *which* evidence is removed from *how much*.
    """
    cfg = cfg or CCEConfig()
    S = cce(dirty, cols, cfg, groups=groups)
    n, d = S.shape
    rng = np.random.default_rng(seed)
    for _ in range(iters):
        if mode == "cell":
            flag = top_cells(S, rho)
        elif mode == "random_cell":
            flag = np.zeros(S.size, dtype=bool)
            flag[rng.choice(S.size, int(round(rho * S.size)), replace=False)] = True
            flag = flag.reshape(S.shape)
        elif mode in ("row", "random_row"):
            r = int(round(rho * n))  # same number of removed cells as rho*n*d
            if mode == "row":
                rows = np.argsort(-S.max(axis=1), kind="stable")[:r]
            else:
                rows = rng.choice(n, r, replace=False)
            flag = np.zeros_like(S, dtype=bool)
            flag[rows] = True
        else:
            raise ValueError(mode)
        S = cce(dirty, cols, cfg, keep=~flag, flagged=flag if mode.endswith("cell") else None,
                groups=groups)
    return S


# ------------------------------------------------------------------ baselines
def value_frequency(dirty, cols):
    return _marginal(dirty, cols, "raw")


def _marginal(dirty, cols, view, beta=0.5):
    (q,) = _codes([dirty], cols, view)
    S = np.zeros(q.shape)
    for j in range(q.shape[1]):
        cnt = np.bincount(q[:, j])
        c = cnt[q[:, j]] - 1
        vocab = (cnt > 0).sum() + 1
        S[:, j] = -np.log((c + beta) / (len(q) - 1 + beta * vocab))
    return S


def pattern_frequency(dirty, cols):
    return _marginal(dirty, cols, "sig")


def vf_pf(dirty, cols):
    return _marginal(dirty, cols, "raw") + _marginal(dirty, cols, "sig")


_NUMRE = re.compile(r"^\s*-?\d+(\.\d+)?\s*$")


def robust_z(dirty, cols, min_numeric=0.8, cap=10.0):
    """MAD z-score on numeric columns; unparsable values in numeric columns get `cap`."""
    S = np.zeros((len(dirty), len(cols)))
    for j, c in enumerate(cols):
        v = dirty[c].values
        ok = np.array([bool(_NUMRE.match(x)) for x in v])
        if ok.mean() < min_numeric:
            continue
        x = np.array([float(a) if o else np.nan for a, o in zip(v, ok)])
        med = np.nanmedian(x)
        mad = np.nanmedian(np.abs(x - med)) * 1.4826
        z = np.abs(x - med) / (mad if mad > 0 else (np.nanstd(x) or 1.0))
        S[:, j] = np.where(ok, np.minimum(z, cap), cap)
    return S


def fd_violations(dirty, cols, max_g3=0.1, max_lhs_ratio=0.9):
    """Approximate-FD detector: x_ij is suspicious when it differs from the leave-one-out
    majority value of j within its LHS group, summed over discovered FDs k -> j."""
    (q,) = _codes([dirty], cols, "raw")
    n, d = q.shape
    S = np.zeros((n, d))
    for j in range(d):
        for k in range(d):
            if k == j:
                continue
            b = q[:, k]
            if len(np.unique(b)) > max_lhs_ratio * n:
                continue
            df = pd.DataFrame({"b": b, "a": q[:, j]})
            ab = df.groupby(["b", "a"]).size().rename("nab").reset_index()
            nb = df.groupby("b").size().rename("nb")
            top = ab.sort_values("nab", ascending=False).drop_duplicates("b").set_index("b")
            m = df.join(nb, on="b").join(top.rename(columns={"a": "amaj", "nab": "nmaj"}), on="b")
            multi = m["nb"].values >= 2
            if multi.sum() < 0.5 * n:
                continue
            g3 = 1 - top["nab"].sum() / len(df)
            if g3 > max_g3:
                continue
            viol = multi & (m["a"].values != m["amaj"].values)
            S[:, j] += viol * (1 - g3)
    return S


def isolation_forest_rows(dirty, cols, seed=0):
    """Row-level anomaly detector broadcast to cells (a row-vs-cell task contrast)."""
    X = _marginal(dirty, cols, "raw")
    f = IsolationForest(n_estimators=200, random_state=seed).fit(X)
    r = -f.score_samples(X)
    return np.repeat(r[:, None], len(cols), axis=1)


BASELINES = {
    "VF": value_frequency,
    "PF": pattern_frequency,
    "VF+PF": vf_pf,
    "RobustZ": robust_z,
    "FD": fd_violations,
    "IF-row": isolation_forest_rows,
}
