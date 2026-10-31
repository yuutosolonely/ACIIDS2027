# CRIC-ED

**Context Purification for Cell-Level Error Detection** is a research project evaluating whether selecting reference rows can improve conditional cell-error detection with tabular models. The project implements the user's selected Idea 3; the original team-card name is **TabFM-ED**.

This repository is an evidence-focused research workspace for ACIIDS 2027. Its protocols, datasets, model revisions, run artifacts, analysis, and manuscript are documented separately so that software checks are not mistaken for scientific results.

## Current status

**As of 2026-10-31:** the confirmatory grid and artifact audits are complete. The 15-page manuscript is built and available for author review. Internal reviews have been recorded, with open findings; this is not an independent replication or a conference decision. The author has not yet completed the final read-through or decided whether to submit. No submission or publication has been made.

The main result is deliberately narrow: on the four capped real-error tables, TabPFN context purification performed worse than matched random removal on three tables and better on one. These are per-table findings, not a general claim that purification succeeds or fails across datasets. The exact estimates and supporting run IDs are in the [claim–evidence ledger](docs/CLAIM_EVIDENCE.md). The grid also contains a disclosed fit-failure case in one injected-error unit; its post hoc sensitivity analysis is labeled exploratory.

See [research state](docs/STATE.md), [authorization](docs/AUTHORIZATION.md), and the [experiment log](docs/EXPERIMENT_LOG.md) for the current gates, decisions, deviations, and unresolved items.

## Study at a glance

- **Task:** rank suspicious cells in dirty tables. This is distinct from row anomaly detection, label-error detection, imputation, and data repair.
- **Intervention:** for each target column, use nested out-of-fold scores to select rows for removal from the model's reference context.
- **Control:** remove the same number of rows at random from the same base context; account for the extra selection compute.
- **Models:** pinned TabPFN-v2 and a task-fitted LightGBM conditional model.
- **Data:** four capped RAHA tables, each evaluated with real errors and two separate injected-error conditions. Five seeds give 60 table–condition–seed units; both models are evaluated in each unit.
- **Scope:** four named source tables, a fixed removal fraction, a capped context, and the declared preprocessing and support rules. The study does not establish state-of-the-art performance or a population-wide effect.

The protocol and estimands are documented in [`prereg/PREREGISTRATION_V2_1.md`](prereg/PREREGISTRATION_V2_1.md); the frozen source and split manifests are in `prereg/` and `data/manifests/`. Numerical claims should be checked against [`docs/CLAIM_EVIDENCE.md`](docs/CLAIM_EVIDENCE.md) and its referenced artifacts.

## Repository map

| Path | Contents |
|---|---|
| `src/cric_ed/` | Detection, baseline, benchmark, and protocol-contract code |
| `experiments/tfm/` | Frozen-run entry points and analysis code |
| `experiments/archive/` | Retained run outputs, audits, and execution history |
| `experiments/validation/` | Read-only verification and reproducibility records |
| `experiments/exploratory/` | Clearly separated post hoc or exploratory analyses |
| `data/manifests/` | Dataset and checkpoint identity records; local raw data are excluded from Git |
| `prereg/` | Protocol versions, freezes, and split manifests |
| `docs/` | State, authorization, evidence ledger, literature, decisions, and workflow records |
| `paper/` | Manuscript sources and built outputs |
| `tools/` | Setup, audit, manuscript, and repository utilities |
| `.agents/`, `.claude/`, `.codex/` | Project-specific instructions and tool configuration; role definitions do not launch agents |

Some archived files record failed or interrupted attempts. They are retained for audit and are not additional successful runs. Files in the research manuscript and historical evidence directories should not be removed merely to make the repository appear smaller.

## Setup and checks

Requirements: Python 3.11 or newer and [`uv`](https://docs.astral.sh/uv/). From the repository root:

```powershell
uv sync --locked
uv run python tools/check_setup.py
uv run pytest -q
uv run python tools/sync_skills.py --check
uv run python tools/check_mcp.py
```

These commands set up and check the local project. Passing them does **not** pass a research gate or verify model performance. The confirmatory model environment and checkpoint requirements are documented separately; setup does not authorize paid compute, new model downloads, accepting new license terms, publication, or submission.

For details, see [`docs/SETUP.md`](docs/SETUP.md), [`docs/WORKFLOW.md`](docs/WORKFLOW.md), and [`docs/HARNESS.md`](docs/HARNESS.md).

## Evidence and reproducibility

- Start from [`AGENTS.md`](AGENTS.md), [`docs/STATE.md`](docs/STATE.md), and [`docs/AUTHORIZATION.md`](docs/AUTHORIZATION.md).
- Review the frozen protocol before interpreting results.
- Treat the claim ledger as the index from manuscript claims to run IDs, artifacts, source revisions, and configurations.
- Distinguish confirmatory measurements, exploratory analyses, source-reported facts, and hypotheses.
- The byte-identical analysis replay uses the same analysis implementation; it is not an independent analysis. The single-unit rerun is not an independent software replication.
- The row-bootstrap intervals are descriptive and conditional on saved predictions and the named tables. They do not establish performance on new tables.

Local raw data, model checkpoints, virtual environments, caches, run directories, and logs are excluded by `.gitignore`. A fresh checkout may therefore require locally authorized data and pinned checkpoints before some analyses can be reproduced. Check their licenses and access conditions separately.

## AI assistance, authorship, and licensing

AI assistance used during the project is disclosed in the manuscript credits. AI systems are not authors; the human author is responsible for the design, sources, results, interpretation, and final text. Do not remove required disclosure or treat generated drafts as verified scientific evidence.

The repository license is in [`LICENSE`](LICENSE). Third-party software, data, and model weights can have separate terms; see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and the relevant manifests. Do not infer rights to redistribute data or checkpoints from the repository license.

## Submission status

The manuscript is for author review. The final submission decision belongs to the author. Agents must not submit, upload, publish, or push this repository; review the current authorization before any external action.
