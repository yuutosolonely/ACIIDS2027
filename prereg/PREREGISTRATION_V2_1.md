# Preregistration v2.1 — CRIC-ED with TabPFN-2 (Path A)

Status: CANDIDATE - becomes FROZEN only when its hash is recorded by the coordinator

Date: 2026-10-30. This amendment preserves v1 (`prereg/PREREGISTRATION.md`) and v2
(`prereg/PREREGISTRATION_V2.md`) as historical records. Authority is the Path A decision
and the four accepted amendment decisions in `docs/DECISION_BRIEF_20261030.md`, as
operationalized by task T2 in `docs/handoffs/TASKS_CODEX_V2_1_20261030.md`. The proposal
`docs/proposals/V2_AMENDMENT_20261030.md` applies only where consistent with those decisions;
its recommended strict group/inductive primary boundary was not adopted. The author chose
NO-GO for the ACIIDS deadline of 31 October 2026. This document authorizes no submission,
publication, paid service, new download, or confirmatory execution before freeze.

This is a prospective specification, not a report of detector results. Implementation
reconciliation and the freeze procedure in §10 remain prerequisites for confirmatory work.

## 1. Questions, estimands and scope of claims

The task is unsupervised **cell-level error detection**. For an observed table, the detector
returns a suspicion score for every eligible cell, with larger scores more suspicious.
Clean values and error labels are reserved for evaluation, construction of injected inputs,
and the explicitly labelled oracle diagnostic. They do not inform deployment arms,
hyperparameters, context selection, column eligibility, or entity-key choice.

- **RQ3, primary (purification):** How does targeted removal compare with random removal of
  the same number of context rows for TabPFN-2 on each real-error table?
- **RQ1, secondary (conditional model):** How does TabPFN-2 compare with LightGBM under the
  same row folds, base contexts and scoring pipeline?
- **RQ2, secondary (contamination):** What is the clean-context oracle gap, and how does it
  differ between random and systematic injection?
- **Boundary and cost questions, secondary:** How do purification versus raw context,
  leave-entity-out versus row-level raw scoring, and LightGBM purification versus random
  removal behave? What incremental compute is required by nested purification?

Let `AP(t,c,s,m,a)` be cell-level average precision for source table `t`, condition `c`, run
seed `s`, model `m` and arm `a`, on that run's complete fixed eligible-cell universe. The
**primary estimand for each real table** is

`Delta_t = (1/5) * sum_{s=0}^4 [AP(t,real,s,tabpfn-v2,purify) - AP(t,real,s,tabpfn-v2,random)]`.

Compute average precision separately for each seed, then average paired differences; do
not average scores before computing AP. Positive differences favor purification, without
constituting a binary cross-dataset superiority decision. The target is the named capped
benchmark tables under the declared algorithm and seeds, not a population of unseen tables.

The following seed-averaged paired contrasts are secondary, reported per table and condition
where the arms are defined:

1. `tabpfn-v2__raw - lgbm__raw` (TFM versus non-TFM conditional model).
2. `tabpfn-v2__oracle - tabpfn-v2__raw` (clean-context gap; diagnostic, not a guaranteed upper
   bound). LightGBM oracle gaps may also be described with the model identified.
3. `tabpfn-v2__purify - tabpfn-v2__raw`.
4. `raw_leo - raw`, for each model on the keyed real tables only (§5).
5. `lgbm__purify - lgbm__random`.

`inj-random` and `inj-systematic` are **mechanism probes**, separate from the primary real-error
estimand. Report purification contrasts and oracle gaps for each probe and table; describe
the systematic-minus-random oracle-gap difference without treating conditions as independent
datasets. `leaky - raw` is a labelled leakage diagnostic on real conditions only.

## 2. Data roles, access disclosure and evaluation universe

The data source is the local RAHA snapshot, upstream commit
`7be1334b8c7bbdac3f47ef514fb3e1e8c5fc181c`; input identities and the recorded Apache-2.0
license are in `data/manifests/raha_download_20261030.json`. Do not substitute upstream
updates. Verify the manifest's dirty/clean hashes before execution.

- **Development:** `movies_1` only, for design, debugging and timing. Development artifacts
  cannot enter confirmatory analysis.
- **Confirmatory:** `hospital`, `flights`, `beers`, `rayyan`; each has `real`, `inj-random`
  and `inj-systematic` conditions and run seeds `0, 1, 2, 3, 4`. Both models are required for
  each table-condition-seed run. No table, condition or seed may be omitted selectively.
- **Access disclosure:** Descriptive error profiles of all five tables (per-column error
  rates and two dirty/clean example pairs per column) were viewed on 2026-10-30 before this
  amendment. Detectors have been run only on `movies_1` and the synthetic fixture. These
  confirmatory tables are therefore not wholly unseen with respect to descriptive error
  information. Synthetic fixtures provide software validation only.

Read CSV values as strings, retaining empty strings. Align clean headers to observed headers
by column order only when shapes agree, as in `benchmark.load_real`; do not repair values.
Eligibility is determined on the source observed real table before subsampling or injection:
exclude a column only if its lowercased name is in `{id, index, tuple_id}` and it is unique
per row. All remaining cells are eligible, including unsupported columns. Real errors are
exact dirty-versus-clean string differences, including representation differences.

Apply a **1,000-row cap before injection**. Keep all rows when `n <= 1000` (`hospital` and
`rayyan`); otherwise select once using
`np.sort(np.random.default_rng(0).choice(n, 1000, replace=False))` (`flights` and `beers`).
Use identical source row IDs for dirty and clean, all arms/models, all conditions and all
run seeds. Record the ordered source IDs, eligible column order and input hashes; never
resample the table to improve performance. The fixed eligible universe is the capped rows
times the eligible columns. Within each seed, all comparisons use the same errors and rows.

Observed-only typing/support follows §4 and may vary with injected inputs. The rule is
fixed, not tuned by error rates; retain all eligible cells regardless of its outcome and
record column specifications per run.

## 3. Injection and random streams

For each capped table, create injected conditions from its **clean** table, replacing real
errors with controlled corruption. `benchmark.inject` targets
`round(0.10 * n_rows * n_eligible_columns)` distinct eligible cells. The five error types
are `typo`, `replace`, `missing`, `format`, `scale`, with type drawn uniformly per attempted
corruption; **uniform is a sampling rule, not a sixth error type**. Non-applicable or
unchanged proposals are rejected, so realized type proportions need not be uniform.

- `inj-random`: select a column and row randomly, then attempt its sampled corruption;
  do not corrupt an already selected cell twice.
- `inj-systematic`: choose a column and clean value and map a sampled share (uniform in
  `[0.3, 0.8)`) of its remaining occurrences to the **same** wrong value. Templates require
  at least two available occurrences; the final remainder can be smaller. Cap selections
  at the remaining corruption budget.

Typos edit characters; replacement uses another value from the column domain; missingness
uses the empty string; format changes representation; scale multiplies parseable numbers
by 10, 100 or 0.1. These are code-defined string corruptions, not human adjudications of
semantic invalidity. The injection loop stops on attaining its target or its fixed attempt
guard (`target * 50`). Report realized corruption counts/rates and any shortfall; do not
silently regenerate to force a preferred profile.

**Injection seed = run seed**, using `default_rng(seed)`. Outer row folds and base-context
sampling also use that integer seed. Injection and context randomness are therefore coupled
by design, not an independent factorial experiment. The real table's error mask stays fixed
across seeds; injected masks can differ across seeds. Subsampling always uses seed 0.
Nested pass-1 uses the same run seed within each outer training pool. Random removal uses
its separate deterministic stream `default_rng([seed, fold, column, 7919])`, independent of
pass-1 ranks. Model `random_state = seed`. Bootstrap uses seed 2027 (§7).

## 4. Scoring semantics and preprocessing boundary

The conditional implementations are `src/cric_ed/conditional.py` and
`src/cric_ed/baselines.py`. A target column is numeric when at least 80% of its nonempty
observed values parse as finite numbers under the declared parser. Otherwise it is
categorical, except a categorical column with observed unique ratio `> 0.5`, which is
**unsupported**. Unsupported target cells receive score **0**, remain in the evaluation
denominator and have their counts/coverage reported. This rule does not exclude near-unique
numeric columns. Unsupported columns may still be conditioning features.

For target column `j`, remove `j` from the feature matrix. Encode numeric features as floats
(unparseable values become NaN); encode other features by observed frequency-rank codes,
with an unknown code for values absent from the encoder fit. The **final-pass** column typing
and encoding use the entire observed table, including outer query rows: this is a label-free
**transductive** preprocessing assumption inherited from v2, not a fully inductive protocol.
The model's fitted contexts exclude the query fold except in `leaky`. No clean values are
used to fit the encoder. Nested pass-1 typing and encoding use only the outer training pool;
its inner preprocessing is transductive within that pool. Thus outer query rows cannot
influence pass-1 scores or trimming. The strict context-only preprocessing recommendation
in the amendment proposal is not silently adopted here.

Conditional scores are negative log probabilities, with numerical semantics stated precisely:

- For a parseable numeric query, use `-log P(parseable) - log(max(tail, 1e-12))`.
  `P(parseable) = (n_parseable + 0.5)/(n_context + 1)`. The model's numerical term is the
  **two-sided predictive tail probability** `2 * min(F(y), 1-F(y))`, **not a density** and not
  a claim that numeric and categorical outputs are calibrated identically. With fewer than
  10 parseable context values or no numeric range, use the declared exact-match fallback
  `(count(y) + 0.5)/(n_parseable + 1)` in place of the predictive tail.
- For a nonparseable token in a numeric column, use `-log P(nonparseable) - log P(token |
  nonparseable)`, with `P(nonparseable) = (n_nonparseable + 0.5)/(n_context + 1)` and
  token probability `(count(token) + 0.5)/(n_nonparseable + 0.5 * (V_nonparseable + 1))`.
- For categorical context vocabulary size `V` and `n = n_context`, use
  `-log((n * p_tilde(value) + 1/(V+1))/(n+1))`. For `V <= 10`, predict its observed classes;
  for `V > 10`, predict the **top-9 + OTHER**. Count ties follow the code's stable ordering
  of the sorted vocabulary. Split OTHER mass by within-OTHER smoothed frequencies
  `(count(value)+0.5)/(n_OTHER+0.5*(V_OTHER+1))`, including unseen values. Without an OTHER
  class an unseen value has model probability zero before smoothing. A one-class context
  uses unit probability for that class without a classifier fit.

Pool these declared scores over the full eligible universe for the primary metric. Also
report numeric/categorical/support status separately; do not introduce pooled rank
normalization, density terminology for tails, or conformal-validity claims.

## 5. Cross-fitting, context arms and entity keys

Primary outer cross-fitting uses **K = 5 row folds**: seeded row permutation, fold `f` is
the sorted `perm[f::5]`. For each fold, sample without replacement a sorted base context of
size `min(512, size_of_outer_training_pool)` from the other folds, using the same generator
after the permutation. Identical bases are shared across eligible target columns, arms
(except `raw_leo`) and models for the run seed. The query row and its whole outer fold are
absent from fitted contexts; other records of the same entity are permitted primary evidence.

Fix **q = 0.15** and remove `round(q * len(base))` rows per column for both removal arms.

- `raw`: dirty base context with no removal.
- `random`: remove that count uniformly without replacement using the §3 stream; scores
  and removals do not depend on pass-1 scores.
- `purify`: for **each outer fold**, run inner raw cross-fitting on its outer training pool
  only (five inner row folds, or `min(5, pool_size)`), with context cap 512 and the same
  model/seed. No outer held-out row may enter inner preprocessing, context, or fit. Rank each
  base row by its inner out-of-fold target-cell score, after the §8 failure penalty, and
  remove the highest scores; break ties by ascending row index. Use the remaining dirty
  context for final scoring. A full-table raw score matrix must not be reused as pass-1.
  There is one removal step, no iterative trimming, gradient influence or rare-valid guard.
- `oracle` (**diagnostic**, all conditions): use the same base row IDs with clean context
  target values and clean conditioning features, transformed by the dirty-fitted encoder.
  Query features and scored query values remain observed. Only this arm receives a clean
  table; it is not deployable and its gap is not guaranteed to be positive.
- `leaky` (**diagnostic**, `real` only): union the dirty base with the entire query fold,
  intentionally violating the context exclusion. The resulting diagnostic context can
  exceed the ordinary cap of 512. It must never be pooled with deployable arms.
- `raw_leo` (**secondary**, keyed `real` tables only): raw scoring with five entity-group
  folds, cap 512 and no removal. Permute distinct observed groups, assign round-robin to
  folds, then sample bases from the other group folds. All rows sharing a key stay together;
  no query entity group enters a fitted context. At least five observed groups are required.
  Its bases necessarily differ from row-level bases; retain the same evaluation rows,
  seeds and model settings for the paired comparison.

The fixed public-schema keys (`benchmark.ENTITY_KEYS`) are `hospital/provider_number`,
`flights/flight`, `beers/brewery_id`. Read them from **observed dirty values** and factorize
exact strings, without clean-key repair or label-based selection. A corrupted key can split
one true entity; shared or empty keys can merge distinct entities. This is observed-key
leave-entity-out, not proof of independence or reliable latent-entity isolation. Final-pass
transductive preprocessing still sees all observed rows in this arm. `rayyan` has no declared
entity key and no `raw_leo` arm; do not invent a substitute or count this as a failed arm.

Record final and inner query/base/active/removed/preprocessing row IDs, model, seed, fold,
stage and outer-fold dependency in `contexts.jsonl`; map subsample positions to source IDs
using metadata. No context selection uses errors, clean values or rare-valid evaluation masks.

## 6. Models, baselines, pins and compute

Use **TabPFN-2**, package **tabpfn 9.2.0**, local pinned classifier and regressor from
`data/manifests/tabpfn_v2_checkpoints_20261030.json`. The manifest specifies upstream
classifier revision `275f19d2add9c2c0de38f9ebaded3856599fa2e7` and regressor revision
`02a44705ff7790b50cded404bc59adb94da456a1`, with SHA-256/size for weights and license files.
Set `n_estimators = 1`, `device = cpu`, `random_state = seed`,
`ignore_pretraining_limits = True`, and categorical feature indices as in the frozen adapter.
Use the pinned regressor's full predictive distribution/CDF for numeric tails. Do not use
newer default weights or silently substitute a checkpoint. TabPFN inference performs no
task-specific weight updates; context `fit`, preprocessing and caching still cost compute.

The conditional non-TFM comparison is **LightGBM 4.6.0**: `n_estimators=100`,
`learning_rate=0.1`, `num_leaves=15`, `min_child_samples=5`, `n_jobs=1`, `verbose=-1`,
`random_state=seed`. Classification predicts context classes. Regression uses a Gaussian
tail around the fitted conditional mean, with residual standard deviation from
`cross_val_predict` using `cv=min(3,n_parseable)` (floor `1e-6`, population standard deviation).
This model is fitted per context; the no-weight-update description applies to TabPFN, not
LightGBM. LightGBM conditional scoring is CDC-inspired, not the published CDC implementation.

Run label-free baselines VF, PF, RobustZ, ColumnIF (100 Isolation Forest trees per column),
and DDCcore, using the exact frozen `baselines.py`. DDCcore is a simplified implementation,
not reference DDC. Numeric-only baseline columns without support retain zero scores and the
full denominator. Baselines can have different support from the conditional scorer; identify
method-specific support and do not present conditional-column coverage as universal support.
TFM-versus-baseline and per-type comparisons are secondary descriptive analyses, without
claims of reproducing published CDC/uTabPFN or comparing supervision regimes as equal SOTA.

CPU local only, budget **$0**; no GPU/cloud, paid API, new data or checkpoint download.
Confirmatory execution uses four concurrent local processes with two Torch/BLAS/TabPFN
threads each (LightGBM remains one thread). The built-model cache is explicitly disabled
(`TABPFN_MODEL_CACHE_SIZE=0`); the package's ordinary raw-checkpoint cache may operate.
This resource allocation was selected from development timing only before confirmatory
evaluation. The initial development grid used three processes with three threads each,
so its timings are feasibility measurements, not directly comparable speed benchmarks.
Use `.venv-tfm/Scripts/python.exe` and the exact distribution pins in
`experiments/tfm_env_freeze.txt`. The environment is **not isolated**:
`include-system-site-packages=true`, with torch inherited from system Python. Record
`experiments/validation/tfm_environment_provenance_20261030.json` with the run environment.
Distribution metadata alone does not pin wheel builds, all transitive dependencies or
licenses; the coordinator must review these limitations before freeze. Record actual CPU,
Python executable/version, package versions and thread settings; do not assert unmeasured
hardware capability. Check core pins before loading data, and evaluate code and weight
licenses separately. The existing weight manifest records Prior Labs License v1.1;
distribution attribution requirements remain applicable, without authorizing distribution.

**Compute control and accounting:** Report ordinary raw and random deployment costs,
purify total cost, and nested first-pass time under **`pass1_nested`** for each model/seed.
Purify timing includes preprocessing, inner typing/encoding/fits and final scoring; report
`purify_final = purify_total - pass1_nested` without double-counting. Nested pass-1 is
purify's incremental preparation cost; it is not free, a reused global raw pass, or an
increment required by random scores. For a matched-compute random control, account for
the same nested pass-1 preparation plus the random final scoring while ignoring its ranks:
`random_matched_compute = random_deployment + pass1_nested`. This is a declared cost
accounting control with the **same random scores**, not an additional accuracy arm.
Label this sum as accounted cost rather than separately measured end-to-end wall time.
Retain component timings and whole-run wall time. Report context/model fit calls and peak
memory when instrumented; unmeasured fields must be marked unavailable, never inferred from
theoretical forward counts or called measured. Do not allocate cost after seeing accuracy.

## 7. Metrics, paired uncertainty and descriptive reporting

The primary metric is cell-level **AUPRC = average precision**, grouping tied scores as in
`sklearn.metrics.average_precision_score`, over all eligible cells. This is not trapezoidal
PR integration. Secondary metrics are R-precision (audit budget = number of labelled errors),
precision at 1% and 5% of eligible cells (`max(1, round(fraction * cells))`), rare-valid alarm
rate, coverage and failure counts. For exact top-k budgets break score ties by stable row-major
cell order. Rare-valid cells are correct cells with clean marginal value frequency `<= 1%`
in columns whose clean unique ratio is `<= 0.5`; report the share flagged in the R-precision
budget. That evaluation-only mask must not protect context rows or influence detection.
If its denominator is zero, report unavailable with the denominator, not zero.

The **source table** is the cross-table reporting unit. Conditions and seeds are repeated
measurements inside that table. For every declared paired contrast, report each seed's
metric, the mean paired difference over all five seeds and its **95% row-bootstrap interval**:

1. Make **1,000** bootstrap draws using `np.random.default_rng(2027)`; each draw samples `n`
   row indices with replacement from that capped table.
2. Use the **same sampled row indices across both arms/models and all five seeds**. Retain
   all cells of each sampled row. Use each seed's own error mask, including for injection.
3. Recompute each seed's two APs on those rows and average their paired differences. Do not
   retrain detectors, resample seeds or average away a missing seed.
4. If any seed in a draw has no positive error cells, discard that **whole** draw. Report
   valid/attempted replicate counts and take the 2.5th and 97.5th percentiles of valid
   seed-averaged differences. If no valid replicates remain, report the interval unavailable
   and stop complete analysis for coordinator review; do not invent an interval.

These are descriptive intervals conditional on the fixed predictions, capped rows and seeds;
they do not include retraining, new corruption-seed or new-table uncertainty. Rows may share
entities or sources. Row resampling assumes row exchangeability for its uncertainty
interpretation and may understate uncertainty under within-entity dependence. Cross-fitting
does not create IID rows. This limitation also applies to the requested `raw_leo` comparison;
its interval remains a row bootstrap, not an unapproved entity bootstrap.

Report **descriptive macro means** with equal weight per source table, separately by
condition and comparison. The primary macro is the arithmetic mean of the four real-table
`Delta_t` values. The LEO macro covers only its three declared keyed tables, with that
denominator explicit. Do not pool all cells or average 12 table-condition entries into an
inferential sample. Report individual table effects even when signs disagree.

There is **NO binary cross-dataset verdict**, no Wilcoxon test over table x condition units,
no H1/H2/H3 supported/reversed rule, no eight-of-twelve threshold and no Holm-adjusted
replacement verdict. Conditions are not independent datasets; seeds are not independent
tables. `docs/CLAIM_EVIDENCE.md`, **DES-01**, records a conditional design-resolution
diagnostic illustrating why repeating conditions does not add independent table signs;
it neither validates a sign test for these tables nor supplies detector evidence. A CI
excluding zero is descriptive per-table evidence, not a multiplicity-controlled discovery
or population-wide superiority claim. No new datasets or selective seeds may be added to
obtain a desired significance result.

Report whole-universe, numeric/categorical and supported-columns-only summaries separately.
The real-only sensitivity analysis excluding columns with error rate `> 50%` is explicitly
evaluation-label-dependent and exploratory; it never replaces the primary denominator.
Failure masks and unsupported cells must remain visible in all relevant reports.

## 8. Failures, coverage and stopping

Unsupported target columns are distinct from prediction failures: score 0 and report their
counts, names, eligible-cell share and error share. For nonfinite predictions (`NaN`/infinity)
or caught column-fit errors, retain a per-cell failure mask and exception metadata and
assign **max finite score + 1.0** within that run/model/arm score matrix; use max = 0 if
there are no finite scores. No failed cell leaves the eligible denominator. Report coverage
as (i) cells in supported columns, (ii) errors in supported columns and (iii) finite output
coverage before penalties, with method-specific denominators where support differs.
Retain pass-1 failures and their penalties because they can affect purification rankings;
do not conceal them behind a finite final score.
The event journal also records nonfinite model returns even when the model call raises
no exception, including their counts and nested/final stage. This reporting check does
not alter the score or penalty rule.

Run-level failures, interrupts, unresolved partial attempts, absent required arms or missing
seeds block complete-grid analysis. Preserve each attempt journal (`attempt.json`), stage,
timestamps, exception and `.partial` artifacts. A successful execution requires `scores.npz`,
`contexts.jsonl`, `meta.json` and a completed journal; execution completion alone does not
establish scientific validity. Do not silently overwrite a failed attempt or replace its
seed. Any repair/retry must preserve the original attempt and have a documented coordinator
resolution. Changes to frozen code require a new amendment/freeze, not a replacement run
under the previous source identity. Undefined metrics remain explicitly unavailable.

Report the entire planned grid, failures, coverage and negative/mixed effects without
changing the question or activating a fallback after seeing results. There is no automatic
pivot authorized by v2.1. If feasibility prevents completion or a decision beyond the
accepted amendments is needed, stop the affected item and refer it to the coordinator.

## 9. Deviations and replacements of historical rules

These are prospective amendments after disclosed descriptive data access, not claims that
the confirmatory tables were wholly unseen. Historical protocols and artifacts stay intact.

### 9.1 Relative to v1 (`PREREGISTRATION.md`)

| Item | v1 | v2.1 | Rationale / limit |
|---|---|---|---|
| Primary information boundary | Leave-entity-out | Five row folds primary; observed-key LEO secondary | Accepted row-level estimand; keys unavailable for every table |
| Numeric score | Density or standardized residual | Two-sided predictive tail plus parseability term; declared fallback | Fix semantics of the implemented distribution API |
| Trimming | Query influence gradient or LOO variance | Outer-isolated nested pass-1 target-cell suspicion, q=0.15 | Feasible per-column intervention; not an influence estimate |
| Rare-valid protection | Frequency guard | No pruning guard; evaluation-only rare-valid alarms | Guard would also protect plausible errors; no oracle protection |
| Baselines | Reference DDC, ColumnIF, CDC, uTabPFN | DDCcore, ColumnIF, LGBM conditional, TFM raw, VF, PF, RobustZ | Explicit implementation identities; no reproduced-system ranking claim |
| Context size and ensemble | Context-size study / pretrained scorer | Cap 512; TabPFN n_estimators=1 | Fixed CPU design; no context-size sweep |
| Data | Four full benchmark tables | movies_1 development; four confirmatory tables capped at 1,000; injection probes | Fixed local compute scope; real remains primary |
| Metrics | Precision/recall/F1 at 1%, 5%, 10% budgets | AP primary; R-precision, P@1%, P@5%, rare-valid alarms and coverage secondary | Preserve v2 metric specification; no 10% or F1 endpoint |
| Uncertainty | Entity-cluster bootstrap | Same-row bootstrap over all seeds, per table | Accepted descriptive row analysis, with dependence caveat |
| Stop/pivot rules | Three automatic fallback criteria | Descriptive effects and feasibility referral; no automatic pivot | Accepted continuation of Path A; preserve negative evidence without outcome-driven reframing |
| Extra purification compute | Matched random count | Matched count plus explicit pass1_nested cost control | Distinguish selection from preparation compute |

### 9.2 Relative to v2 (`PREREGISTRATION_V2.md`)

| Item | v2 | v2.1 | Authority / consequence |
|---|---|---|---|
| Primary endpoint | Purify minus random over 12 table-condition units | TabPFN purify minus random per real table, seed mean | Accepted descriptive scope; injection is mechanistic |
| Cross-table inference | Wilcoxon, positive-CI count, Holm, binary verdict | Per-table paired intervals; descriptive condition-specific macros; no binary verdict | Conditions are dependent; DES-01 informs design limitation |
| Pass-1 boundary | Same model's whole-table raw pass | Nested raw cross-fitting isolated from each outer query fold | Prevent outer-query information entering trimming |
| Final preprocessing | Label-free global observed encoding | Retained, explicitly transductive; inner preprocessing restricted to outer pool | Strict inductive/group proposal not adopted as primary |
| Entity sensitivity | Row folds only | raw_leo on three real tables with fixed observed keys | Accepted secondary boundary; corrupted-key limitation disclosed |
| Compute control | Arm wall times | Nested cost separate and incremental to purify; random scores independent; matched-compute accounted sum | Accepted control interpretation in task card |
| Numerical terminology | Predictive tail in formula | Explicit tail, not density; fallback and token semantics specified | Avoid conflating score types |
| Injection | 10%, types list includes ambiguous “uniform” | Five types, uniform attempted type selection; injection seed equals run seed | Match inject/get_table without adding an error type |
| Environment | “isolated” .venv-tfm | System site packages inherited, provenance disclosed | Recorded environment limitation; no isolation claim |
| Failures and freeze | Coverage penalty and protocol hash | Preserve journals/partials, require full source manifest plus protocol hash | No silent failed-seed removal or stale-code analysis |
| Access disclosure | Profiles viewed; design on movies_1 | All-five-table profiles viewed; detector access limited to dev/fixture | Explicitly distinguish descriptive access from detector evaluation |

## 10. Freeze and provenance procedure (coordinator only)

No hash, source manifest, run, approval or result is created by this document. Before any
confirmatory run, the coordinator must reconcile source and analysis with this amendment,
resolve discrepancies recorded in the prereg worker's handoff, synchronize affected design
documents, review environment/checkpoint provenance, and record the final source identity.
Freeze the deterministic data/subsample/eligibility, typing, fold/base, seed, trimming/tie,
score/failure and analysis rules above, with their ordered row IDs and dependency records
retained in run artifacts. Do not choose them after inspecting confirmatory scores.

Create **both** `prereg/PREREGISTRATION_V2_1.sha256` (protocol SHA-256) and
`prereg/PREREGISTRATION_V2_1.freeze.json` (schema_version 1, `files_sha256` mapping).
The full source manifest must cover every path in **REQUIRED_FREEZE_FILES** in
`src/cric_ed/v2_contract.py`, not only this Markdown file. At this candidate snapshot these
are:

- `src/cric_ed/conditional.py`
- `src/cric_ed/baselines.py`
- `src/cric_ed/benchmark.py`
- `src/cric_ed/v2_contract.py`
- `src/cric_ed/run_record.py`
- `experiments/tfm/run_v2.py`
- `experiments/tfm/analyze_v2.py`
- `prereg/PREREGISTRATION_V2_1.md`
- `experiments/tfm_env_freeze.txt`
- `data/manifests/raha_download_20261030.json`
- `data/manifests/tabpfn_v2_checkpoints_20261030.json`

The manifest may additionally cover provenance and split records; it must not omit any
required file. `verify_freeze` must accept exact bytes, reject stale/missing entries and
agree with the protocol-only hash. The coordinator records protocol hash, full manifest
identity, source revision, timestamp and authorization **before execution** in
`docs/EXPERIMENT_LOG.md`. Only that act gives this candidate its FROZEN status; the status
line is not permission to run. Automatic hashes do not establish scientific approval.

Each run retains protocol/source snapshot/code/checkpoint identities, package metadata,
configuration and seed, input/row identity, contexts, failure masks, timings, journal and
scores. Analysis must reject development runs, duplicate/incomplete table-condition-seed
grids, unresolved partial attempts, missing required arms, different row/column universes,
or identities inconsistent with the freeze. Include raw_leo only where defined. Archive
metadata, analysis inputs and scores.npz hashes under an identified source revision. Every
later numerical research claim must be linked by the coordinator through
`docs/CLAIM_EVIDENCE.md` to run, artifact, source and configuration. Any post-freeze method,
code, data, checkpoint or analysis change requires a documented amendment and new freeze.
