# CRIC-ED prospective protocol v3 — strict group-isolated context purification

Status: **INACTIVE ALTERNATIVE, NOT ADOPTED, NOT FROZEN.** The newer Claude coordinator
checkpoint `0aff63e` and author decisions in `docs/DECISION_BRIEF_20261030.md` select v2.1:
row-level primary, leave-entity-out secondary, per-table descriptive reporting. This strict
group-primary draft was written before that newer handoff was discovered; it is retained
for provenance only and must not drive current experiments or replace the accepted choices.
Prepared under the user's active research/paper goal on 2026-10-30. Coordinator design
decisions remain open to methodological correction before freeze; they are not recorded
as detailed author statements. v1/v2 remain unchanged. Implementation, split manifests
and analysis must be complete and validated before a source/input freeze is recorded.

## 1. Task, research questions and scientific scope

Unsupervised cell-level error detection in dirty heterogeneous tables. Deployment arms
receive dirty eligible columns and a protected observed-group registry; no clean values
or error labels. Training-free refers to no task-specific TFM weight updates, with all
context fitting/preprocessing/preparation costs reported. The LightGBM comparator does
perform task-specific fitting and is reported as a separate supervised-in-context model.

RQ1: does conditional TabPFN-v2 scoring improve over simple label-free baselines and an
otherwise paired LightGBM conditional model? RQ2: how does dirty versus clean context
change scores under real and injected errors? RQ3: does fold-isolated context purification
improve over same-size random removal, and what happens to rare-valid alarms? These are
empirical questions, not promised positive findings.

Primary descriptive endpoint: per-table, seed-mean AUPRC difference between purification
and matched random on real errors. Report all individual effects and the descriptive
macro mean over the four named tables. Conditions and seeds are repeated measurements,
not independent datasets. No cross-table significance or general superiority verdict is
declared for this four-table collection. Confidence intervals have their explicit
within-table resampling scope and assumptions.

## 2. Data and prior exposure

RAHA upstream revision and file hashes remain those in
`data/manifests/raha_download_20261030.json`. Development: `movies_1`; named evaluation
tables: hospital, flights, beers, rayyan. Row cap 1,000, same sorted row IDs for every
arm/condition/seed; tables above the cap use `default_rng(0).choice(..., replace=False)`.
No dataset is omitted or replaced based on results.

Existing exposure is disclosed: dirty/clean descriptive error profiles of all tables
were viewed during the earlier audit; previous detector runs were development movies_1
only. Dirty-only schema/group profiles were read during this design stage. The study
is prospective relative to new detector evaluation, not an untouched-data claim.

Protected metadata columns are excluded from targets and query features before error
evaluation: row IDs named id/index/tuple_id when unique, and the declared group column.
Group columns: hospital provider_number; flights flight; beers brewery_id; rayyan
journal_issn. Group IDs are the observed dirty strings, with all empty entries assigned
one reserved missing group. They remain fixed across injected conditions and seeds.
This is observed-key isolation, not proof that corrupted keys identify all true entities.
Publish the excluded columns/counts and grouping limitations with the eligible universe.

Real condition uses dirty values with cell errors defined by raw string inequality to
the clean reference. Injection conditions start from the clean eligible values but only
the injector/evaluator sees the clean table. Random/systematic injection at fraction
0.10 uses the existing declared typo/replace/missing/format/scale implementation, applied
to eligible cells only. Group metadata is protected and never injected. Every shortfall
from the requested number of modified cells is recorded. No other injection rate or
method is selected from results.

## 3. Scorer and information boundary

Five outer folds of observed groups, seed-controlled. Shared base context per fold is
drawn without replacement from other groups, cap 256. Same split/base across models,
columns and arms. Context seeds 0,1,2,3,4. The injection seed equals the run seed in the
two synthetic-error conditions; disclose that coupled-seed estimand and never count it
as independent dataset replication.

For each outer training pool, infer column kinds from dirty training values only:
numeric when at least 80% of nonempty values parse as numbers, otherwise categorical;
categorical unique ratio over 0.5 is unsupported. Per-arm feature encoders fit on its
active context, never on queries. Target features are dropped. Column typing is shared
within the outer training pool and includes rows beyond the selected base; logs record
both typing and encoding dependencies. Unsupported targets remain in the denominator
with score zero and explicit support/kind masks.

Use the documented conditional score in `conditional.score_column`: negative log of
the two-sided predictive tail plus parseability mass for numeric values; smoothed token
mass for unparseable tokens; smoothed categorical probability with top-9 plus OTHER
when needed. These are tail/probability suspicion scores, not mixed continuous densities
or conformal p-values. Tail floor 1e-12. No fitted calibration from error labels.

Arms: raw; random removal of round(0.15 * base size); purification removing the same
count of highest pass-1 target-cell scores, ties by source row position. Pass 1 is an
inner group cross-fit inside each outer training pool, with min(5, number of groups)
folds and at least two groups. Both typing and encoders in every inner fit exclude its
query groups. A global pass-1 matrix is never supplied to the strict scorer.

The inner preparation is computed once per model/outer fold, shared for accounting.
Random ignores its ranks. Report shared preparation and each incremental arm cost;
standalone matched-compute comparisons include preparation for both random and purify.
Raw deployment cost excludes unnecessary preparation, while total study cost includes
all shared work. Report conditional model calls as well as time.

## 4. Models, baselines and labelled diagnostics

TabPFN package 9.2.0, pinned local v2 classifier/regressor from the existing checkpoint
manifest, one estimator, CPU, fixed run seed. LightGBM 4.6.0 conditional baseline uses
the same contexts, feature handling and arms, with the existing 100-tree/15-leaf model
and regression residual-tail approximation. It is CDC-inspired, not a reproduced CDC.

Simple baselines to implement/validate before freeze: leave-context frequency, pattern
frequency, robust numeric z-deviation and per-column Isolation Forest, using the same
group isolation wherever they fit reference statistics. Any DDCcore simplification is
labelled a local reimplementation, not the published system. CDC's clean-trained/
calibrated regime is discussed separately; no unfair headline ranking is claimed.

Oracle-clean context is a separate diagnostic entry point, with the same observed group
registry and query dirty values; it uses clean reference values only for context rows.
Leaky context deliberately includes outer query rows, on real errors only. Diagnostic
values never select a deployment arm, trim ratio, threshold or eligible column.

## 5. Evaluation and uncertainty — implementation pending

AP/AUPRC with ties grouped over every eligible cell; per-fold kinds/support reported,
numerical/categorical slices separate. Also precision/recall at 1%, 5%, 10% audit budgets,
rare-valid alarm counts/rates and coverage/failure denominators. Stable row/column order
breaks budget ties. Rare-valid is evaluation-only: a correct cell with clean-value
frequency at most 1% in an eligible column with unique ratio at most 0.5. Never pass this
mask to the detector or use it as a purification guard.

Report seed-mean paired effects. Within each table, resample the frozen observed groups
with replacement 1,000 times, retaining all rows in a sampled group and using the same
draw for every arm/model/seed. If any seed has no positive errors, discard the whole
replicate and report the valid count. Group independence is an assumption and corrupted
keys may understate dependence. No IID-cell bootstrap or hypothesis verdict from the
number of positive condition-level intervals.

Failure/NaN predictions receive max finite arm score + 1.0, with all failure masks and
denominators retained. Unsupported targets receive their declared zero score, not a
silently reduced universe. A run-level failure remains journaled and blocks complete-grid
analysis until a documented code/protocol resolution; no selective seed retries/omission.
All results and deviations are retained, including reversed/no-effect purification.

## 6. Freeze and completion prerequisites

Before any evaluation run: finalize/test scorer, group-isolated baselines, loader,
injection accounting, analysis and table generation; freeze exact row/group/fold/base
manifests and complete source/config/input/model/environment hashes. Record Python,
torch build, system-site inheritance and memory/timing method. The current environment
has inherited packages; versions alone are not a wheel-level reproducibility guarantee.

The capability check `g0_capability_20261030` establishes local API support only. It
does not supply benchmark evidence. No fixed numeric result is expected by this protocol.
Writing/publication decisions follow actual results and the active paper completion plan.
