# Coordinator checkpoint — Claude → Codex (paused 2026-10-30 08:55 ICT)

Author instruction: "tạm dừng lưu check point và bàn giao cho codex". Claude has paused all
coordination; Codex takes over (coordination and execution). Nothing was submitted, pushed or
frozen. NO-GO for ACIIDS 31 Oct 2026 remains in force.

## Source identity
- Main repo `F:/competitions/ACIIDS/ACIIDS2027`: branch **`coord/v2-1-base`** (created from
  `main` @ `06ded05`). Base snapshot commit `17c2676` (audit, decisions, candidate v2 pipeline,
  task cards). This checkpoint commit adds this file and `docs/handoffs/coord_prompts_20261030/`.
  `main` itself is unchanged. No push.
- Worktrees (created on author request 2026-10-30), each on its own branch from `17c2676`:

| Worktree | Branch | Checkpoint commit | State when paused |
|---|---|---|---|
| `F:/competitions/ACIIDS/ACIIDS2027_wt/impl` | `codex/impl` | `a7560c1` WIP | analyze_v2.py per-table rewrite in progress (+319/−), run_v2/conditional/benchmark/v2_contract edits, new `tests/test_v2_reporting.py`. Tests NOT verified. T3 dev run not started (unverified) |
| `F:/competitions/ACIIDS/ACIIDS2027_wt/prereg` | `codex/prereg` | `32d4bc2` WIP | draft `prereg/PREREGISTRATION_V2_1.md` (CANDIDATE, unreviewed) |
| `F:/competitions/ACIIDS/ACIIDS2027_wt/lit` | `codex/lit` | `d2fe584` WIP | `docs/literature/PRIMARY_METADATA_20261030.json` (Crossref/arXiv lookups in progress) |
| `F:/competitions/ACIIDS/ACIIDS2027_wt/paper` | `codex/paper` | none (no changes) | not started |

  WIP commits were made by the coordinator to preserve interrupted work; they are not reviewed.
- Each worktree has directory junctions (gitignored) to the main repo: `data/raw`,
  `checkpoints`, `.venv-tfm`, `.venv` — treat as read-only.
- Worker sessions were `codex exec` (codex-cli 0.163.0, sandbox workspace-write; lit with
  network). Session IDs: impl `01a18a7d-c802-7061-8d88-e64590bbefc8`, prereg
  `01a18a7d-c9fd-7941-9d53-791d48b21df2`, lit `01a18a7d-ce9b-70c2-a265-ed21df813710`, paper
  `01a18a7d-d487-70b1-b32e-f439a1916f5d` (resumable with `codex exec resume <id>` from the same
  worktree, or restart from the prompts). All worker processes were stopped; none is running.
- Prompts given to workers: `docs/handoffs/coord_prompts_20261030/` (`common.md` + `task_*.md`).
  Full task list: `docs/handoffs/TASKS_CODEX_V2_1_20261030.md` (T1–T8). Raw worker logs remain
  local in `.cache/coord/` (gitignored).

## Accepted author decisions (authoritative record: `docs/DECISION_BRIEF_20261030.md`)
NO-GO for ACIIDS 2027; Path A (TabPFN-2, `tabpfn==9.2.0`, pinned checkpoints, CPU, $0; v2 weights
ungated, no PriorLabs account); row-level cross-fitting primary + leave-entity-out secondary
(keys hospital/provider_number, flights/flight, beers/brewery_id); per-table descriptive
statistics, no binary cross-dataset verdict; shared nested pass-1 with compute-matched reporting;
Claude only coordinates, Codex executes; work split across worktrees.

## New blocker found at pause (P1, must fix before any freeze)
`core.autocrlf=true` in this repo: files checked out in the worktrees get CRLF line endings, so
their SHA-256 differ from the LF bytes recorded in manifests (verified:
`docs/context/team_package/IDEA_L3_LexConsolidate.md` c97e5e19… in main vs 433f5172… in
`_wt/impl`; the impl worker's log shows the resulting manifest mismatch). Any freeze/hash check
run inside a worktree will be inconsistent with the main repo. Decide one policy (e.g. a
`.gitattributes` with `eol=lf` for hashed text files, or `core.autocrlf=false` + re-checkout of
the worktrees) and record it before T4.

## Next actions for Codex (in order)
1. Decide/fix the line-ending policy above; re-checkout worktrees if needed.
2. Resume or restart the four workers; review each WIP diff before continuing (nothing in them
   is accepted yet).
3. Merge accepted worker branches into `coord/v2-1-base` (only owned files; resolve conflicts
   in favour of the decision brief); run the full suites.
4. Continue T3 (dev run on movies_1) → T4 (freeze) → T5 (confirmatory grid) → T6 (frozen
   analysis) → T7 (manuscript) → T8, as specified in the task cards. Shared docs (STATE,
   EXPERIMENT_LOG, CLAIM_EVIDENCE) were last updated on `17c2676`; they do not yet mention the
   worktrees or this pause.
5. Escalate to the author for anything outside the accepted decisions (costs, new downloads,
   protocol changes after freeze, submission).
