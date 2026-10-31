"""RAHA benchmark loading, eligibility, row subsampling and controlled error injection.

Clean tables and error masks live in `Table.clean` / `Table.errors` and are consumed only by
evaluation code and explicitly labelled oracle diagnostics; detectors receive `Table.dirty`.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "raw" / "raha"
ID_NAMES = {"id", "index", "tuple_id"}


@dataclass
class Table:
    """A dirty table plus evaluation-only ground truth (never passed to detectors)."""

    name: str
    dirty: pd.DataFrame
    clean: pd.DataFrame
    eligible: list[str]
    meta: dict = field(default_factory=dict)

    @property
    def errors(self) -> np.ndarray:
        return (self.dirty[self.eligible].values != self.clean[self.eligible].values)


def _read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")


def eligible_columns(df: pd.DataFrame) -> list[str]:
    """Exclude row identifiers: named id-like columns that are unique per row."""
    out = []
    for c in df.columns:
        if c.lower() in ID_NAMES and df[c].is_unique:
            continue
        out.append(c)
    return out


def subsample(t: Table, max_rows: int, seed: int) -> Table:
    """Fixed random row subsample (same rows for dirty and clean)."""
    if len(t.dirty) <= max_rows:
        return t
    idx = np.sort(np.random.default_rng(seed).choice(len(t.dirty), max_rows, replace=False))
    meta = dict(t.meta, subsample={"max_rows": max_rows, "seed": seed, "from_rows": len(t.dirty)},
                row_ids=idx.tolist())
    return Table(t.name, t.dirty.iloc[idx].reset_index(drop=True), t.clean.iloc[idx].reset_index(drop=True),
                 t.eligible, meta)


def load_real(name: str) -> Table:
    dirty = _read(RAW / name / "dirty.csv")
    clean = _read(RAW / name / "clean.csv")
    if list(clean.columns) != list(dirty.columns):
        # RAHA ships differently-cased/named headers for some clean files; order is identical.
        assert clean.shape == dirty.shape, name
        clean.columns = dirty.columns
    elig = eligible_columns(dirty)
    return Table(name, dirty, clean, elig, {"source": "real", "sha256": file_sha(RAW / name / "dirty.csv")})


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- injection
ERROR_TYPES = ("typo", "replace", "missing", "format", "scale")
_NUM = re.compile(r"^-?\d+(\.\d+)?$")


def _typo(v: str, rng: np.random.Generator) -> str:
    if len(v) < 2:
        return v + "x"
    i = int(rng.integers(len(v)))
    op = rng.integers(4)
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    if op == 0:  # substitute
        ch = alphabet[int(rng.integers(len(alphabet)))]
        while ch == v[i]:
            ch = alphabet[int(rng.integers(len(alphabet)))]
        return v[:i] + ch + v[i + 1:]
    if op == 1:  # delete
        return v[:i] + v[i + 1:]
    if op == 2:  # insert
        return v[:i] + alphabet[int(rng.integers(len(alphabet)))] + v[i:]
    j = min(i + 1, len(v) - 1)  # transpose (falls back to substitute if equal)
    if v[i] == v[j]:
        return v[:i] + ("x" if v[i] != "x" else "y") + v[i + 1:]
    s = list(v)
    s[i], s[j] = s[j], s[i]
    return "".join(s)


def _format(v: str, rng: np.random.Generator) -> str:
    """Representation change that keeps semantics recognisable to a human."""
    if _NUM.match(v):
        return [v + ".0", v + " units", "~" + v][int(rng.integers(3))]
    opts = [v.upper(), v + " ", "_".join(v.split()), "(" + v + ")"]
    opts = [o for o in opts if o != v] or [v + "#"]
    return opts[int(rng.integers(len(opts)))]


def _scale(v: str, rng: np.random.Generator) -> str | None:
    if not _NUM.match(v):
        return None
    f = float(v) * [10.0, 100.0, 0.1][int(rng.integers(3))]
    return str(int(f)) if f.is_integer() else f"{f:.4g}"


def corrupt_value(v: str, etype: str, domain: np.ndarray, rng: np.random.Generator) -> str | None:
    if etype == "typo":
        return _typo(v, rng) if v else None
    if etype == "missing":
        return "" if v else None
    if etype == "format":
        return _format(v, rng) if v else None
    if etype == "scale":
        return _scale(v, rng)
    if etype == "replace":  # in-domain substitution: only cross-column evidence can expose it
        others = domain[domain != v]
        return str(others[int(rng.integers(len(others)))]) if len(others) else None
    raise ValueError(etype)


def inject(clean: pd.DataFrame, eligible: list[str], rate: float, structure: str,
           seed: int, types: tuple[str, ...] = ERROR_TYPES) -> pd.DataFrame:
    """Corrupt `rate` of eligible cells of a clean table.

    structure="random": independent cells, error type drawn uniformly per cell.
    structure="systematic": errors come in repeated templates; a template picks a
    (column, clean value) and maps a share of its occurrences to the SAME wrong value,
    emulating source-specific or batch errors that can look frequent in context.
    """
    rng = np.random.default_rng(seed)
    dirty = clean.copy()
    n_rows = len(clean)
    target = int(round(rate * n_rows * len(eligible)))
    domains = {c: clean[c].unique() for c in eligible}
    hit = np.zeros((n_rows, len(eligible)), dtype=bool)
    done, guard = 0, 0
    while done < target and guard < target * 50:
        guard += 1
        j = int(rng.integers(len(eligible)))
        c = eligible[j]
        etype = types[int(rng.integers(len(types)))]
        if structure == "random":
            i = int(rng.integers(n_rows))
            if hit[i, j]:
                continue
            new = corrupt_value(clean.iat[i, clean.columns.get_loc(c)], etype, domains[c], rng)
            if new is None or new == clean.iat[i, clean.columns.get_loc(c)]:
                continue
            dirty.iat[i, dirty.columns.get_loc(c)] = new
            hit[i, j] = True
            done += 1
        elif structure == "systematic":
            col = clean[c].values
            i0 = int(rng.integers(n_rows))
            v = col[i0]
            new = corrupt_value(v, etype, domains[c], rng)
            if new is None or new == v:
                continue
            rows = np.flatnonzero((col == v) & ~hit[:, j])
            if len(rows) < 2:
                continue
            share = rng.uniform(0.3, 0.8)
            k = max(2, int(round(share * len(rows))))
            k = min(k, len(rows), target - done)
            if k < 1:
                break
            chosen = rng.choice(rows, size=k, replace=False)
            dirty.iloc[chosen, dirty.columns.get_loc(c)] = new
            hit[chosen, j] = True
            done += k
        else:
            raise ValueError(structure)
    return dirty


def load_injected(name: str, rate: float, structure: str, seed: int) -> Table:
    base = load_real(name)
    clean = base.clean
    dirty = inject(clean, base.eligible, rate, structure, seed)
    meta = {"source": "injected", "base": name, "rate": rate, "structure": structure, "seed": seed,
            "clean_sha256": file_sha(RAW / name / "clean.csv")}
    return Table(f"{name}+inj", dirty, clean, base.eligible, meta)


def describe(t: Table) -> dict:
    e = t.errors
    return {"name": t.name, "rows": len(t.dirty), "eligible_cols": len(t.eligible),
            "cells": int(e.size), "errors": int(e.sum()), "error_rate": round(float(e.mean()), 4),
            "meta": json.loads(json.dumps(t.meta))}


ROW_CAP = 1000
CONFIRMATORY = ("hospital", "flights", "beers", "rayyan")
DEVELOPMENT = ("movies_1",)


def get_table(name: str, condition: str, seed: int, rate: float = 0.10) -> Table:
    """Table for preregistration v2: `real`, `inj-random` or `inj-systematic`."""
    base = subsample(load_real(name), ROW_CAP, 0)
    if condition == "real":
        return base
    structure = {"inj-random": "random", "inj-systematic": "systematic"}[condition]
    dirty = inject(base.clean, base.eligible, rate, structure, seed)
    meta = dict(base.meta, source="injected", condition=condition, rate=rate, injection_seed=seed)
    return Table(name, dirty, base.clean, base.eligible, meta)


# Public-schema entity keys for the leave-entity-out secondary analysis (author decision
# 2026-10-30). Chosen from column names in the published schemas, not from labels or error
# rates. Keys are read from the *observed* table, so a corrupted key can split one entity.
ENTITY_KEYS = {"hospital": "provider_number", "flights": "flight", "beers": "brewery_id"}


def entity_groups(t: Table) -> np.ndarray | None:
    key = ENTITY_KEYS.get(getattr(t, "name", None))
    if key is None:
        return None
    if key not in t.dirty:
        raise ValueError("Declared entity key missing from observed table: " + key)
    codes, _ = pd.factorize(t.dirty[key].values)
    return codes
