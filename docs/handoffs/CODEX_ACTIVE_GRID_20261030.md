# Active research checkpoint — Codex continuation

This file is a continuation checkpoint, not completion or submission approval.
**Latest05:00UTC:** goal tool reports `usageLimited`; do not mark it complete or
invent a resume. Existing local CPU jobs continue. Automatic postprocessor session
**80142** now owns downstream audit/analysis/generated-paper outputs. It waits for
the full grid, then runs the frozen audit, split audit, analysis twice with numeric
equality checks, artifact generation and a data-dependent internal draft/build.
Read `experiments/archive/v2_1_postprocess/status.json` before doing any of those
commands manually. Do not race it or overwrite its outputs. Prepared scripts are
syntax-checked; downstream real execution remains pending until the grid finishes.
Final numerical/interpretive/citation/visual review remains necessary after it ends.
Current grid12/60, zero run errors/recorded fit failures. Verification rerun PASS_EXACT.
Author email clarification is still pending; ORCID/name/institution are in LaTeX.
User asks for a complete research paper within roughly eight hours from02:24UTC,
and explicitly requires fully verified experiments. Target roughly10:24UTC;
do not reduce the grid or fabricate completion if execution takes longer.

## Active processes

- Full grid: exec session **49575** running
  `.venv-tfm/Scripts/python.exe experiments/tfm/run_grid_v2_1.py --workers 4 --threads 2`.
  Started02:59:15UTC. Output `experiments/runs/v2_1/`; tracked archives/status
  `experiments/archive/v2_1_runs/`. At04:38–04:44UTC,11/60 complete, no run errors
  or recorded fit failures. Runtime highly variable: hospital real seed0~75min,
  flights~12min, rayyan~14min, beers~23min. Do not inspect partial effects/tune.
- Verification rerun: exec session **80238**, flights/real/seed0, same frozen
  source/threads2; started04:24:40UTC, still nested stage at last check.
  Output `experiments/validation/v2_1_replication/`; excluded from grid statistics.
  Temporary fifth process is disclosed as host-concurrency timing deviation.
  **Update04:45UTC:** completed with zero recorded failures; comparison PASS_EXACT,
  all saved arrays and contexts identical. Comparison JSON under experiments/validation.
  Session80238 is finished; do not poll it again or rerun/overwrite its outputs.
- No other agents or Claude running, per user. Codex solely integrates/executes.
  No new agents, worktrees, commits, pushes, paid services or submissions.

## Frozen source — DO NOT EDIT WHILE EXECUTING

Parent HEAD `0aff63e292da7a071368f594015089d5d746fa05`, branch `coord/v2-1-base`.
Uncommitted source identified by complete exact hash map; freeze at02:58:59UTC.
Protocol `eea8f0ee8b217458a82b073bac5261f43ab8056e1b4eb32a170e5aece061543a`.
Snapshot `c37e39ab8168ed2fda38e9a6e952a15114bda4faa595356c7aeeb5f633bf5678`.
Freeze files `prereg/PREREGISTRATION_V2_1.{md,sha256,freeze.json}` and split manifest.
Accepted PathA, row-primary, LEO-secondary, descriptive per-table, nested costs.
V3/strict_scorer remains inactive. Historical v1/v2 unchanged. $0/localCPU only.

## Completed evidence

- WIP integrated exactly from Claude's paused worker commits; integration manifest
  in `docs/handoffs/WIP_INTEGRATION_20261030.json`. LF policy in `.gitattributes`;
  immutable archive/data/binary bytes preserved, no mass normalization.
- Development movies_1 seed0 all3 conditions, both models completed with zero
  recorded fit failures. Audit4,480 contexts. Archive `v2_1_development/`.
  Original and reporting-reconciled analyses retained in experiments/validation.
  One pre-freeze JSON int64 replay error preserved; fixed before freeze.
- Last full scientific tests71 passed; minimal37 passed/4skip; static setupPASS,
  skillsMATCH; gitdiff whitespace clean (CRLF warnings only).
- `experiments/validation/v2_1_progress_artifact_audit_s0.json`: actual first
  real seed0 on all4 tables,4,740 contexts verified, zero recorded failures.
  This is PARTIAL TECHNICAL CHECK ONLY, not complete-grid analysis.
- Pinned TFM capability and source licences checked earlier; no new weights.
  Environment is inherited/nonisolated; distribution pins checked, no full wheels freeze.

## Paper/literature

- `paper/main.tex` and five sections drafted; results/conclusion explicitly pending.
  Latest built PDF11 pages before results, official Springer LNCS2.25 template.
  Build script copies template into cache and renders pages with PyMuPDF.
  Current source has author name/institution/ORCID but latest PDF predates that edit.
  Old negative-fixture manuscript archived byte-identically.
- `paper/MANUSCRIPT.md` generated from same LaTeX via installed Pandoc3.12.1;
  regenerate after final edits with `tools/sync_manuscript.py`.
- Bibliography/related work extended using primary sources: DDC, CDC, TabPFN,
  TACTIC, ZeroED, Raha, IF, LGBM, QualiTab, L2C2, LUCoS, cellGMM. No reference
  reproduction or broad novelty claim. Per-claim support in citation audit.
- Eleven public sources cached locally in `.cache/literature_primary/` for overlap
  screening. Zero12word matches at current draft scope; not a plagiarism certificate.
  Preserve required AI disclosure and TabPFN attribution; no AI-detector evasion claim.
- `docs/review/V2_1_MANUSCRIPT_SELF_CHECK_20261030.md` is an internal self-check,
  explicitly not independent peer review. Key limitations already disclosed: LGBM
  code features treated numerically vs categorical indices forTFM; transductive
  final encoder; row dependence; accounted random compute not best equal-budget
  alternative; failure penalty can improveAP; injection/oracle causal limits.

## Author reply / pending clarification

User supplied one author: Ngo Dang Trong Hieu, Ton Duc Thang University,
ORCID0009-0007-1773-3680 (checksum valid, no external account ownership claim).
Email as sent: ngodangtronghieu.dl2021@gmail.comm. Async clarification pending
whether `.com` or `.comm`; do not silently correct. Record `paper/AUTHOR_METADATA.json`.
Update `main.tex` with confirmed email, rerun PDF/Markdown later. Human final scholarly
verification remains pending; never claim authors have reviewed what they have not.

## Next execution actions

**Superseding ownership note:** steps3–5 below are now scheduled by the local
postprocessor (session80142), including empirical draft generation and PDF/Markdown
build. Inspect its status/logs, do not duplicate those steps. If it fails, preserve
all artifacts and diagnose the recorded stage before repairing anything. Frozen
measurement/analysis files stay unchanged. Its end state is review_pending, not
paper acceptance. The goal remains usageLimited until user/system resumes it.

1. Poll grid and verification sessions without terminating them. Archive all errors.
2. When verification finishes, run `tools/compare_replication.py` with original
   `experiments/runs/v2_1/flights__real__s0`, replica under validation, output
   `experiments/validation/v2_1_replication_comparison.json`. Do not replace originals.
3. After all60 finish: frozen `tools/audit_v2_artifacts.py` over grid, output
   `experiments/archive/v2_1_artifact_audit.json`; additional read-only
   `tools/check_frozen_splits.py`; analysis once into `experiments/archive/v2_1_analysis/`.
4. Repeat numerical analysis into fresh validation directory; compare resultsJSON
   and CSVs byte-for-byte (PDF timestamps can differ). No source edits to force PASS.
5. `tools/generate_paper_results.py` is prepared, not yet executed, requires full
   analysis plus artifact audit. It generates7tables,2figures and numerical macros
   under paper/generated. It is typesetting code outside frozen measurement source.
6. Write final results/abstract/conclusion from full artifacts only. Keep negative
   or mixed findings, bootstrap limits and baseline identities. Update claim ledger.
7. Build/render all final pages, adjust manuscript layout to12–15pages includingrefs,
   verify every number and citation. Rerun local overlap screen on final prose.
8. Update STATE/EXPERIMENT_LOG/reproducibility/handoff with actual results and limits.
   Active goal remains unfinished until empirical paper verified; no submission.
