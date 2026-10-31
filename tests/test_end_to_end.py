"""End-to-end integration test running on synthetic benchmark fixture."""

from pathlib import Path
from cric_ed.loader import load_dirty_benchmark_table, load_ground_truth_errors
from cric_ed.detectors.baseline_classical import RobustCoordinateDevianceDetector
from cric_ed.detectors.cric_scorer import CRICDetector
from cric_ed.evaluation.evaluator import evaluate_cell_scores

def test_cric_ed_vs_baseline_on_fixture():
    fixture_dir = Path(__file__).resolve().parent.parent / "data" / "fixtures" / "toy_mixed"
    dirty_path = fixture_dir / "dirty.csv"
    errors_path = fixture_dir / "errors.csv"

    table = load_dirty_benchmark_table(
        dirty_path,
        entity_col="entity_id",
        numeric_cols={"feature_a", "feature_b", "num_target"},
        primary_key_cols={"entity_id"}
    )
    headers, gt_mask = load_ground_truth_errors(errors_path)

    # 1. Baseline Run
    base_detector = RobustCoordinateDevianceDetector()
    base_scores = base_detector.score_table(table)
    base_metrics = evaluate_cell_scores(
        base_scores,
        gt_mask,
        table.entity_ids,
        table.numeric_col_indices
    )
    assert base_metrics["overall_auprc"] > 0.05
    assert base_metrics["eligible_cells"] == 400  # 100 rows * 4 non-pk cols

    # 2. CRIC-ED Run (Influence Trimming)
    cric_detector = CRICDetector(
        context_size=30,
        trim_ratio=0.15,
        trimming_mode="influence",
        n_splits=5,
        seed=42,
        rare_valid_patterns={"category_c": {"RareDelta"}}
    )
    cric_scores = cric_detector.score_table(table)
    cric_metrics = evaluate_cell_scores(
        cric_scores,
        gt_mask,
        table.entity_ids,
        table.numeric_col_indices
    )
    assert cric_metrics["overall_auprc"] > 0.05
    assert cric_metrics["eligible_cells"] == 400

    # 3. Matched Random Removal Ablation
    cric_rand = CRICDetector(
        context_size=30,
        trim_ratio=0.15,
        trimming_mode="matched_random",
        n_splits=5,
        seed=42
    )
    rand_scores = cric_rand.score_table(table)
    rand_metrics = evaluate_cell_scores(
        rand_scores,
        gt_mask,
        table.entity_ids,
        table.numeric_col_indices
    )
    assert rand_metrics["eligible_cells"] == 400
