# Candidate v2 pipeline — local remediation, not an approved research protocol

The author has recorded NO-GO for the ACIIDS deadline. The statement of Path A approval
in `prereg/PREREGISTRATION_V2.md` is not corroborated by the authorization/decision brief.
The code corrections described here are proposals for a future protocol amendment.
No real model, development benchmark or confirmatory run was executed to validate them.
Preregistration v1/v2 and existing result files remain unchanged.

## Corrections implemented for CPU validation

`conditional.score_table` rejects externally supplied pass-1 matrices. For each outer
fold, the candidate purification arm computes an inner cross-fit on the remaining rows,
including typing and encoding for that inner work. Only those scores rank rows in the
shared outer base context. Thus the outer query fold cannot influence purification via
the inner model or its preprocessing. Final-pass encoding is still the candidate's
global transductive encoding; this does not resolve its compatibility with the original
group/information-boundary requirements.

The proposal increases purification compute. Its full arm time includes preprocessing,
context construction and the inner fits; comparisons must disclose this extra work.
Matched random removes the same number of rows from the same outer base. Whether this
also needs a matched-compute control remains a design question before freeze.

`contexts.jsonl` records final and pass-1 stages, outer fold, seed, column, query/base/
active/removed row IDs and preprocessing row IDs. Failure records retain stage/fold/model
identity. Row IDs for the fixed dataset subsample are retained in run metadata.
Context IDs are subsample row positions, mapped to source rows by metadata `row_ids`.
Clean data may be passed only to the labelled oracle arm.

## Freeze and analysis validation (candidate contract)

Neither runner nor analysis creates a protocol lock automatically. Confirmatory runs
require both `prereg/PREREGISTRATION_V2.sha256` and
`prereg/PREREGISTRATION_V2.freeze.json`. The latter must have `schema_version: 1` and
`files_sha256`, mapping repository-relative paths to SHA-256 values. Required paths are
defined by `cric_ed.v2_contract.REQUIRED_FREEZE_FILES`: protocol, scorer, baselines,
loader, contract module, runner, analysis, environment record and pinned input manifests.
All listed files must still match; paths cannot escape the repository. The protocol
digest must agree between both locks. No actual lock is supplied by this remediation.

The canonical sorted hash map defines `source_snapshot_sha256`; runs record it and the
protocol/code/checkpoint identities. Runner verifies data/checkpoint/license file bytes
against the pinned manifests, refuses reuse of existing/partial run directories, and
checks the source freeze again before finalizing a confirmatory run. Hash verification
does not establish authorization, license compatibility or actual environment versions.

Analysis requires the full declared table-condition-seed grid and both models, rejects
partial/duplicate/wrong-source runs, and validates all declared method arrays, error masks,
failure masks, eligible denominators and row alignment across seeds. Invalid input creates
no result directory. Existing analysis output is not overwritten. Bootstrap replicates
are discarded as a whole if any seed has no positive error; a replicate never silently
changes the seed mean. The candidate decision rule still uses the v2 units and threshold;
their cross-condition dependence and multiplicity interpretation need methodological review.

Before any real freeze: reconcile scope/rights, amend and approve the protocol, decide
group and preprocessing boundaries, validate actual environment/checkpoint capabilities,
freeze exact split/subsample manifests and failure handling, and resolve the statistical
unit and matched-compute questions. This implementation does not complete those gates.

## Tests without checkpoints or network

The minimal environment runs the contract tests; the scientific module is skipped if
NumPy/pandas/SciPy are absent. The existing `.venv-tfm` environment can run the whole suite:

```powershell
.venv-tfm/Scripts/python.exe -m pytest -q -p no:cacheprovider
```

All new tests use temporary synthetic arrays/tables and a deterministic fake predictor.
They do not load weights or access RAHA data. Test PASS is software validation only.

## Reliability continuation — candidate setup, not a research run

`run_record.run_attempt` journals each fresh attempt before runtime/input verification.
It retains stage, source/request identity, error type/message and partial artifacts on
exceptions or interrupts, then re-raises the failure. Only a successful block with all
required output files finalizes the directory. Abrupt termination may leave a running
journal in `.partial`; analysis rejects that incomplete attempt too. Completed metadata
and the attempt journal must agree before analysis accepts an output directory.

`verify_environment` checks exact installed distribution metadata against the declared
pins before dataset loading, including all core scientific packages and `torch`. The
original pin record omitted torch; it is archived unchanged at
`experiments/archive/tfm_env_freeze_before_core_pin_20261030.txt`. The candidate pin record
now adds the installed version and its declared-pin check passes.

The existing `.venv-tfm` enables system site packages; it must not be called isolated.
See `experiments/validation/tfm_environment_provenance_20261030.json` for installation
origins and limitations. No packages or weights were installed/downloaded. Matching
distribution versions is not a complete dependency/build/license freeze.

The proposed statistical and information-boundary amendment is
`docs/proposals/V2_AMENDMENT_20261030.md`. It recommends table-level, descriptive reporting
for the present collection; the existing v2 hypothesis rule was not changed. The exact
sign-pattern enumeration in `experiments/validation/inference_resolution_20261030.json`
is a mathematical design diagnostic under stated assumptions, not a benchmark result.
