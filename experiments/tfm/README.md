# CRIC-ED v2.1: authorized CPU study

Authority: the appended Path A and amendment decisions in
`docs/DECISION_BRIEF_20261030.md`, and Claude checkpoint `0aff63e`.
Codex owns integration and execution. NO-GO for the original ACIIDS deadline remains;
no submission, paid compute or new model download is authorized.

## Protocol

`prereg/PREREGISTRATION_V2_1.md` is the prospective amended specification. V1 and v2
remain historical records. Primary: row-level five-fold cross-fitting. Secondary:
observed-key leave-entity-out raw scoring for hospital/provider_number, flights/flight,
beers/brewery_id, real condition only. Final observed-table typing and encoding are
explicitly transductive; fitted contexts exclude query folds. Nested purification
preprocessing and inner fits cannot see the outer query fold. V3 and strict_scorer
are inactive diagnostic alternatives, not this pipeline.

Models: pinned TabPFN-v2 classifier/regressor, tabpfn==9.2.0, CPU, one estimator;
LightGBM conditional comparison. Numeric scores use predictive two-sided tails plus
parseability, not densities. Baselines: VF, PF, RobustZ, ColumnIF, simplified DDCcore.
Neither LGBM nor DDCcore nor TFM raw is a reproduction of CDC/DDC/uTabPFN.

Primary contrast: TabPFN purify minus matched-count random on each real source table.
Report five-seed mean paired differences and 1,000 paired row-bootstrap intervals,
with row-dependence caveats. Injection probes remain separate. Macro means are
descriptive; no Wilcoxon/Holm or binary cross-dataset superiority verdict.

Purify includes outer-isolated nested pass-1 compute, reported as pass1_nested.
Purify_final subtracts this component. Random_matched_total adds it to ordinary
random cost while retaining identical random scores: an accounted cost, not an
independently measured end-to-end accuracy arm. No double-counting these entries.

## Execution and validation

```powershell
.venv-tfm/Scripts/python.exe -m pytest -q -p no:cacheprovider
.venv-tfm/Scripts/python.exe experiments/tfm/run_v2.py --table movies_1 --condition real --seeds 0 --threads 3 --out experiments/runs/v2_dev
.venv-tfm/Scripts/python.exe experiments/tfm/analyze_v2.py --runs experiments/runs/v2_dev --out experiments/validation/v2_1_dev_analysis --development
```

Development analysis requires movies_1 only, all three conditions with the same seeds.
Confirmatory execution requires both PREREGISTRATION_V2_1.sha256 and .freeze.json,
covering every REQUIRED_FREEZE_FILES entry. Freeze verification uses exact bytes.
The root .gitattributes uses LF for text and preserves immutable archive/data/binary
bytes; do not mass-normalize archived artifacts or run from stale CRLF worktrees.

After development validation and recorded freeze, execute the full 4-table x
3-condition x 5-seed grid with both models. The analysis rejects missing/duplicate
runs, unresolved partials, absent arms, denominator misalignment and stale identities.
No result directory is overwritten. Source modifications after freeze require an
amendment and new freeze, not replacement of completed results.

Every fresh attempt starts as .partial with an attempt.json stage/time/request/source
journal. Exceptions and interrupts retain the journal and partials. Completion
requires scores.npz, contexts.jsonl and meta.json; abrupt termination may leave a
running journal, which is still incomplete. Inner and final context IDs are subsample
positions mapped to original rows by metadata.row_ids. Clean truth is evaluation-only
except the explicitly labelled oracle input. Failure masks retain the full denominator.

Runtime and input hashes are checked before data loading. The scientific environment
inherits system site packages and is NOT isolated; see the environment provenance
record. Exact distribution versions do not fully identify wheels or all transitive
packages. The original torch-omitting pin record is preserved in experiments/archive.
Capability verification at experiments/validation/g0_capability_20261030 uses synthetic
data and recorded zero network attempts; it is not benchmark performance evidence.

All numerical claims must link to runs, config/source hashes and artifacts through
`docs/CLAIM_EVIDENCE.md`. Tests using fake predictors establish software behavior only.
