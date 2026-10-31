# V2.1 manuscript self-check — working assessment

Owner: Codex, also the implementer/writer. **Not independent peer review.**
Framework: reviewer-astar; no official editorial decision or acceptance probability.
Scope authorized by the author: internal research, verification and manuscript editing.
No submission or external manuscript upload. Author's final scholarly verification pending.

## Snapshot and evidence

- Executed measurement/analysis source: frozen map
  `c37e39ab8168ed2fda38e9a6e952a15114bda4faa595356c7aeeb5f633bf5678`,
  parent HEAD `0aff63e`, exact hashes in preregistration freeze. Still matches after
  manuscript-only editing. No frozen source is edited during execution.
- Manuscript sources: `paper/main.tex`, `paper/sections/`, `paper/references.bib`.
  These remain a draft while the grid and analysis are incomplete. PDF currently
  method/protocol only; results placeholders are deliberately explicit.
- Development evidence: three movies_1 conditions, one seed, both models;
  audit4,480 contexts, no recorded fit failures. Not confirmatory evidence.
- Confirmatory evidence at review start: first11 units completed, no recorded fit
  failures; performance effects not inspected. Complete60 required before analysis.
- Primary sources actually inspected are itemized in the citation audit. Search hits
  or verified metadata alone are not used as method support.

## Strongest defensible contribution

A controlled empirical test of one target-specific context-removal rule for cell
rankings with fixed pretrained weights. The nested first pass isolates outer queries;
matched-count random removal separates targeted selection from context-size change.
The study exposes compute cost, unsupported targets, rare-valid alarms, observed-key
boundary sensitivity and actual failures. Its value depends on measured evidence and
analysis, including negative or heterogeneous results.

## Findings and observable closure

1. **P1 — Incomplete empirical evidence (OPEN).** No finished-study abstract/conclusion
   is defensible until all60 units, original attempts, input/context/split audit and
   reproducible analysis are complete. Close with actual artifacts and claim ledger;
   never infer results from development or first completed units.
2. **P1 — Broad novelty would be unsupported (PROSE FIXED, final recheck pending).**
   DDC/cellGMM already address cellwise contamination; TabPFN already supports
   conditional density estimation; TACTIC studies contaminated contexts; QualiTab
   compares clean contexts; L2C2 addresses TFM cleaning and LUCoS selects contexts
   without labels before annotation. Current related work cites these differences.
   No “first TFM cleaning”, generic selection novelty, or SOTA claim is allowed.
3. **P2 — Backbone comparison also changes feature treatment (PROSE FIXED).**
   Frozen LGBM adapter ignores categorical indices and treats frequency codes
   numerically; TabPFN receives categorical indices. Disclose this in limitations
   and avoid interpreting differences as pretrained weights alone.
4. **P2 — Row dependence and transduction (PROSE FIXED).** Final encoder observes
   dirty queries; row folds allow related records; observed-key LEO can misidentify
   latent entities. Bootstrap intervals condition on predictions and can understate
   dependence. No population-wide inferential verdict, conformal validity or
   fully inductive claim. Final result text must retain these qualifications.
5. **P2 — Compute-matched accounting is limited (PROSE FIXED).** Random scores
   do not consume ranks; adding nested cost is an accounted control, not a measured
   extra accuracy arm or the best possible use of equal compute. Nested work remains
   included in purification. No double-counting or free-preparation claim.
6. **P2 — Baseline identities/support (IMPLEMENTED; full-data check pending).**
   DDCcore/LGBM/rawTFM do not reproduce DDC/CDC/uTabPFN. RobustZ and DDCcore
   numerical support differs from frequency/IF and conditional support. Export
   method-specific counts, full-universe AP and seed-level undefined endpoints.
7. **P2 — Failure penalty can help AP (PROSE FIXED; measured check pending).**
   Maximally suspicious failed cells may coincide with true errors. Full failure
   masks/counts must accompany metrics; zero failures may be claimed only after
   complete artifact review. Nonfinite nested returns are now logged and tested.
8. **P2 — Scope of mechanism interpretation (PROSE FIXED).** Injection is string
   corruption with coupled seeds; oracle substitutes all context features, not
   target values alone. Neither contrast isolates every causal source of degradation.
   No automatic pivot or parameter change after viewing results.
9. **P1 for external use — Author/policy details (PARTIAL).** Author supplied name,
   institution and ORCID; checksum valid. Email suffix is being clarified. Required
   AI disclosure and weight attribution retained. Actual author verification and
   future venue-specific anonymity/disclosure rules remain outside an internal PASS.
10. **P2 — Text originality review is bounded (OPEN until final prose).** Local
    exact-phrase screen has no12word match against11 primary texts, but this is
    not plagiarism certification and does not test unsearched/semantic overlap.
    Inspect attribution and rerun on final prose. No AI-detector claim.

## Remaining acceptance work

Complete grid; preserve errors; audit actual inputs/splits/contexts; compare a separate
frozen verification rerun; rerun numerical analysis into a new directory and compare;
generate result tables/figures directly from artifacts; write outcome-bounded results,
abstract and conclusion; update claim-evidence map; compile/render every final page,
check12–15 pages and reference support. Mark independent review as pending unless it
actually occurs. This checklist itself supplies no research-performance evidence.
