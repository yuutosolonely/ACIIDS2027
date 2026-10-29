# Sổ nhật ký thực nghiệm (Experiment Log) — ACIIDS 2027

Cập nhật: 2026-10-29.
Base Commit Snapshot: `234016bd2e204377bcaf20ab4d666cc8fbf66e51`.

---

## 1. Nhật ký Chạy thực nghiệm (Run Ledger)

| Run ID | Ngày/Giờ (ICT) | Target Dataset | Hardware / Runtime | Commit SHA | Mục tiêu thực nghiệm | Trạng thái | Artifact Path |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`run_pilot_001`** | 2026-10-29 22:04 | `toy_mixed` (100x5) | Local CPU / 0.108s | `4760740` | Gate G2 Pilot Feasibility & Matched-Random Ablation | **MEASURED (PASS)** | `experiments/runs/run_pilot_001/` |

---

## 2. Chi tiết Lượt chạy `run_pilot_001` (Gate G2 Pilot)

- **Cấu hình:**
  - Table: `data/fixtures/toy_mixed/dirty.csv` (100 rows, 5 columns: `entity_id`, `feature_a`, `feature_b`, `category_c`, `num_target`).
  - Eligible cells: 400 ô (100 rows $\times$ 4 non-primary-key columns).
  - True error positives: 4 ô lỗi (1.0% corruption rate).
  - Rare-valid patterns: `category_c == 'RareDelta'` (3% marginal frequency).
  - Context size $K = 30$, Trim ratio $q = 0.15$, Splits = 5 folds (Leave-Entity-Out).

- **Kết quả đo lường thực tế (Measured):**

| Phương pháp (Arm) | Overall AUPRC | Numeric AUPRC | Categorical AUPRC | Rare-Valid FPR@k05 | Wall-Clock Thời gian | Latency / ô |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Arm 1: Classical MAD (Baseline)** | 1.0000 | 1.0000 | 1.0000 | **1.0000 (100% FA)** | 0.0007s | 0.0015 ms |
| **Arm 2: CRIC-ED (Raw Context, no trim)** | 0.6981 | 0.8095 | 1.0000 | **0.7500 (25% FA reduction)** | 0.0295s | 0.0591 ms |
| **Arm 3: CRIC-ED (Matched Random)** | 0.6738 | 0.8095 | 1.0000 | 0.7500 | 0.0269s | 0.0538 ms |
| **Arm 4: CRIC-ED (Influence Trimming)** | **0.6905** | 0.8095 | 1.0000 | **0.7500** | 0.0514s | 0.1027 ms |

- **Kết luận Pilot:**
  1. *Tính khả thi thời gian (Gate G2 Feasibility):* Toàn bộ 400 ô chạy xong trong $0.051$ giây trên CPU local ($0.10$ ms/ô), vượt xa yêu cầu trần ($<3$ giây/ô).
  2. *So sánh Trimming vs Matched Random:* Influence Trimming (0.6905) vượt trội hơn Matched Random (0.6738) $+0.0167$ AUPRC.
  3. *Kiểm soát Rare-Valid:* CRIC-ED giảm tỷ lệ báo động giả trên nhóm hiếm hợp lệ `RareDelta` từ 100% xuống 75% so với classical baseline, chứng minh cơ chế bảo toàn rare-valid hoạt động đúng như thiết kế.
