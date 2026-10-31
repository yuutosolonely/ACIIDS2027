# Reproducing the CRIC-ED v2.1 study

Status: confirmatory execution in progress. This document describes actual frozen
configuration and required verification, not a claim that all results are ready.

## Frozen source and inputs

Parent Git revision: 0aff63e292da7a071368f594015089d5d746fa05, branch coord/v2-1-base.
The integration remains uncommitted; the exact file map, not parent HEAD alone,
identifies executed code. Frozen at 2026-10-30T02:58:59.307840+00:00.
Protocol SHA256: eea8f0ee8b217458a82b073bac5261f43ab8056e1b4eb32a170e5aece061543a.
Source snapshot: c37e39ab8168ed2fda38e9a6e952a15114bda4faa595356c7aeeb5f633bf5678.

See prereg/PREREGISTRATION_V2_1.{md,sha256,freeze.json},
prereg/v2_1_split_manifest.json, data/manifests/raha_download_20261030.json,
and data/manifests/tabpfn_v2_checkpoints_20261030.json. Do not regenerate the
existing freeze or replace existing attempts. Data/weights are retained locally;
redistribution is subject to the applicable separate licenses and unresolved
dataset-level terms. No model defaults or upstream latest revisions are substituted.

The scientific environment inherits system site packages; it is not isolated.
Declared distribution pins are in experiments/tfm_env_freeze.txt; build/origin
limitations in experiments/validation/tfm_environment_provenance_20261030.json.
Run metadata records exact installed versions and CPU identification. This does
not establish wheel-level or arbitrary-platform bitwise reproducibility.

## Complete-grid execution

Use the existing .venv-tfm Python. The grid is four source tables x three conditions
x seeds0-4, both models per unit, with no selective omission. Fixed row cap1000,
outer folds5, context cap512, removal fraction0.15, TabPFN estimators1, CPU.
Four processes, two Torch/BLAS/TabPFN threads each; LGBM one thread; built-model
cache disabled. The initial development timing used three processes x three threads.
A separate verification rerun transiently adds one process and is excluded from
the performance grid; timing contention is disclosed in the experiment log.

```powershell
.venv-tfm/Scripts/python.exe experiments/tfm/run_grid_v2_1.py --workers 4 --threads 2 --out experiments/runs/v2_1 --archive experiments/archive/v2_1_runs
```

This command requires fresh output/archive roots and refuses overwrite. For a
full reproduction use new roots under the same frozen source. Failed/interrupted
attempts remain .partial with stage/exception journals; resolve them explicitly.
Raw scores, failure masks and clean evaluation arrays are saved in scores.npz;
meta.json retains configuration/source/rows/timing; contexts.jsonl records the
actual final/inner dependencies. Archived units copy meta, journal and predictions,
with hashes for large context files retained locally.

## Verification and analysis after the grid finishes

```powershell
.venv-tfm/Scripts/python.exe tools/audit_v2_artifacts.py --runs experiments/runs/v2_1 --out experiments/archive/v2_1_artifact_audit.json
.venv-tfm/Scripts/python.exe tools/check_frozen_splits.py
.venv-tfm/Scripts/python.exe experiments/tfm/analyze_v2.py --runs experiments/runs/v2_1 --out experiments/archive/v2_1_analysis
```

The frozen analysis requires all60 completed units with matching identities and
universes. It reports per-seed metrics, per-table paired AP differences and1000
same-row bootstrap draws shared across arms and seeds; source-level macro means
are descriptive. There is no Wilcoxon/Holm or binary cross-dataset verdict.
Intervals condition on saved predictions and do not account for retraining or
within-entity dependence. LEO is secondary on observed keys only.

Repeat analysis into a fresh validation directory and compare numeric JSON/CSV
artifacts, keeping both outputs. PDF creation timestamps may differ; compare
numerical data separately from figure binary hashes. A single frozen unit is also
rerun into experiments/validation/v2_1_replication; compare its arrays and contexts
with tools/compare_replication.py, without adding it to the60-unit analysis.

## Manuscript

```powershell
.venv-tfm/Scripts/python.exe tools/generate_paper_results.py
.venv-tfm/Scripts/python.exe tools/build_paper.py
```

The result generator requires complete confirmatory analysis and a passing actual
artifact audit. Tables and figures retain source hashes. Build uses the official
Springer LNCS2.25 template, copied to a local build directory, cached TeX resources,
and local PDF rendering. Verify every rendered page and the final12-15 page length.
Source/claim/citation and local text-overlap checks remain necessary; neither a
successful compile nor an automated overlap screen establishes scientific merit.
Human authors retain responsibility and must verify the final paper and disclosures.
