"""Data models and container structures for CRIC-ED."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Sequence, Set

@dataclass(frozen=True)
class DirtyTable:
    """Represents a dirty tabular dataset under inference isolation."""
    headers: List[str]
    rows: List[List[Any]]
    entity_ids: List[str]
    numeric_col_indices: Set[int]
    categorical_col_indices: Set[int]
    primary_key_col_indices: Set[int] = field(default_factory=set)

    @property
    def num_rows(self) -> int:
        return len(self.rows)

    @property
    def num_cols(self) -> int:
        return len(self.headers)

    def get_cell(self, row_idx: int, col_idx: int) -> Any:
        return self.rows[row_idx][col_idx]

@dataclass
class CellScore:
    """Scoring result for a single coordinate (i, j)."""
    row_idx: int
    col_idx: int
    col_name: str
    raw_value: Any
    score: float
    is_eligible: bool = True
    failure_status: bool = False
    details: dict = field(default_factory=dict)
