"""Evaluation harness for cell error detection.

Strictly isolates ground-truth labels and computes cell-level AUPRC,
budgeted metrics, and cluster-preserving bootstrap confidence intervals.
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Optional, Sequence, Tuple
from cric_ed.models import CellScore

def compute_average_precision(scores: Sequence[float], labels: Sequence[int]) -> float:
    """Compute Average Precision (AUPRC) using step-wise integration.
    
    Higher score indicates higher suspicion of error.
    """
    if len(scores) != len(labels) or not scores:
        return 0.0

    positives = sum(labels)
    if positives == 0:
        return 0.0

    # Sort descending by score, stable tie-breaking
    paired = sorted(zip(scores, labels), key=lambda x: -x[0])

    tp = 0
    fp = 0
    precisions = []
    recalls = []

    # Compute precision-recall points
    cum_tp = 0
    ap = 0.0
    prev_recall = 0.0

    for i, (s, y) in enumerate(paired):
        if y == 1:
            cum_tp += 1
        current_precision = cum_tp / (i + 1)
        current_recall = cum_tp / positives

        # Integrate area when recall increases
        if current_recall > prev_recall:
            ap += current_precision * (current_recall - prev_recall)
            prev_recall = current_recall

    return float(ap)

def cluster_bootstrap_auprc_ci(
    scores_by_row: Dict[int, List[float]],
    labels_by_row: Dict[int, List[int]],
    entity_to_rows: Dict[str, List[int]],
    n_bootstraps: int = 200,
    seed: int = 42
) -> Tuple[float, float, float]:
    """Compute mean and 95% CI for AUPRC using cluster-preserving bootstrap over entities."""
    rng = random.Random(seed)
    unique_entities = list(entity_to_rows.keys())
    n_entities = len(unique_entities)

    if n_entities < 2:
        # Fallback if too few clusters
        flat_s = [s for r in scores_by_row.values() for s in r]
        flat_l = [l for r in labels_by_row.values() for l in r]
        base_ap = compute_average_precision(flat_s, flat_l)
        return base_ap, base_ap, base_ap

    boot_aps = []

    for _ in range(n_bootstraps):
        sampled_entities = [rng.choice(unique_entities) for _ in range(n_entities)]
        boot_scores = []
        boot_labels = []

        for ent in sampled_entities:
            for r in entity_to_rows[ent]:
                boot_scores.extend(scores_by_row.get(r, []))
                boot_labels.extend(labels_by_row.get(r, []))

        ap = compute_average_precision(boot_scores, boot_labels)
        boot_aps.append(ap)

    boot_aps.sort()
    lower_idx = int(0.025 * len(boot_aps))
    upper_idx = int(0.975 * len(boot_aps))
    mean_ap = sum(boot_aps) / len(boot_aps)

    return mean_ap, boot_aps[lower_idx], boot_aps[min(upper_idx, len(boot_aps) - 1)]

def evaluate_cell_scores(
    cell_scores: List[CellScore],
    ground_truth_errors: List[List[int]],
    entity_ids: List[str],
    numeric_col_indices: Sequence[int],
    rare_valid_mask: Optional[List[List[bool]]] = None
) -> Dict[str, Any]:
    """Evaluate full cell predictions against isolated ground truth."""
    eligible_scores: List[float] = []
    eligible_labels: List[int] = []

    num_scores: List[float] = []
    num_labels: List[int] = []

    cat_scores: List[float] = []
    cat_labels: List[int] = []

    scores_by_row: Dict[int, List[float]] = {}
    labels_by_row: Dict[int, List[int]] = {}
    entity_to_rows: Dict[str, List[int]] = {}

    for r, ent in enumerate(entity_ids):
        entity_to_rows.setdefault(ent, []).append(r)
        scores_by_row[r] = []
        labels_by_row[r] = []

    rare_valid_scores: List[float] = []

    for cs in cell_scores:
        if not cs.is_eligible:
            continue

        true_label = ground_truth_errors[cs.row_idx][cs.col_idx]
        score = cs.score

        eligible_scores.append(score)
        eligible_labels.append(true_label)

        scores_by_row[cs.row_idx].append(score)
        labels_by_row[cs.row_idx].append(true_label)

        if cs.col_idx in numeric_col_indices:
            num_scores.append(score)
            num_labels.append(true_label)
        else:
            cat_scores.append(score)
            cat_labels.append(true_label)

        if rare_valid_mask and rare_valid_mask[cs.row_idx][cs.col_idx]:
            rare_valid_scores.append(score)

    # 1. Primary AUPRC
    overall_auprc = compute_average_precision(eligible_scores, eligible_labels)
    numeric_auprc = compute_average_precision(num_scores, num_labels)
    categorical_auprc = compute_average_precision(cat_scores, cat_labels)

    # 2. Cluster Bootstrap CI
    mean_ap, ci_lower, ci_upper = cluster_bootstrap_auprc_ci(
        scores_by_row, labels_by_row, entity_to_rows, n_bootstraps=100
    )

    # 3. Budgeted Metrics (k = 1%, 5%, 10% of eligible cells)
    total_eligible = len(eligible_scores)
    budgets = {
        "k_01": max(int(0.01 * total_eligible), 1),
        "k_05": max(int(0.05 * total_eligible), 1),
        "k_10": max(int(0.10 * total_eligible), 1)
    }

    budgeted_results = {}
    positives = sum(eligible_labels)
    sorted_idx = sorted(range(total_eligible), key=lambda i: -eligible_scores[i])

    for b_key, b_size in budgets.items():
        top_k = sorted_idx[:b_size]
        tp = sum(eligible_labels[i] for i in top_k)
        prec = tp / b_size if b_size else 0.0
        rec = tp / positives if positives else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        budgeted_results[b_key] = {
            "budget": b_size,
            "true_positives": tp,
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4)
        }

    # 4. Rare-valid false positive alarm rate (fraction of rare-valid cells in top 5% audit budget)
    rare_valid_fpr = 0.0
    if rare_valid_scores and total_eligible > 0:
        threshold_top5 = eligible_scores[sorted_idx[budgets["k_05"] - 1]]
        alarms_on_rare = sum(1 for s in rare_valid_scores if s >= threshold_top5)
        rare_valid_fpr = alarms_on_rare / len(rare_valid_scores)

    return {
        "eligible_cells": total_eligible,
        "true_error_positives": positives,
        "overall_auprc": round(overall_auprc, 4),
        "numeric_auprc": round(numeric_auprc, 4),
        "categorical_auprc": round(categorical_auprc, 4),
        "auprc_95_ci": [round(ci_lower, 4), round(ci_upper, 4)],
        "budgeted_metrics": budgeted_results,
        "rare_valid_fpr_at_k05": round(rare_valid_fpr, 4)
    }
