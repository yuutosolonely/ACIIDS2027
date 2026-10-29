# Preregistration Protocol — CRIC-ED / ACIIDS 2027

**Worker:** W4-METH (Methods & Statistical Design Specialist)  
**Worktree:** `C:/Users/ngoda/orca/workspaces/ACIIDS2027/methods`  
**Date Frozen:** 2026-10-29  
**Status:** **FROZEN PRIOR TO CONFIRMATORY EVALUATION**  

---

## 1. Formal Mathematical Formulation

Let $\tilde{X} \in \mathcal{X}^{N \times D}$ be a dirty tabular dataset composed of $N$ rows and $D$ heterogeneous columns (numerical and categorical). Ground-truth error matrix $Y^* \in \{0, 1\}^{N \times D}$ is hidden from the detector during inference.

### 1.1 Information Boundaries & Cross-Fitting Invariants
For each target cell $(i, j)$ with $i \in \{1, \dots, N\}$ and $j \in \{1, \dots, D\}$:
1. **Target Feature Exclusion:** The target attribute $j$ is excluded from the input conditioning vector $\tilde{x}_{i, -j}$.
2. **Leave-Entity-Out (LEO) Cross-Fitting:** Let $\mathcal{E}(i)$ denote the entity group containing row $i$. The candidate in-context demonstration pool is strictly bounded by:
   $$\mathcal{C}_{(-i)} = \{ k \in \{1, \dots, N\} \mid \mathcal{E}(k) \neq \mathcal{E}(i) \}$$
   Row $i$ (and its co-entities) strictly never appears in its own context.

### 1.2 Training-Free Conditional Likelihood Scoring
Using a frozen Tabular Foundation Model parameter vector $\theta$:
- **Categorical Attributes:**
  $$S_{i,j}^{\text{cat}} = -\log P_\theta(X_{i,j} = \tilde{x}_{i,j} \mid \tilde{x}_{i, -j}, \mathcal{C}_{(-i)})$$
- **Continuous Numerical Attributes:**
  Using the predicted parametric or quantile distribution $\hat{F}_{i,j}(z) = P_\theta(X_{i,j} \le z \mid \tilde{x}_{i, -j}, \mathcal{C}_{(-i)})$, the standardized deviance is defined as:
  $$S_{i,j}^{\text{num}} = -\log \hat{f}_{i,j}(\tilde{x}_{i,j}) \quad \text{or} \quad \frac{|\tilde{x}_{i,j} - \hat{\mu}_{i,j}|}{\hat{\sigma}_{i,j} + \epsilon}$$

---

## 2. Context Intervention & Influence Trimming Algorithm

1. **Context Initialization:** Sample a base context $\mathcal{C}_0 \subset \mathcal{C}_{(-i)}$ of size $K$.
2. **Influence Scoring:** For each exemplar $m \in \mathcal{C}_0$, evaluate its contribution to the conditional variance:
   $$I(m) = \left\| \nabla_{\tilde{x}_{m}} \log P_\theta(\tilde{x}_{i,j} \mid \tilde{x}_{i,-j}, \mathcal{C}_0) \right\| \quad \text{or proxy variance under leave-one-out subsampling}$$
3. **Controlled Pruning with Rare-Valid Guard:**
   - Remove the top $q\%$ highest-leverage exemplars.
   - **Guardrail:** Exemplars matching rare-valid patterns ($\le 1\%$ marginal frequency) are immune from pruning to prevent purging legitimate domain diversity.
4. **Matched-Random Control:**
   For every trimmed context $\mathcal{C}_{\text{trim}}$ of size $K(1 - q)$, an ablation context $\mathcal{C}_{\text{rand}}$ of identical size $K(1 - q)$ is sampled uniformly at random.
   **Null Hypothesis ($H_0$):** $AUPRC(\mathcal{C}_{\text{trim}}) = AUPRC(\mathcal{C}_{\text{rand}})$. If $H_0$ is not rejected, trimming efficacy is unproven.

---

## 3. Multi-Tier Benchmark Baselines

All baselines are evaluated on the exact same universe of eligible cells:
1. **Tier 1 (Classical Coordinate-Wise):**
   - **DDC (Detecting Deviating Data Cells)**: Technometrics 2018 (numeric cells).
   - **Column-wise Isolation Forest**: Scikit-Learn standard baseline.
2. **Tier 2 (Modern Competitors):**
   - **CDC (Imputation + Conformal Calibration)**: AISTATS 2024.
   - **uTabPFN (Raw In-Context Likelihood)**: Random context, zero trimming.
3. **Tier 3 (Diagnostic Controls):**
   - **Clean-Context Oracle**: Evaluates TFM likelihood when context is guaranteed 100% clean (upper bound).
   - **Leaky Control**: Query row deliberately leaked into context (leakage floor).

---

## 4. Evaluation Universe, Metrics & Coverage Penalty

1. **Eligible Cell Universe:** All non-primary-key cells $M = N \times (D - 1)$.
2. **Primary Metric:** Cell-Level Area Under Precision-Recall Curve (AUPRC).
3. **Secondary Metrics:** Precision@$k$, Recall@$k$, F1@$k$ for audit budgets $k \in \{0.01, 0.05, 0.10\} \times M$.
4. **Coverage Penalty Rule:** If an algorithm outputs `NaN`, inf, or crashes on cell $(i,j)$, the cell is assigned the maximum anomaly score ($S_{i,j} = \max S + 1.0$). Zero cells may be omitted from the denominator.
5. **Statistical Significance:** Cluster-preserving bootstrap over row entities (1,000 resamples), reporting 95% Confidence Intervals.

---

## 5. Explicit Stop / Pivot Falsification Criteria

- **Rule 1 (Baseline Superiority):** If raw uTabPFN or CDC achieves higher macro AUPRC than CRIC-ED on the pilot benchmark: **STOP CRIC-ED and activate Fallback Framing 1 (CS-ED)**.
- **Rule 2 (Rare-Valid Preservation):** If Influence Trimming increases the False Positive Rate on rare-valid cells by $>20\%$ compared to raw uTabPFN: **STOP Trimming and pivot to Selective Abstention (CS-ED)**.
- **Rule 3 (Compute Feasibility):** If CPU inference latency exceeds 3.0 seconds per cell: **STOP TFM and activate Fallback Framing 2 (Dual-ED)**.
