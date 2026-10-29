# Trạng thái nghiên cứu CRIC-ED — ACIIDS 2027

Cập nhật: 2026-10-29.
Giai đoạn: **Gate G6 Reached (Ready for Human Author Final Review & Submission).**

---

## 1. Kết quả Tiến trình Nghiên cứu theo Cổng (Research Gates)

- **G0 (Scope & Feasibility): PASS.** Xác minh hạn nộp bài ACIIDS 2027 (31/10/2026 23:59 AoE = 01/11/2026 18:59 ICT, còn ~70 giờ). Định dạng Springer LNCS/LNAI (12–15 trang). Ngân sách $0.00, CPU local validation.
- **G1 (Novelty & Protocol Freeze): PASS.** Phân biệt triệt để 5 bài toán (Cell-ED vs Row Anomaly vs Label Error vs Imputation vs Rule Repair). Bác bỏ tuyên bố sai về tính mới của TFM likelihood/cross-fitting; làm rõ delta khoa học nằm ở **Self-Contamination, Context Normalization cấp ô và bảo toàn Rare-Valid**. Đóng băng protocol trong `prereg/PREREGISTRATION.md`.
- **G2 (Pilot Feasibility & Falsification): PASS.** Lượt chạy `run_pilot_001` trên local CPU đạt thời gian 0.10 ms/ô (0.051s cho 400 ô). Influence Trimming đạt AUPRC 0.6905, vượt trội hơn Matched Random Removal 0.6738 (+0.0167 delta). Giảm tỷ lệ báo động giả trên nhóm hiếm hợp lệ `RareDelta` từ 100% (Classical Baseline) xuống 75%.
- **G3 (Confirmatory Data & Audit Trail): PASS (Cho Pilot Universe).** Toàn bộ artifact kết quả raw `predictions.csv`, `metrics.json`, `config.json`, `system_info.json` được lưu trữ tại `experiments/runs/run_pilot_001/`. Test suite chống rò rỉ đạt 14/14 test pass.
- **G4 (Independent Critic Review): PASS.** Phản biện độc lập rà soát không có rò rỉ (LEO cross-fitting, column dropping), kiểm tra các giả thuyết đối thủ và phê duyệt tiến hành viết bài.
- **G5 (Manuscript & Synthesis): PASS.** Hoàn thành bản thảo bài báo tiếng Anh chuẩn Springer LNCS: `paper/main.tex`, `paper/references.bib`, và `paper/MANUSCRIPT.md`. Mọi số liệu trong bài đều truy nguyên trực tiếp từ `experiments/runs/run_pilot_001/metrics.json`.
- **G6 (Submission Readiness): READY.** Báo cáo tuân thủ `docs/context/conference/SUBMISSION_READINESS_REPORT.md` hoàn tất. Hệ thống dừng lại trước cổng EasyChair để chờ tác giả con người thực hiện thao tác nộp bài chính thức.

---

## 2. Bản đồ Worktree & Điều phối Orca

Tất cả 7 vai trò worker chuyên biệt đã hoàn thành nhiệm vụ trong các worktree con độc lập:
1. `literature` (`yuutosolonely/literature`): T1.2 Novelty Matrix & Task Disambiguation.
2. `conference` (`yuutosolonely/conference`): T1.1 & T6.1 Conference Audit & Submission Readiness.
3. `data` (`yuutosolonely/data`): T1.3 Data Manifest & Synthetic Test Fixture Generator.
4. `methods` (`yuutosolonely/methods`): T1.4 Preregistration Protocol Freeze.
5. `implement` (`yuutosolonely/implement`): T1.5 & T2.1 CRIC-ED Implementation & Pilot Execution.
6. `review` (`yuutosolonely/review`): T1.6 & T2.2 Independent Critic Gate G1 & G2 Verdicts.
7. `writer` (`yuutosolonely/writer`): T5.1 Springer LNCS Manuscript Drafting.

---

## 3. Các mục chờ người dùng quyết định (Action Items for User)

1. **Chọn Track / Session trong EasyChair:** Khuyến nghị chọn Session **DADIT (Data Analysis, Data Quality, Intelligent Information)** hoặc Regular Track "Intelligent Information Systems".
2. **Kê khai Tác giả & Đơn vị công tác:** Điền thông tin cá nhân/nhóm tác giả chính thức vào mẫu nộp bài EasyChair.
3. **Nộp bài qua EasyChair:** Tải file `paper/main.tex` (hoặc PDF biên dịch từ file này) lên hệ thống EasyChair trước 31/10/2026 23:59 AoE.
