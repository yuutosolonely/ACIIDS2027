# V2.1 pre-freeze reconciliation — 2026-10-30

Owner: Codex integration. Source HEAD `0aff63e` + integrated WIP.
This is an implementation checklist, not independent peer review or a gate PASS.

- Accepted row-primary/LEO-secondary/descriptive/nested-cost choices agree with scorer,
  runner and candidate specification. Historical v1/v2 and inactive v3 remain separate.
- Real development execution is in progress. Freeze and confirmatory scoring remain closed.
- Code read found reporting omissions before freeze: the candidate names `leaky - raw`
  but analysis currently omits that contrast; seed-level metrics and rare-valid/support
  counts need explicit export; the systematic-minus-random oracle-gap description
  needs a derived descriptive entry; baseline support must not inherit conditional
  coverage as if it were method-specific. These are reporting corrections, not detector
  parameter changes. Apply after the current development processes finish, preserving
  their original code hashes and recording any analysis-only source transition.
- Planned validation: complete dev artifacts, input/context/AP audit, per-condition
  failure review, source-before/after identity check, full tests after reporting repair,
  final v2.1 freeze including dirty-only outer split manifest, then all 60 units.
- Exact-byte source manifests distinguish uncommitted integration from parent Git HEAD.
  Working-tree text uses LF; immutable historical artifacts are not normalized.
- The inherited scientific environment is usable with declared version checks but is
  not an isolated, complete wheel-level reproduction environment. Report this limitation.

Closure before freeze: all three development conditions completed, no recorded fit
failures; saved-artifact audit verified 4,480 contexts and AP/input identities. Reporting
omissions above corrected; original and revised development analyses retained separately
with explicit source transition. A JSON scalar failure during replay was preserved and
fixed with a strict serialization test. Scorer now logs nonfinite returns in both stages.
Scientific suite 71 passed; minimal 37 passed/4 skipped; setup PASS; mirror MATCH.
Resource configuration fixed prospectively at four processes x two threads, cache0.
V2.1 freeze and confirmatory runs can now proceed under the recorded author decisions.
