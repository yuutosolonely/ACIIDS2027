# Reproducibility Protocol & Artifact Checklist — ACIIDS 2027

**Worker:** W2-CONF (Conference & Reproducibility Specialist)  
**Target:** CRIC-ED / Idea 3 Reproducibility Verification  
**Standard:** ACM / IEEE / Springer Reproducibility & Replication Guidelines  

---

## 1. Reproducibility Standard (Tenets)

1. **Deterministic Execution:**
   - All random seeds for context sampling, cross-fitting row splitting, and synthetic perturbations are explicitly fixed and recorded (`seeds = [42, 1337, 2026, 7, 99]`).
2. **Deterministic Code Environment:**
   - Package dependencies locked via `uv.lock` with Python 3.12+.
   - System environment checkable via `tools/check_setup.py`.
3. **Artifact Provenance & Audit Trail:**
   - Every experimental run must emit a self-contained directory under `experiments/runs/<run_id>/` containing:
     - `config.json`: All hyperparameters, seeds, dataset hashes, model revisions.
     - `raw_predictions.csv`: Coordinate-wise outputs `(row_id, col_name, ground_truth_label, raw_score, is_eligible)`.
     - `metrics.json`: Evaluated metrics (AUPRC, P@k, R@k, F1@k, coverage denominator, elapsed runtime).
     - `system_info.json`: Hardware, CPU/RAM, OS, git commit SHA.

---

## 2. Evaluation Universe & Coverage Accounting

- **No Silent Cell Dropping:**
  - Evaluated cells denominator $M$ must equal the total eligible cells in the evaluation universe:
    $$M = N_{\text{eval}} \times D_{\text{eval}}$$
  - If a column is unsupported (e.g. arbitrary long text or unstructured timestamps), it must be explicitly declared before evaluation.
  - If an algorithm fails to produce a prediction for cell $(i,j)$ (e.g. NaN likelihood or out-of-vocabulary class), the system records `failure_status = 1`. In the confirmatory analysis, failed cells are penalized with the default worst-case score (highest anomaly score), NOT omitted from the denominator.

---

## 3. Statistical Analysis Protocol

- **Independent Resampling Units:**
  - Tabular rows within an entity cluster (e.g. repeated hospital admissions or flights of the same airline) are not IID.
  - 95% Confidence Intervals are calculated via **Cluster-Preserving Bootstrap** (resampling rows or entity clusters 1,000 times), rather than naive cellwise bootstrap.
- **Hypothesis Testing:**
  - Paired Wilcoxon signed-rank test across datasets between CRIC-ED and each competitor baseline.

---

## 4. Open-Science Code Release Package Structure

```text
├── src/cric_ed/           # Core algorithmic package
│   ├── protocol.py        # Group cross-fitting & leakage boundary logic
│   ├── adapters/          # TFM and baseline interfaces
│   ├── detectors/         # CRIC-ED influence-aware scorer
│   └── evaluation/        # Metrics and cluster-bootstrap evaluator
├── data/
│   ├── DATA_CARD.md       # License, provenance, split metadata
│   └── manifests/         # Locked JSON manifests of benchmark tables
├── prereg/
│   └── PREREGISTRATION.md # Protocol frozen before confirmatory runs
├── experiments/
│   ├── run_pilot.py       # Pilot verification script
│   ├── run_benchmark.py   # Confirmatory benchmark harness
│   └── runs/              # Raw output run artifacts
├── paper/                 # LaTeX sources and deterministic figure scripts
└── tools/                 # Setup and verification utilities
```
