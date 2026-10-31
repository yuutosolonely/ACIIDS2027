# Candidate v2 amendment for author review

Status: **PROPOSAL, NOT APPROVED, NOT FROZEN.** This document does not select Path A,
accept weight terms, change the budget, or authorize a model/benchmark run. It leaves
`prereg/PREREGISTRATION.md` and `prereg/PREREGISTRATION_V2.md` unchanged. Source is
`06ded051a382bee8e6db47c582e46145fe544515` plus the working tree identified by
`docs/handoffs/PREFLIGHT_RELIABILITY_20261030.json`.

## 1. Recommended scope and estimands

Retain the original cell-error-detection question. Use each fixed eligible cell universe
and the same errors/rows across arms within a table, condition and seed. The proposed
primary comparison is `purify - matched-random` AUPRC on each real-error table, averaged
over the declared context seeds. Report each table and a descriptive macro mean across
the planned tables. This targets the named benchmark collection; it does not establish
performance over a population of unseen datasets.

TFM versus the non-TFM conditional model remains a secondary comparison, using identical
contexts. Clean-context and leaky variants remain labelled diagnostics. Injected random
and systematic conditions probe mechanisms separately; neither becomes another independent
dataset merely because it is another condition. The current coupling of injection/context
seeds must be disclosed or replaced by explicitly frozen streams before execution.

All score types must be named accurately: the numerical candidate uses a predictive
tail score, not a continuous density. Keep numerical/categorical and whole-universe
reports separate. Do not introduce pooled rank normalization without an approved rule.

## 2. Information boundary and groups

Recommend an inductive boundary: fit transformations and models without the query row's
declared entity group. Both outer and inner folds preserve groups. Inside each outer
training pool, inner cross-fitting supplies pass-1 scores for context candidates; the
outer held-out groups are absent from inner preprocessing, fits and trimming decisions.
Within an inner fold, fit preprocessing without its own held-out groups too.

Group keys and their limitations need a per-table registry before runs, based on public
schema/dirty metadata or exogenous IDs. Do not use clean values or error rates to define
groups. Corrupted entity IDs may fail to link true duplicates; a unique row ID does not
prove independent entities. If a defensible group definition is unavailable, record that
limitation and obtain an explicit row-level estimand decision. Do not silently substitute
row folds or omit the planned table.

Freeze the column schema/eligibility rule before evaluation. For the recommended strict
boundary, fit encoding parameters on the declared training context only and state whether
trimming also removes a row from that fit. Report unseen values, missing values and
unsupported columns over the fixed universe. The current candidate still uses global
final-pass encoding and row folds; it does not implement this full proposal.

## 3. Controls and compute

Raw, matched-random and purification use the same base rows, model configuration, query
rows and context cap. Random removal removes the same count as purification and uses a
separate deterministic stream independent of pass-1 ranks.

To address extra compute, propose a common nested first-pass stage available to both
purification and a matched-compute random control; the latter does not use its ranks.
Log the common preparation cost and each arm's incremental cost. Also report the ordinary
raw detector's deployment cost separately. Do not hide the nested fits by calling them
cached/free, and do not allocate shared cost post hoc to improve a runtime comparison.
Context-fit calls, transformation time, memory and wall time remain required measurements.

## 4. Statistical unit and limits of the current collection

Use the source table as the proposed cross-table unit. Conditions and seeds are repeated
measurements inside a table. Retain paired resampling of declared entities within each
table for conditional uncertainty, with the same sampled entities and all declared seeds
in every valid replicate. A valid resampling interpretation still needs stated assumptions
about independence between entities; cross-fitting does not create IID observations.

SciPy's Wilcoxon notes assume independent, identically distributed differences and discuss
symmetry, ties and zeros. The current design does not justify treating every table-condition
contrast as an independent draw. Source inspected 2026-10-30:
[SciPy Wilcoxon documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.wilcoxon.html).

The design diagnostic `design_resolution_20261030` enumerates an exact sign-flip scenario
with four independent table signs: there are 16 equiprobable assignments, and an all-positive
maximal statistic has one-sided p = 1/16 = 0.0625. Repeating three conditions per table does
not add independent signs. This calculation assumes independent symmetric/equiprobable null
signs; it does not validate sign-flipping for the actual tables or rule out every other
statistical model. Artifact/config/source identity:
`experiments/validation/inference_resolution_20261030.json`; code:
`tools/check_inference_resolution.py`; claim ledger: DES-01.

Recommendation for the current collection: descriptive table effects, uncertainty with
its scope stated, and no binary cross-dataset superiority verdict. Retain negative and
mixed effects. If a future project requires a cross-dataset confirmatory claim, design a
new collection and analysis before results, with justified independent units and
multiplicity handling; do not count conditions/seeds as extra datasets or add datasets
until a desired p-value appears. This recommendation has not replaced v2's decision rule.

## 5. Run failures and provenance

The new attempt journal reserves a fresh `.partial` directory. It records the request,
source/code identity, stage and timestamps. Runtime/preflight exceptions and interrupts
remain failures at that path and are re-raised. A run finalizes only after its required
artifacts exist; scientific validity is separate from execution completion. Per-cell
failures remain in masks/metadata under the declared penalty rule. Run-level failures
block complete-grid analysis until an explicitly documented resolution; they are not
silently skipped or replaced by a successful seed.

Runtime metadata must match exact declared core pins before input loading. The inherited
environment record omitted `torch`; its original bytes are preserved at
`experiments/archive/tfm_env_freeze_before_core_pin_20261030.txt`. The candidate record now
adds the installed distribution's exact version and passes the declared-pin check. This
is a local setup correction, not a protocol freeze.

The environment is not isolated: `.venv-tfm/pyvenv.cfg` enables system site packages and
`torch` resolves from the base Python installation. The v2 prose calling it isolated is
therefore unsupported and must be corrected in an approved amendment. Metadata provenance:
`experiments/validation/tfm_environment_provenance_20261030.json`. Before freeze, review
complete dependencies and artifact/build origins or provision a reproducible environment
under authorization. Distribution versions alone do not pin wheel builds, device
capability or licenses; no packages were installed in this work.

## 6. Freeze contents before confirmatory

After approval, synchronize IDEA, plan and a new/amended preregistration. Freeze the
exact schema, eligible universe, group registry, subsample IDs, outer/inner fold membership,
seed streams, context bases, trimming/tie rules, score semantics, failure policy, analysis
unit, reporting thresholds and control costs. Freeze source, packages/builds, input and
checkpoint revisions/hashes and code/weight licenses separately. Generate hashes only
after all required choices are fixed; an automatic hash does not confer approval.

The candidate source-manifest guard and synthetic tests implement only part of this
process. No real protocol lock or split manifest has been generated in this work.

## 7. Decisions required before research execution

The author still needs to confirm Path A and the rights associated with the existing
weights, or choose a different scope; no paid compute is authorized. Then review this
proposal's group/inductive boundary, extra-compute control, descriptive cross-table framing
and failure policy. Local implementation and synthetic validation may continue under the
existing authorization, while the original NO-GO decision for this deadline remains active.
