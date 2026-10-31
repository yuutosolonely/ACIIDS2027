"""Artifact verifier must reject outer-query and entity leakage in saved logs."""
import importlib.util
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("sklearn")
spec = importlib.util.spec_from_file_location("artifact_audit", Path(__file__).resolve().parents[1] / "tools/audit_v2_artifacts.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def record(**overrides):
    result = {"model": "fixture", "stage": "pass1", "arm": "raw", "outer_fold": 0,
              "column": "x", "query_row_ids": [2], "base_row_ids": [3, 4],
              "active_row_ids": [3, 4], "removed_row_ids": [], "preprocessing_row_ids": [2, 3, 4]}
    return {**result, **overrides}


def test_artifact_audit_rejects_outer_query_encoder_and_fit_leakage():
    outer = {("fixture", 0): {0, 1}}
    audit.audit_context(record(), 5, ["x"], None, outer)
    with pytest.raises(ValueError, match="encoder crossed"):
        audit.audit_context(record(preprocessing_row_ids=[0, 1, 2, 3, 4]), 5, ["x"], None, outer)
    with pytest.raises(ValueError):
        audit.audit_context(record(base_row_ids=[0, 3], active_row_ids=[0, 3]), 5, ["x"], None, outer)


def test_artifact_audit_rejects_distinct_rows_sharing_query_entity():
    c = record(stage="final", arm="raw_leo", outer_fold=None,
               preprocessing_row_ids=list(range(5)))
    groups = np.array([0, 1, 7, 7, 8])
    with pytest.raises(ValueError, match="Entity crossed"):
        audit.audit_context(c, 5, ["x"], groups, {})
