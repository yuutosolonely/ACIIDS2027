---
name: tabfm-protocol
description: "Triển khai hoặc kiểm scorer, cross-fitting và context selection của CRIC-ED."
---

# tabfm-protocol

Read docs/IDEA.md and experiment-plan. Define target column/task, eligibility, missing/unseen-category policy and score orientation. Exclude target from query features and held-out row/groups from reference context. Prevent clean truth and evaluation labels from reaching preprocessing/trimming. Pin package and checkpoint; check classification/regression/distribution support and licenses separately. Rank-normalize score types only under a preregistered rule; density is not probability. Record unsupported columns, nonfinite outputs and coverage. Treat no-crossfit/oracle-clean as diagnostic only. Test intervention effects with matched compute/context size; unsupervised anomaly methods are not automatically cell detectors.
