"""Classical Tier 1 baselines for coordinate-wise tabular error detection."""

from __future__ import annotations

import math
from typing import List
from cric_ed.models import CellScore, DirtyTable

class RobustCoordinateDevianceDetector:
    """Robust Coordinate-Wise Deviance Detector (DDC proxy using MAD).
    
    Operates strictly within training-free information boundaries.
    For numerical columns: computes median and Median Absolute Deviation (MAD).
    For categorical columns: computes marginal negative log frequency.
    """

    def __init__(self, clip_max: float = 20.0):
        self.clip_max = clip_max

    def score_table(self, table: DirtyTable) -> List[CellScore]:
        scores: List[CellScore] = []
        n_rows = table.num_rows

        for col_idx, col_name in enumerate(table.headers):
            if col_idx in table.primary_key_col_indices:
                # Primary keys are excluded from eligible evaluation universe
                for row_idx in range(n_rows):
                    scores.append(CellScore(
                        row_idx=row_idx,
                        col_idx=col_idx,
                        col_name=col_name,
                        raw_value=table.get_cell(row_idx, col_idx),
                        score=0.0,
                        is_eligible=False
                    ))
                continue

            col_values = [table.get_cell(r, col_idx) for r in range(n_rows)]

            if col_idx in table.numeric_col_indices:
                # Convert valid numbers
                nums: List[float] = []
                valid_indices: List[int] = []
                for r, v in enumerate(col_values):
                    try:
                        val = float(v)
                        if math.isfinite(val):
                            nums.append(val)
                            valid_indices.append(r)
                    except (ValueError, TypeError):
                        pass

                if len(nums) < 3:
                    # Fallback if too few numeric values
                    med = 0.0
                    mad = 1.0
                else:
                    sorted_nums = sorted(nums)
                    med = sorted_nums[len(sorted_nums) // 2]
                    abs_diffs = sorted([abs(x - med) for x in nums])
                    mad = abs_diffs[len(abs_diffs) // 2]
                    if mad < 1e-6:
                        # Mean absolute deviation fallback
                        mad = (sum(abs_diffs) / len(abs_diffs)) or 1e-3

                # Standard normal consistency constant 1.4826
                norm_scale = 1.4826 * mad

                for r in range(n_rows):
                    v = col_values[r]
                    try:
                        val = float(v)
                        if math.isfinite(val):
                            z = abs(val - med) / norm_scale
                            s = min(float(z), self.clip_max)
                            failure = False
                        else:
                            s = self.clip_max
                            failure = True
                    except (ValueError, TypeError):
                        # Non-parseable string in numeric column is an extreme error
                        s = self.clip_max
                        failure = True

                    scores.append(CellScore(
                        row_idx=r,
                        col_idx=col_idx,
                        col_name=col_name,
                        raw_value=v,
                        score=s,
                        is_eligible=True,
                        failure_status=failure
                    ))

            else:
                # Categorical column: empirical negative log frequency
                counts = {}
                for v in col_values:
                    sv = str(v)
                    counts[sv] = counts.get(sv, 0) + 1

                total = len(col_values)
                for r in range(n_rows):
                    v = str(col_values[r])
                    freq = counts.get(v, 1) / total
                    nll = -math.log(max(freq, 1e-6))
                    scores.append(CellScore(
                        row_idx=r,
                        col_idx=col_idx,
                        col_name=col_name,
                        raw_value=col_values[r],
                        score=min(nll, self.clip_max),
                        is_eligible=True,
                        failure_status=False
                    ))

        return scores
