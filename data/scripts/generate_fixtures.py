#!/usr/bin/env python3
"""Generate deterministic offline synthetic fixtures for CRIC-ED unit and smoke tests.

Zero-cost, offline, reproducible fixture generator strictly adhering to authorization limits.
"""

from __future__ import annotations

import csv
from pathlib import Path
import random

def generate_toy_fixture(out_dir: Path, seed: int = 42) -> None:
    random.seed(seed)
    out_dir.mkdir(parents=True, exist_ok=True)

    header = ["entity_id", "feature_a", "feature_b", "category_c", "num_target"]
    n_rows = 100

    clean_rows = []
    dirty_rows = []
    error_mask = []

    categories = ["Alpha", "Beta", "Gamma", "RareDelta"]

    for i in range(n_rows):
        entity = f"ent_{i // 5}"  # group of 5 rows per entity
        fa = round(random.gauss(10.0, 2.0), 3)
        fb = round(fa * 1.5 + random.gauss(0.0, 0.5), 3)
        # Category C: RareDelta is rare valid (3% frequency)
        cat = "RareDelta" if (i % 30 == 0) else random.choice(categories[:3])
        num = round(fa * 2.0 + (5.0 if cat == "Beta" else 1.0), 3)

        c_row = [entity, fa, fb, cat, num]
        d_row = list(c_row)
        err = [0, 0, 0, 0, 0]

        # Inject controlled errors into ~10% of cells (excluding entity_id)
        if random.random() < 0.12 and i % 7 == 0:
            # Numeric extreme error / typo
            d_row[1] = round(fa * 10.0, 3)
            err[1] = 1
        if random.random() < 0.10 and i % 5 == 0:
            # Categorical corruption
            d_row[3] = "CorruptedCategory"
            err[3] = 1
        if random.random() < 0.12 and i % 4 == 0:
            # Swapped / inverted numeric target
            d_row[4] = round(-abs(num), 3)
            err[4] = 1

        clean_rows.append(c_row)
        dirty_rows.append(d_row)
        error_mask.append(err)

    # Write clean.csv
    with open(out_dir / "clean.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(clean_rows)

    # Write dirty.csv
    with open(out_dir / "dirty.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(dirty_rows)

    # Write errors.csv
    with open(out_dir / "errors.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(error_mask)

    print(f"Generated synthetic fixture at: {out_dir}")

if __name__ == "__main__":
    target = Path(__file__).resolve().parent.parent / "fixtures" / "toy_mixed"
    generate_toy_fixture(target)
