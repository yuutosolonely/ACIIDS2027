# Task cards for Codex — CRIC-ED v2.1 (coordinator: Claude, 2026-10-30)

Role split (author directive 2026-10-30): **Claude coordinates only; Codex executes all work.**
Read first: `AGENTS.md`, `docs/AUTHORIZATION.md`, `docs/DECISION_BRIEF_20261030.md` (last three
sections), `docs/proposals/V2_AMENDMENT_20261030.md`, your own handoffs in `docs/handoffs/`.
Goal (author): a complete, evidence-backed manuscript with detailed experiments, suitable for a
CORE-B-or-better venue. NO-GO for ACIIDS 31 Oct 2026 stands; no submission, publication, commit or
push unless the author asks. One Codex session at a time owns the files below.

## Accepted author decisions (2026-10-30, recorded in the decision brief)
1. Path A: TabPFN-2 via `tabpfn==9.2.0`, pinned checkpoints (`data/manifests/tabpfn_v2_checkpoints_20261030.json`), CPU, $0. v2 weights are ungated; no PriorLabs account needed. Prior Labs License v1.1 attribution applies on distribution.
2. Primary boundary: row-level cross-fitting (only the query row excluded). Secondary: leave-entity-out on tables with public entity keys (`ENTITY_KEYS` in `src/cric_ed/benchmark.py`: hospital/provider_number, flights/flight, beers/brewery_id).
3. Statistics: per-table descriptive; unit = source table; paired differences with row-bootstrap uncertainty per table; descriptive macro mean; **no binary cross-dataset verdict / no Wilcoxon over table×condition units**.
4. Compute-matched control: shared nested pass-1 (already implemented by Codex) used by purify; random-removal scores do not depend on pass-1, so report the nested pass-1 cost separately and as purify's incremental cost.

## Uncommitted edits Claude made BEFORE the role directive (review, keep or amend; do not silently revert)
- `src/cric_ed/conditional.py`: `folds_and_bases(..., groups=None)` group folds; `raw_leo` arm (requires groups); nested pass-1 timing in `log.seconds[("pass1_nested", seed)]`.
- `src/cric_ed/benchmark.py`: `ENTITY_KEYS`, `entity_groups()`.
- `experiments/tfm/run_v2.py`: `raw_leo` arm for `real` on keyed tables; timing rounding; `entity_key_leo` in params; prereg constants removed (now via `v2_contract`).
- `src/cric_ed/v2_contract.py`: `PREREG` → `prereg/PREREGISTRATION_V2_1.md`; freeze files → `PREREGISTRATION_V2_1.freeze.json` / `.sha256`.
- Known breakage to fix: `tests/test_v2_contract.py` still uses V2 freeze filenames; `experiments/tfm/README.md` is stale; `analyze_v2.py` still has the Wilcoxon/Holm verdict (must change per decision 3) and does not yet expect `raw_leo`.

## T1 — Reconcile code and tests (no model runs)
Make the four decisions executable; update `analyze_v2.py` to per-table descriptive reporting (primary: `tabpfn-v2__purify − tabpfn-v2__random` on each `real` table; mechanism probes: injected conditions per table; secondary: TFM−LGBM, oracle−raw, purify−raw, raw_leo−raw, LGBM purify−random; macro means descriptive; cost table incl. pass1_nested); require `raw_leo` arrays where defined; fix tests; add tests for group folds (no group overlap between query fold and context) and raw_leo argument checks.
Accept: full scientific suite passes in `.venv-tfm`; minimal suite passes in `.venv`; `tools/check_setup.py` PASS; `sync_skills --check` MATCH.

## T2 — Write `prereg/PREREGISTRATION_V2_1.md` (do not edit v1 or v2)
Based on v2 + the four decisions + the amendment proposal where consistent with them. Must state: estimands, primary/secondary comparisons, per-table reporting rule (no binary verdict), data/subsample/seed streams (incl. that injection seed = run seed), arms, score semantics (tail probability, not density), coverage/unsupported policy, failure policy, compute accounting, LEO keys and their limitation (keys read from dirty values), environment is NOT isolated (system site-packages; record provenance), data-access disclosure (descriptive profiles of all five tables seen; dev = movies_1 only), deviations from v1 and v2.
Accept: internally consistent with code and `analyze_v2.py`; no results referenced.

## T3 — Development run on `movies_1` only
Run `run_v2.py --table movies_1` for one seed per condition (development role). Check artifacts, timing (estimate full-grid wall time), failures, analysis on dev artifacts in a scratch output. Fix bugs found (re-run T1 tests). Record in `docs/EXPERIMENT_LOG.md` as development.
Accept: complete artifacts, no unexplained failures, wall-time estimate recorded.

## T4 — Freeze
Create `prereg/PREREGISTRATION_V2_1.sha256` and `.freeze.json` covering all `REQUIRED_FREEZE_FILES`; record hashes + timestamp in `docs/EXPERIMENT_LOG.md` before any confirmatory run. Any later code change = new amendment + new freeze, documented.

## T5 — Confirmatory grid
4 tables × 3 conditions × seeds 0–4, both models. Run in parallel processes only if outputs/threads do not interfere; keep failed/partial attempts. Copy run metadata, metrics inputs and SHA-256 of `scores.npz` into a tracked archive (`experiments/archive/v2_1_runs/`), raw npz may stay local if large.
Accept: complete grid or every failure documented; no reruns that replace failures silently.

## T6 — Frozen analysis
Run `analyze_v2.py` once into `experiments/archive/v2_1_analysis/`. Update `docs/CLAIM_EVIDENCE.md` (every number → run IDs/artifact/commit/config), `docs/EXPERIMENT_LOG.md`, `docs/STATE.md`. Negative or mixed results are reported as they are.

## T7 — Manuscript (English, LNCS, 12–15 pages incl. references)
Rewrite `paper/main.tex` (+ `MANUSCRIPT.md` companion) from T6 artifacts only: problem, related work (verified citations only; extend via primary sources and record in `docs/literature/CITATION_AUDIT_20261030.md`), method with pseudo-code and complexity, protocol and deviations, results with tables/figures generated by script, per-table uncertainty, negative results, threats/limitations, reproducibility, AI disclosure, TabPFN attribution. Vendor the current official Springer `llncs.cls`/`splncs04.bst` (record source/licence) or document the build source; build PDF, open it, record page count.
Accept: every number traceable; no claim beyond evidence; PDF builds.

## T8 — Self-check before handing back
Run the checks, update `docs/STATE.md`, write a handoff (template `docs/templates/HANDOFF.md`) with source identity, checks, runs, open items. Claude will then dispatch an independent read-only review.

Escalate to the coordinator (stop and write the question in your handoff) if: a decision outside 1–4 is needed, a cost/licence/new-download question arises, or results suggest changing the protocol after freeze.
