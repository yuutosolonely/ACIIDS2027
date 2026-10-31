# Preregistration v2 — CRIC-ED with a real tabular foundation model (Path A)

Status: **FROZEN** when its SHA-256 is recorded in `docs/EXPERIMENT_LOG.md` §6 before any
confirmatory run. Version 1 (`prereg/PREREGISTRATION.md`) is unchanged and remains the record
of the original plan; §9 lists every departure from it.

Author decisions: 2026-10-30 NO-GO for ACIIDS 2027; Path A (keep the TFM question with
TabPFN v2) for the next phase (`docs/DECISION_BRIEF_20261030.md`).

## 1. Research questions and hypotheses

Task: unsupervised cell-level error detection; each eligible cell receives a suspicion score;
labels are used only for evaluation and for the labelled oracle diagnostic.

- **RQ1 (TFM vs. non-TFM conditional model and label-free baselines).** H1: on the same
  cross-fitting protocol and contexts, TabPFN-v2 conditional scoring (`TFM-raw`) attains higher
  cell-level AUPRC than the same pipeline with LightGBM (`LGBM-raw`).
- **RQ2 (self-contamination).** H2a: scoring with clean context values (`oracle`, diagnostic)
  yields higher AUPRC than dirty context (`raw`) — the contamination gap is positive. H2b: the
  gap is larger under systematic (repeated) errors than under random errors.
- **RQ3 (cell-level self-purification).** H3 (primary endpoint): removing from each column's
  context the 15% of rows whose target cell scored most suspicious in pass 1 (`purify`) yields
  higher AUPRC than removing the same number of rows uniformly at random from the same base
  context (`random`). Secondary: `purify` vs `raw`; rare-valid false alarms of `purify` vs `raw`.

## 2. Data (RAHA, upstream commit `7be1334b8c7bbdac3f47ef514fb3e1e8c5fc181c`, Apache-2.0)

Hashes: `data/manifests/raha_download_20261030.json`.

| Role | Tables |
|---|---|
| Development (design, debugging, timing; no confirmatory claims) | `movies_1` |
| Confirmatory | `hospital`, `flights`, `beers`, `rayyan` |

- Row cap 1,000: `hospital` and `rayyan` used in full; `flights` and `beers` subsampled once
  with `numpy.random.default_rng(0).choice(n, 1000, replace=False)` (same rows for dirty/clean).
- Eligible cells: all cells except row-identifier columns (name in {id, index, tuple_id} and
  unique per row). Errors: dirty value ≠ clean value (string comparison).
- Conditions per confirmatory table:
  - `real`: the RAHA dirty table with its real errors;
  - `inj-random`, `inj-systematic`: the clean table with 10% of eligible cells corrupted by
    `cric_ed.benchmark.inject` (types typo, replace, missing, format, scale, uniform;
    `systematic` = repeated templates mapping 30–80% of one value's occurrences to the same
    wrong value). Injection seed = run seed.
- Disclosure: descriptive error profiles (per-column error rates and two example pairs per
  column) of all five tables were viewed on 2026-10-30 before this protocol. Design choices in
  §3 were made on `movies_1` only. No detector has been run on a confirmatory table.

## 3. Scoring (implementation: `src/cric_ed/conditional.py`, `src/cric_ed/baselines.py`)

- Column typing on the observed table: numeric if ≥80% of non-empty values parse as numbers;
  otherwise categorical; categorical with unique ratio > 0.5 is **unsupported** (score 0 for
  every cell, kept in the denominator; coverage reported).
- Features for column j: all other eligible columns; numeric → float (NaN if not parseable),
  categorical → frequency-rank code fitted on the observed table (label-free, transductive).
- Scores are negative log probabilities: numeric parseable → −log P(parseable) − log(two-sided
  predictive tail probability, floor 1e−12); numeric non-parseable token → −log P(non-parseable)
  − log smoothed token frequency; categorical → −log((n·p̃(v) + q0)/(n + 1)), q0 = 1/(|V|+1),
  with top-9 classes + OTHER when |V| > 10 (OTHER mass split by smoothed within-OTHER counts).
- Cross-fitting: K = 5 row folds (permutation seeded by the run seed). For each fold a base
  context of at most C = 512 rows is drawn from the other folds and shared by all columns,
  arms and models for that seed.
- Arms: `raw`; `random` (q = 0.15 of base removed uniformly, stream `[seed, fold, column, 7919]`);
  `purify` (q = 0.15 of base with the highest `raw` score in the target column removed; ties by
  row index; pass 1 = the same model's `raw` run with the same seed); diagnostics `oracle`
  (clean values for context rows) and `leaky` (base ∪ query fold; `real` condition only).
- Models: TabPFN v2 (`tabpfn==9.2.0`, checkpoints pinned in
  `data/manifests/tabpfn_v2_checkpoints_20261030.json`, `n_estimators = 1`, CPU, random_state =
  seed); LightGBM 4.6.0 (100 trees, 15 leaves, min_child_samples 5; regression tail from a
  Gaussian with 3-fold CV residual s.d.).
- Label-free baselines: VF, PF, RobustZ, ColumnIF (Isolation Forest per column, 100 trees),
  DDCcore (simplified re-implementation; §9).
- Seeds: 0, 1, 2, 3, 4 for every table × condition × arm × model.

## 4. Metrics and analysis (script frozen with this file: `experiments/tfm/analyze_v2.py`)

- Primary metric: cell-level AUPRC = scikit-learn `average_precision_score` over all eligible
  cells (ties grouped).
- Secondary: R-precision (budget = number of errors), precision at 1% and 5% of cells,
  rare-valid alarm rate (share of correct cells whose clean value has marginal frequency ≤1%,
  in columns with unique ratio ≤0.5, that fall in the R-precision budget), coverage (share of
  cells in supported columns; share of errors in supported columns).
- Unit of analysis: a *dataset-condition* (4 tables × 3 conditions = 12 units). Per unit the
  arm/model value is the mean over 5 seeds. Uncertainty: row-cluster bootstrap (1,000
  resamples of rows, the same resampled rows applied to every seed), 95% percentile interval of
  the seed-averaged paired difference.
- Decision rules (one-sided, α = 0.05):
  - **H3 supported** iff the Wilcoxon signed-rank test over the 12 units of
    Δ = AUPRC(purify) − AUPRC(random) gives p < 0.05 **and** the bootstrap interval excludes 0
    with Δ > 0 in at least 8 of 12 units. Otherwise "not supported"; if the median Δ < 0,
    "reversed".
  - **H1** same rule with Δ = AUPRC(TFM-raw) − AUPRC(LGBM-raw).
  - **H2a** same rule with Δ = AUPRC(oracle) − AUPRC(raw) for TFM. **H2b** descriptive: gap
    under `inj-systematic` minus gap under `inj-random`, per table (4 units, no test).
  - Holm correction across H1, H2a, H3 reported alongside the raw p-values.
- Secondary analyses (labelled exploratory): excluding columns whose error rate exceeds 50%
  (`real` only); supported-columns-only; TFM vs each baseline; per-type recall; leaky gap.

## 5. Stopping, failures and reporting

- All units, seeds and failed runs are reported. A model failure on a column is recorded and
  its cells receive the preregistered coverage penalty (max finite score + 1.0) for that arm.
- If H3 is not supported, the purification claim is withdrawn and reported as a negative result;
  the framing is not changed post hoc.
- No result may be described as a benchmark ranking of published systems; Raha/Baran/ZeroED
  operate in different supervision regimes and are not re-run.

## 6. Compute and environment

CPU only (12 threads; GPU present but unused), isolated environment `.venv-tfm`
(`experiments/tfm_env_freeze.txt`), $0. Wall-clock time per arm is logged.

## 9. Deviations from version 1 (decided before confirmatory data access)

| Item | Version 1 | Version 2 | Reason |
|---|---|---|---|
| Cross-fitting unit | leave-entity-out | row folds (K=5) | Error detection may legitimately use other records of the same entity; only the query cell's row is excluded. Entity keys are not defined for all tables |
| Influence score | likelihood-gradient norm or LOO variance per query | pass-1 target-cell suspicion per column context | TabPFN fits one context per fold; per-query context editing is infeasible |
| Rare-valid guard | protect values with ≤1% frequency | none (rare-valid alarms are measured instead) | The v1 pilot needed an oracle list; a frequency guard would also protect typos |
| Baselines | DDC, column IF, CDC, uTabPFN | DDCcore (re-implementation), ColumnIF, LightGBM conditional (CDC-inspired, not CDC), TFM-raw (plays the uTabPFN-style role) + VF, PF, RobustZ | No R; CDC code not integrated |
| Context size | {32,…,512} ablation | C = 512 fixed | Compute |
| TabPFN ensemble | default | n_estimators = 1 | CPU time |
| Bootstrap unit | row entities | rows | No common entity key |
| Data | RAHA 4 tables, full | 4 tables, ≤1,000 rows; + controlled injection | TabPFN CPU limit; RQ2 needs known contamination structure |
