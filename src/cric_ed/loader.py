"""Table loading utility adhering to evaluation insulation."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Optional, Set, Tuple
from cric_ed.models import DirtyTable

def load_dirty_benchmark_table(
    table_path: Path,
    entity_col: str,
    numeric_cols: Set[str],
    primary_key_cols: Optional[Set[str]] = None
) -> DirtyTable:
    """Load dirty table for inference without exposing clean or error labels."""
    with open(table_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    if entity_col not in headers:
        raise ValueError(f"Entity col '{entity_col}' not found in headers {headers}")

    entity_idx = headers.index(entity_col)
    entity_ids = [r[entity_idx] for r in rows]

    numeric_indices = {i for i, h in enumerate(headers) if h in numeric_cols}
    pk_cols = primary_key_cols or {entity_col}
    pk_indices = {i for i, h in enumerate(headers) if h in pk_cols}
    cat_indices = {i for i in range(len(headers)) if i not in numeric_indices and i not in pk_indices}

    return DirtyTable(
        headers=headers,
        rows=rows,
        entity_ids=entity_ids,
        numeric_col_indices=numeric_indices,
        categorical_col_indices=cat_indices,
        primary_key_col_indices=pk_indices
    )

def load_ground_truth_errors(errors_path: Path) -> Tuple[List[str], List[List[int]]]:
    """Load isolated ground truth binary error mask strictly for evaluation harness."""
    with open(errors_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        mask = [[int(cell) for cell in row] for row in reader]
    return headers, mask
