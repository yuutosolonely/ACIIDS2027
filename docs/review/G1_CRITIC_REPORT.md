# Independent Critic Protocol Audit & Gate G1 Verdict

**Reviewer:** W6-CRIT (Independent Scientific Critic)  
**Worktree:** `C:/Users/ngoda/orca/workspaces/ACIIDS2027/review`  
**Date:** 2026-10-29  
**Reviewed Artifacts:**
- `docs/context/conference/CONFERENCE_AUDIT.md` (W2-CONF)
- `docs/literature/CLOSEST_WORK_MATRIX.md` (W1-LIT)
- `data/DATA_CARD.md` & `data/manifests/raha_benchmark_manifest.json` (W3-DATA)
- `prereg/PREREGISTRATION.md` (W4-METH)

---

## 1. Adversarial Audit Findings

### Finding 1: The "Swapping the Imputer" Novelty Trap (High Risk)
- *Vulnerability:* In `docs/literature/CLOSEST_WORK_MATRIX.md`, CDC (AISTATS 2024) is identified as the closest cell-level competitor. CDC combines an imputer with conformal residual thresholding. If CRIC-ED is presented simply as "CDC with TabPFN instead of MissForest", top-tier reviewers at ACIIDS/LNAI will reject the paper as an incremental empirical comparison.
- *Remedy Requirement:* The primary framing must strictly center on **the pathology of Self-Contamination under In-Context Learning**. The contribution is not the likelihood function itself, but the discovery of **Context Normalization** (where in-context errors distort $P(X_j \mid X_{-j})$) and the **Influence-Aware Intervention** that fixes it while preserving rare-valid records.

### Finding 2: Compute Feasibility under Local CPU & 70-Hour Deadline (High Risk)
- *Vulnerability:* The official deadline is 31 October 2026 23:59 AoE (~70 hours remaining). The budget is strictly $0.00 (CPU local). TabPFN inference requires running $D$ separate forward passes for every single row. For a table of 1,000 rows and 15 columns, that is 15,000 forward passes. On a consumer CPU, if each forward pass takes 0.2s, that is 3,000 seconds (50 minutes) per table, which scales rapidly if 5 seeds and multiple ablations are run.
- *Remedy Requirement:* The pilot protocol (Gate G2) **MUST** benchmark per-cell latency immediately on CPU. If latency exceeds the budget, the project must immediately switch to **Fallback Framing 2 (Dual-ED: Robust Coordinate-Wise Deviance + Fast Local Association)** which executes in seconds on CPU without neural forward passes.

### Finding 3: The Rare-Valid Collateral Damage Risk (Moderate Risk)
- *Vulnerability:* Context trimming based on high influence or high deviance risks pruning legitimate outlier clusters (rare-valid patients, niche craft beers). If trimming improves overall AUPRC by simply removing hard legitimate cases, it produces an inflated score that is clinically or practically dangerous.
- *Remedy Requirement:* Preregistration Rule 2 (Rare-Valid Preservation) is approved and must be strictly enforced: if FPR on rare-valid cells increases by $>20\%$, the intervention is considered a failure.

### Finding 4: Leakage Isolation Invariant (Sound)
- *Verification:* The separation into `dirty.csv` (input to detector) and `errors.csv` (input strictly to evaluation) combined with Leave-Entity-Out (LEO) cross-fitting is methodologically airtight. No target row or entity cluster is permitted to contaminate its own demonstration pool.

---

## 2. Gate G1 Verdict

### Verdict: **CONDITIONAL PASS (GO TO PILOT G2 WITH RESTRICTIONS)**

1. **Protocol Approved:** The mathematical formulation, LEO cross-fitting, matched-random ablation controls, and multi-tier baselines in `prereg/PREREGISTRATION.md` are approved.
2. **Pilot Constraints:**
   - Execute Pilot G2 strictly on a tiny synthetic fixture (`toy_mixed`) and a 100-row subset of `beers` on CPU.
   - Profile exact wall-clock latency per cell.
   - If TabPFN fails CPU throughput or yields zero gain over matched random removal, activate Fallback Framing immediately.
