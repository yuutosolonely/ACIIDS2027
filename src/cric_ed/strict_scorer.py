"""Unadopted group-isolated alternative, retained as a software diagnostic.

The accepted current v2.1 primary study uses row folds and a LEO secondary; this
module is not its scorer and must not silently replace the author's decision.

Every fitted encoder and predictor sees active context rows only. Pass-1 scoring
is nested inside the outer training groups. No clean values/error masks are accepted.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field

import numpy as np

from cric_ed.conditional import Encoder, apply_penalty, column_specs, score_column
from cric_ed.protocol import group_folds


@dataclass(frozen=True)
class StrictConfig:
    folds: int = 5
    cap: int = 256
    trim: float = 0.15


@dataclass
class StrictLog:
    contexts: list = field(default_factory=list)
    failures: list = field(default_factory=list)
    seconds: dict = field(default_factory=dict)
    model_calls: dict = field(default_factory=dict)


class _CountedModel:
    def __init__(self, model):
        self.model = model
        self.calls = 0

    def tail(self, *args):
        self.calls += 1
        return self.model.tail(*args)

    def class_proba(self, *args):
        self.calls += 1
        return self.model.class_proba(*args)


def context_plan(groups, config: StrictConfig, seed):
    if config.cap < 1 or not 0 <= config.trim < 1:
        raise ValueError("Positive context cap and trim in [0,1) required")
    folds = group_folds(list(groups), config.folds, seed)
    out = []
    for f, (pool, query) in enumerate(folds):
        pool, query = np.asarray(pool, dtype=int), np.asarray(query, dtype=int)
        rng = np.random.default_rng([seed, f, 15485863])
        base = np.sort(rng.choice(pool, min(config.cap, len(pool)), replace=False))
        out.append((pool, query, base))
    return out


def _context_score(dirty, cols, model, specs, j, query, base, active, typing_rows, row_ids,
                   groups, log, stage, outer_fold, fold, arm, reference=None):
    """The reference override is private and reserved for the explicit oracle helper."""
    spec = specs[j]
    if not len(active):
        raise ValueError("No active context remains")
    source = dirty if reference is None else reference
    training = source.iloc[active]
    enc = Encoder(training, specs)
    keep = np.arange(len(cols)) != j
    Xc = enc.features(training)[:, keep]
    Xq = enc.features(dirty.iloc[query])[:, keep]
    failed = False
    try:
        scores = score_column(model, spec, j, Xc, training[spec.name].values,
                              Xq, dirty.iloc[query][spec.name].values, enc.categorical_idx(j))
        if scores.shape != (len(query),) or not np.isfinite(scores).all():
            raise ValueError("Nonfinite or misaligned conditional scores")
    except Exception as exc:
        failed = True
        scores = np.full(len(query), np.nan)
        log.failures.append({"stage": stage, "outer_fold": outer_fold, "fold": fold,
                             "column": spec.name, "arm": arm,
                             "error": f"{type(exc).__name__}: {str(exc)[:200]}"})
    log.contexts.append({"stage": stage, "outer_fold": outer_fold, "fold": fold,
                         "arm": arm, "column": spec.name, "kind": spec.kind,
                         "query_row_ids": row_ids[query].tolist(),
                         "base_row_ids": row_ids[base].tolist(),
                         "active_row_ids": row_ids[active].tolist(),
                         "preprocessing_row_ids": row_ids[active].tolist(),
                         "typing_row_ids": row_ids[typing_rows].tolist(),
                         "query_groups": sorted(set(str(x) for x in groups[query])),
                         "context_groups": sorted(set(str(x) for x in groups[active])),
                         "encoder_sha256": hashlib.sha256(
                             json.dumps(enc.maps, sort_keys=True).encode()).hexdigest()})
    return scores, failed


def _inner_raw(dirty, cols, groups, model, config, seed, row_ids, log, outer_fold):
    k = min(config.folds, len(set(groups)))
    if k < 2:
        raise ValueError("Nested scoring requires at least two outer training groups")
    inner_config = StrictConfig(k, config.cap, config.trim)
    values = np.zeros((len(dirty), len(cols)))
    for f, (pool, query, base) in enumerate(context_plan(groups, inner_config, seed)):
        specs = column_specs(dirty.iloc[pool], cols)
        for j in range(len(cols)):
            values[query, j], _ = _context_score(dirty, cols, model, specs, j, query, base,
                                                base, pool, row_ids, groups, log, "pass1",
                                                outer_fold, f, "raw")
    return apply_penalty(values)


def score_variants(dirty, cols, groups, model, seed, config=StrictConfig(),
                   arms=("raw", "random", "purify"), log=None):
    """Return paired dirty-only scores, coverage/kinds and a full dependency log.

    The shared nested preparation cost is reported separately. Random ignores its
    ranks; a standalone arm cost includes that common cost when compared to purify.
    """
    if not cols or len(cols) != len(set(cols)) or any(c not in dirty for c in cols):
        raise ValueError("Nonempty unique eligible columns required")
    if not arms or len(set(arms)) != len(arms) or set(arms) - {"raw", "random", "purify"}:
        raise ValueError("Only distinct dirty-only arms are accepted")
    if len(groups) != len(dirty) or any(g is None for g in groups):
        raise ValueError("An aligned, nonmissing group registry is required")
    log = StrictLog() if log is None else log
    group_ids = np.asarray(groups, dtype=str)
    row_ids = np.arange(len(dirty))
    counted = _CountedModel(model)
    shape = (len(dirty), len(cols))
    scores = {a: np.zeros(shape) for a in arms}
    kinds = np.zeros(shape, dtype=np.uint8)
    shared_seconds, shared_calls = 0.0, 0
    incremental_seconds = {a: 0.0 for a in arms}
    incremental_calls = {a: 0 for a in arms}
    started = time.perf_counter()
    for f, (pool, query, base) in enumerate(context_plan(group_ids, config, seed)):
        specs = column_specs(dirty.iloc[pool], cols)
        inner = None
        if "purify" in arms:
            before = counted.calls
            t0 = time.perf_counter()
            inner = _inner_raw(dirty.iloc[pool].reset_index(drop=True), cols, group_ids[pool],
                               counted, config, seed, row_ids[pool], log, f)
            shared_seconds += time.perf_counter() - t0
            shared_calls += counted.calls - before
        for j, spec in enumerate(specs):
            kinds[query, j] = {"unsupported": 0, "numeric": 1, "categorical": 2}[spec.kind]
            n_remove = int(round(config.trim * len(base)))
            for arm in arms:
                t0, before = time.perf_counter(), counted.calls
                active = base
                if arm == "random":
                    rr = np.random.default_rng([seed, f, j, 7919])
                    removed = rr.choice(base, n_remove, replace=False)
                    active = np.setdiff1d(base, removed)
                elif arm == "purify":
                    local = np.searchsorted(pool, base)
                    order = np.lexsort((base, -inner[local, j]))
                    active = np.setdiff1d(base, base[order[:n_remove]])
                scores[arm][query, j], _ = _context_score(dirty, cols, counted, specs, j,
                    query, base, active, pool, row_ids, group_ids, log, "final", f, f, arm)
                incremental_seconds[arm] += time.perf_counter() - t0
                incremental_calls[arm] += counted.calls - before
    log.seconds.update(total=time.perf_counter() - started, shared_pass1=shared_seconds,
                       incremental=incremental_seconds)
    log.seconds["common_outer_setup"] = max(0.0, log.seconds["total"] - shared_seconds - sum(incremental_seconds.values()))
    log.model_calls.update(shared_pass1=shared_calls, incremental=incremental_calls)
    return {"scores": scores, "kinds": kinds, "supported": kinds != 0, "log": log}


def score_diagnostic(dirty, cols, groups, model, seed, arm, clean=None,
                     config=StrictConfig(), log=None):
    """Separate entry point for labelled oracle/leaky diagnostics only."""
    if arm not in {"oracle", "leaky"}:
        raise ValueError("A labelled oracle or leaky diagnostic is required")
    if arm == "oracle" and (clean is None or clean.shape != dirty.shape or
                            not clean.columns.equals(dirty.columns)):
        raise ValueError("Aligned oracle reference required")
    if arm == "leaky" and clean is not None:
        raise ValueError("Leaky diagnostic does not accept clean values")
    log = StrictLog() if log is None else log
    groups = np.asarray(groups, dtype=str)
    row_ids = np.arange(len(dirty))
    values = np.zeros((len(dirty), len(cols)))
    started = time.perf_counter()
    counted = _CountedModel(model)
    for f, (pool, query, base) in enumerate(context_plan(groups, config, seed)):
        specs = column_specs(dirty.iloc[pool], cols)
        active = base if arm == "oracle" else np.union1d(base, query)
        for j in range(len(cols)):
            values[query, j], _ = _context_score(dirty, cols, counted, specs, j, query,
                base, active, pool, row_ids, groups, log, "diagnostic", f, f, arm,
                reference=clean if arm == "oracle" else None)
    log.seconds[arm] = time.perf_counter() - started
    log.model_calls[arm] = counted.calls
    return values, log
