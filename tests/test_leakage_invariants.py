"""Tests verifying strict information boundaries and anti-leakage invariants."""

import pytest
from pathlib import Path
from cric_ed.loader import load_dirty_benchmark_table
from cric_ed.detectors.cric_scorer import CRICDetector
from cric_ed.protocol import group_folds

def test_leave_entity_out_invariants():
    """Verify that no query row or its co-entities ever appear in context."""
    entity_ids = ["e1", "e1", "e2", "e2", "e3", "e3", "e4", "e4", "e5", "e5"]
    folds = group_folds(entity_ids, n_splits=5, seed=42)

    for context_indices, query_indices in folds:
        query_entities = {entity_ids[q] for q in query_indices}
        context_entities = {entity_ids[c] for c in context_indices}

        # Strict disjoint assertion
        intersection = query_entities.intersection(context_entities)
        assert len(intersection) == 0, f"Leakage detected: entities {intersection} shared across split"

def test_target_column_masking_in_distance():
    """Verify that target column is dropped during conditioning distance calculation."""
    detector = CRICDetector()
    row_a = ["e1", 10.0, 20.0, "CatA", 30.0]
    row_b = ["e2", 10.0, 20.0, "CatA", 99999.0]  # Massive difference in column 4

    numeric_cols = {1, 2, 4}

    # When target column is 4 and primary key 0 is ignored, distance must be zero because features 1, 2, 3 are identical
    dist = detector._compute_row_distance(row_a, row_b, target_col=4, numeric_cols=numeric_cols, ignored_cols={0})
    assert dist == 0.0, f"Target column 4 leaked into conditioning distance: got {dist}"

    # When target column is 1 and primary key 0 is ignored, distance must be large because column 4 is included
    dist_with_col4 = detector._compute_row_distance(row_a, row_b, target_col=1, numeric_cols=numeric_cols, ignored_cols={0})
    assert dist_with_col4 > 1000.0, "Feature 4 was unexpectedly dropped"
