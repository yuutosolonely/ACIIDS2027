"""CRIC-ED: Contamination-Resilient In-Context Likelihood Scorer.

Adheres strictly to the frozen protocol in prereg/PREREGISTRATION.md:
- Leave-Entity-Out (LEO) Cross-Fitting
- Target Column Masking
- Paired Context Interventions (none vs matched_random vs influence)
- Rare-Valid Pattern Preservation Guardrails
"""

from __future__ import annotations

import math
import random
from typing import Any, Dict, List, Optional, Sequence, Set
from cric_ed.models import CellScore, DirtyTable
from cric_ed.protocol import group_folds

class CRICDetector:
    """Contamination-Resilient In-Context Likelihood Detector."""

    def __init__(
        self,
        context_size: int = 40,
        trim_ratio: float = 0.15,
        trimming_mode: str = "influence",  # "none", "matched_random", "influence"
        n_splits: int = 5,
        seed: int = 42,
        clip_max: float = 25.0,
        rare_valid_patterns: Optional[Dict[str, Set[Any]]] = None
    ):
        if trimming_mode not in ("none", "matched_random", "influence"):
            raise ValueError(f"Unknown trimming_mode: {trimming_mode}")
        self.context_size = context_size
        self.trim_ratio = trim_ratio
        self.trimming_mode = trimming_mode
        self.n_splits = n_splits
        self.seed = seed
        self.clip_max = clip_max
        self.rare_valid_patterns = rare_valid_patterns or {}
        self.rng = random.Random(seed)

    def _compute_row_distance(
        self,
        row_a: List[Any],
        row_b: List[Any],
        target_col: int,
        numeric_cols: Set[int],
        ignored_cols: Optional[Set[int]] = None
    ) -> float:
        """Compute conditioning feature distance excluding target column and ignored keys."""
        skip_cols = {target_col}
        if ignored_cols:
            skip_cols.update(ignored_cols)

        dist_sq = 0.0
        n_feats = 0
        for c in range(len(row_a)):
            if c in skip_cols:
                continue
            va, vb = row_a[c], row_b[c]
            if c in numeric_cols:
                try:
                    fa, fb = float(va), float(vb)
                    diff = fa - fb
                    dist_sq += diff * diff
                    n_feats += 1
                except (ValueError, TypeError):
                    dist_sq += 4.0
                    n_feats += 1
            else:
                # Hamming distance for categorical
                dist_sq += 0.0 if str(va) == str(vb) else 2.0
                n_feats += 1

        return math.sqrt(dist_sq / max(n_feats, 1))

    def _apply_trimming(
        self,
        context_indices: Sequence[int],
        query_row: List[Any],
        target_col: int,
        table: DirtyTable,
        col_name: str
    ) -> List[int]:
        """Apply context intervention based on designated mode."""
        if len(context_indices) <= 5 or self.trimming_mode == "none":
            return list(context_indices)

        n_trim = int(len(context_indices) * self.trim_ratio)
        if n_trim <= 0:
            return list(context_indices)

        if self.trimming_mode == "matched_random":
            # Matched random removal: remove n_trim uniformly at random
            sample_pool = list(context_indices)
            self.rng.shuffle(sample_pool)
            return sample_pool[:-n_trim]

        # Influence trimming: compute leverage/deviance to query row
        scores_with_idx = []
        rare_vals = self.rare_valid_patterns.get(col_name, set())

        for idx in context_indices:
            c_row = table.rows[idx]
            val = c_row[target_col]

            # Rare-valid guardrail: if context row contains rare-valid pattern, protect it
            is_rare_valid = val in rare_vals or str(val) in rare_vals

            dist = self._compute_row_distance(
                query_row, c_row, target_col, table.numeric_col_indices, table.primary_key_col_indices
            )
            
            # High distance + outlier value = high leverage / potential contamination
            leverage = dist
            scores_with_idx.append((leverage, is_rare_valid, idx))

        # Sort candidate items by leverage descending (highest leverage first)
        # However, rare-valid items are placed at the end to prevent pruning
        sorted_candidates = sorted(scores_with_idx, key=lambda x: (x[1], -x[0]))

        # Prune top non-rare-valid exemplars
        pruned_indices = set()
        for leverage, is_rare, idx in sorted_candidates:
            if not is_rare and len(pruned_indices) < n_trim:
                pruned_indices.add(idx)

        return [idx for idx in context_indices if idx not in pruned_indices]

    def score_table(self, table: DirtyTable) -> List[CellScore]:
        scores: List[CellScore] = []
        n_rows = table.num_rows

        # 1. Establish Leave-Entity-Out cross-fitting folds
        folds = group_folds(table.entity_ids, self.n_splits, self.seed)

        # Precompute eligible and primary keys
        for col_idx, col_name in enumerate(table.headers):
            if col_idx in table.primary_key_col_indices:
                for r in range(n_rows):
                    scores.append(CellScore(
                        row_idx=r,
                        col_idx=col_idx,
                        col_name=col_name,
                        raw_value=table.get_cell(r, col_idx),
                        score=0.0,
                        is_eligible=False
                    ))
                continue

            is_numeric = col_idx in table.numeric_col_indices

            # Score fold by fold to guarantee strict LEO boundary
            for context_pool, query_indices in folds:
                for q_idx in query_indices:
                    q_row = table.rows[q_idx]
                    q_val = q_row[col_idx]

                    # Sample base context from candidate context pool
                    if len(context_pool) <= self.context_size:
                        base_context = list(context_pool)
                    else:
                        base_context = self.rng.sample(context_pool, self.context_size)

                    # Apply context intervention / trimming
                    active_context = self._apply_trimming(base_context, q_row, col_idx, table, col_name)

                    # Calculate In-Context Conditional Likelihood
                    if is_numeric:
                        # Numeric conditional density
                        nums: List[float] = []
                        weights: List[float] = []
                        for c_idx in active_context:
                            try:
                                cv = float(table.get_cell(c_idx, col_idx))
                                if math.isfinite(cv):
                                    d = self._compute_row_distance(
                                        q_row, table.rows[c_idx], col_idx, table.numeric_col_indices, table.primary_key_col_indices
                                    )
                                    w = math.exp(-0.5 * d)
                                    nums.append(cv)
                                    weights.append(w)
                            except (ValueError, TypeError):
                                pass

                        try:
                            q_num = float(q_val)
                            if not math.isfinite(q_num):
                                raise ValueError("Nonfinite query")

                            if not nums or sum(weights) < 1e-6:
                                cell_score = self.clip_max
                                failure = True
                            else:
                                total_w = sum(weights)
                                weighted_mean = sum(n * w for n, w in zip(nums, weights)) / total_w
                                var = sum(w * ((n - weighted_mean) ** 2) for n, w in zip(nums, weights)) / total_w
                                std = math.sqrt(max(var, 1e-4))
                                z = abs(q_num - weighted_mean) / std
                                # Continuous negative log density proxy
                                cell_score = min(float(z), self.clip_max)
                                failure = False

                        except (ValueError, TypeError):
                            cell_score = self.clip_max
                            failure = True

                    else:
                        # Categorical in-context conditional frequency
                        counts: Dict[str, float] = {}
                        total_w = 0.0
                        for c_idx in active_context:
                            cv = str(table.get_cell(c_idx, col_idx))
                            d = self._compute_row_distance(
                                q_row, table.rows[c_idx], col_idx, table.numeric_col_indices, table.primary_key_col_indices
                            )
                            w = math.exp(-0.5 * d)
                            counts[cv] = counts.get(cv, 0.0) + w
                            total_w += w

                        q_str = str(q_val)
                        # Laplace smoothing with |V| ~ counts size + 1
                        vocab_size = max(len(counts) + 1, 2)
                        matched_w = counts.get(q_str, 0.0)
                        prob = (matched_w + 1.0) / (total_w + vocab_size)
                        nll = -math.log(max(prob, 1e-8))
                        cell_score = min(nll, self.clip_max)
                        failure = False

                    scores.append(CellScore(
                        row_idx=q_idx,
                        col_idx=col_idx,
                        col_name=col_name,
                        raw_value=q_val,
                        score=cell_score,
                        is_eligible=True,
                        failure_status=failure,
                        details={"trimming_mode": self.trimming_mode, "active_context_size": len(active_context)}
                    ))

        return scores
