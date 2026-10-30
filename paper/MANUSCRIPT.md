# Manuscript status — INTERNAL DRAFT, NOT FOR SUBMISSION

Updated 2026-10-30. The LaTeX source of record is `paper/main.tex`; this file is a plain-text
companion and must not diverge from it.

The previous version of this file (commit `4c8f0f3`, retained in Git history) is withdrawn.
It claimed a tabular foundation model, RAHA benchmark results, a paired `+0.0167` AUPRC
trimming gain, a rare-valid guardrail benefit, `K = 25` and rejection of a null hypothesis.
None of these is supported by the artifacts (see `docs/review/AUDIT_20261030.md`).

## What the measured pilot shows (synthetic software fixture only)

Source: `experiments/archive/run_pilot_001/` (as executed) and
`experiments/archive/run_pilot_003_evalfix/` (paired streams, corrected evaluator). 100 rows,
20 entities, 400 eligible cells, 4 error cells, 1 seed.

| Arm | AUPRC run 001 (old evaluator) | AUPRC run 003 | 95% CI run 003 | Rare-valid cells in top 5% |
|---|---|---|---|---|
| MAD (column-wise) | 1.000 | 1.000 | [1.000, 1.000] | 4/4 |
| Conditional scorer, no trimming | 0.698 | 0.365 | [0.292, 1.000] | 3/4 |
| + matched-random removal | 0.674 | 0.365 | [0.294, 1.000] | 3/4 |
| + influence trimming (oracle rare list) | 0.691 | 0.357 | [0.278, 1.000] | 3/4 |

Run 003: separated random streams (paired arms), tie-invariant AUPRC (= scikit-learn average
precision), coverage penalty, 1,000 entity-cluster bootstrap resamples (990 valid). Paired
differences (95% CI): trim − random −0.008 [−0.081, 0.048]; trim − untrimmed −0.008
[−0.042, 0.000]; untrimmed − MAD −0.635 [−0.708, 0.000]. The run-001 value 0.698 came from
input-order tie breaking among six cells clipped at score 25 (two of them errors).

- The scorer is a kernel-weighted local conditional estimator; no TFM was run.
- MAD beats all conditional-scorer arms; untrimmed context is at least as good as influence
  trimming. Rule 1 cannot be evaluated as written (raw uTabPFN/CDC on a pilot benchmark were never
  run); the untrimmed proxy outcome is negative.
- The rare-valid difference is one cell and is shared by the untrimmed arm.
- The trimming comparisons are inconclusive (paired intervals include 0); no trimming benefit is supported.

A submission manuscript requires an approved research path and confirmatory evidence; see
`docs/DECISION_BRIEF_20261030.md`.
