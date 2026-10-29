# Claim → Evidence Ledger — ACIIDS 2027

Cập nhật: 2026-10-29.
Nguyên tắc: Mọi khẳng định nghiên cứu khoa học phải truy nguyên trực tiếp về Run ID, artifact thực nghiệm, source revision và config cụ thể. Phân định rạch ròi giữa Đã đo lường (Measured), Nguồn công bố báo cáo (Source-reported), Giả thuyết (Hypothesis), Đề xuất (Proposal) và Đang chờ thực hiện (Pending).

---

## 1. Trạng thái các Claim của Đề tài (Idea 3 / CRIC-ED)

| Claim ID | Nội dung khẳng định | Trạng thái hiện tại | Loại bằng chứng / Nguồn chứng minh | Ghi chú & Rào cản |
| :--- | :--- | :--- | :--- | :--- |
| **CLM-01** | CRIC-ED khả thi về mặt tính toán và có thể chạy training-free trên CPU local mà không cần GPU trả phí. | **MEASURED (Đã đo)** | `experiments/runs/run_pilot_001/` (Latency 0.10 ms/ô trên CPU). | Chứng minh tính khả thi kỹ thuật cho Gate G2 theo ngân sách $0.00. |
| **CLM-02** | Influence-Aware Trimming đạt AUPRC cấp ô cao hơn Matched Random Removal khi cùng kích thước context. | **MEASURED (Đã đo sơ bộ)** | `experiments/runs/run_pilot_001/` (0.6905 vs 0.6738 trên toy_mixed). | Xác nhận hiệu ứng trimming không chỉ đơn giản là hiệu ứng thay đổi kích thước context. |
| **CLM-03** | In-Context Error Detection giảm tỷ lệ báo động giả trên các mẫu hiếm hợp lệ (rare-valid) so với Classical MAD. | **MEASURED (Đã đo sơ bộ)** | `experiments/runs/run_pilot_001/` (Rare-valid FPR 0.75 vs 1.00). | Cơ chế guardrail bảo vệ rare-valid khỏi bị loại bỏ trong trimming. |
| **CLM-04** | "Conditional TFM scoring" hoặc "Cross-fitting" là đóng góp hoàn toàn mới. | **NOT ESTABLISHED (Bác bỏ)** | Prior work đã sử dụng: uTabPFN (code), ZEN (arXiv 2026-10), TACTIC (arXiv 2026-03). | Đóng góp nghiên cứu tập trung vào: **Cell-level self-contamination mechanisms & rare-valid preservation**. |
| **CLM-05** | CRIC-ED đạt SOTA vượt trội CDC trên toàn bộ 4 tập dữ liệu lớn của RAHA. | **PENDING (Đang chờ)** | Chưa chạy confirmatory evaluation trên toàn bộ RAHA. | Không đưa kết luận này vào bài báo trước Gate G3. |

---

## 2. Truy nguyên Thực nghiệm (Run Provenance)
- **Run ID:** `run_pilot_001`
- **Artifact Directory:** `experiments/runs/run_pilot_001/`
- **Tập tin đã lưu:** `config.json`, `metrics.json`, `predictions.csv`, `system_info.json`.
- **Git Commit:** Xem git log tại thời điểm commit handoff.
