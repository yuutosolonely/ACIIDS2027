# Handoff Report — Task T1.2: Literature & Novelty Falsification Audit

- **Task ID:** T1.2
- **Worker:** W1-LIT (Literature & Novelty Specialist)
- **Worktree:** `C:/Users/ngoda/orca/workspaces/ACIIDS2027/literature`
- **Branch:** `yuutosolonely/literature`
- **Status:** **COMPLETE**

## 1. Files Changed / Added
- `docs/literature/CLOSEST_WORK_MATRIX.md` (Created)

## 2. Key Findings & Novelty Boundaries
- **Task Disambiguation:** Strictly separated Cell-ED ($N \times D$) from Row Anomaly ($N \times 1$), Label Error ($N \times 1$ target), and Imputation.
- **Novelty Boundaries:**
  - Banned false claims: TFM anomaly scoring is not novel; cross-fitting is not novel.
  - Cleared genuine delta: Investigating cell-level self-contamination mechanisms, paired context intervention, and preserving rare-valid subgroups under training-free influence trimming.
- **Falsification & Fallback Rules:** Established strict triggers to pivot to Fallback Framing 1 (CS-ED) or Framing 2 (Dual-ED) if pilot gains are indistinguishable from matched-random removal or harm rare-valid groups.

## 3. Recommended Actions for Coordinator
- Approve Gate G1 Literature & Novelty criteria.
- Direct Methods Worker (W4) to incorporate rare-valid controls into the preregistration protocol.
