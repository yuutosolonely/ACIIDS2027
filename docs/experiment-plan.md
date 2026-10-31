# Kế hoạch Thực nghiệm CRIC-ED — ACIIDS 2027

> **Kế hoạch thực thi hiện hành, 2026-10-30:** theo thiết kế đã đồng bộ trong `docs/IDEA.md` và accepted decisions của tác giả, thực hiện T1–T8 của `docs/handoffs/TASKS_CODEX_V2_1_20261030.md`. V2.1 candidate là đặc tả prospective; v1/v2 giữ nguyên lịch sử. Dev: movies_1, seed0, ba điều kiện; confirmatory sau freeze: hospital/flights/beers/rayyan × real/inj-random/inj-systematic × seeds0–4, cả LGBM và pinned TabPFN-2. Row primary, observed-key LEO secondary, row-bootstrap mô tả; final preprocessing transductive công khai. Không tự áp dụng group-primary/inductive v3, không Wilcoxon/Holm, không đổi protocol theo kết quả. Các phần kế hoạch gốc bên dưới không thay amendment hiện hành.

Cập nhật: 2026-10-29.
Trạng thái: **Protocol Design; Chưa đóng băng (Unfrozen); Chưa chạy confirmatory runs.**

> **Ghi chú 2026-10-30:** tài liệu này là kế hoạch lịch sử. Protocol đóng băng hiện hành là `prereg/PREREGISTRATION.md` (không sửa). Trạng thái thực hiện và deviation: `docs/EXPERIMENT_LOG.md` §3–4, `docs/review/AUDIT_20261030.md`.

Candidate v2 và đề xuất nested pass 1/kiểm freeze-source-grid ở `experiments/tfm/README.md` chưa phải amendment được duyệt. Chỉ validation CPU tổng hợp được thực hiện trong lượt remediation; không thay prereg v1/v2, không mở confirmatory.

Chi tiết amendment đề xuất (chưa duyệt): `docs/proposals/V2_AMENDMENT_20261030.md`. Tài liệu nêu estimand, group/inductive boundary, matched-compute control, dependence theo source table và lý do khuyến nghị mô tả kết quả trên bộ bảng hiện tại. Run-attempt/runtime validation đã được kiểm trên fixtures, chưa có checkpoint capability hoặc benchmark validation.

---

## 1. Dữ liệu và Ranh giới Thông tin (Datasets & Information Boundaries)

### Tập dữ liệu ứng cử viên (Benchmark Candidates)
- **Nguồn chính**: Benchmark chuẩn RAHA (https://github.com/BigDaMa/raha).
  - *Hospital*: Bảng dữ liệu y tế, lỗi hỗn hợp (typos, swapped attributes).
  - *Beers*: Dữ liệu sản phẩm/nhà máy bia, nhiều giá trị phân loại và đơn vị đo.
  - *Flights*: Dữ liệu lịch trình bay, lỗi định dạng thời gian và số hiệu.
  - *Rayyan*: Dữ liệu tài liệu y văn, lỗi chuỗi dài và giá trị phân loại hiếm.
- **Ranh giới dữ liệu**:
  - Giữ nguyên cấu trúc thô (raw CSV values), không tự ép kiểu làm mất đi thuộc tính lỗi.
  - Không nạp giá trị sạch (clean ground-truth) vào pipeline detector.
  - Nhãn lỗi thực sự chỉ được phép mở cho module đánh giá (Evaluation Harness) để tính metric.
  - Khi có thực thể lặp lại (duplicate entities / grouped rows), thực hiện Grouped Split để tránh rò rỉ cùng một entity vào context.

---

## 2. Các tầng Baseline so sánh (Multi-Tier Baselines)

Để đánh giá trung thực và thuyết phục cho phản biện ACIIDS 2027:

1. **Tier 1: Classical Coordinate-Wise Baselines**:
   - *DDC (Detecting Deviating Data Cells)*: Thống kê đa biến robust trên các cột số.
   - *Column-wise Isolation Forest / Local Outlier Factor*: Mô hình học máy truyền thống chấm điểm độc lập trên từng cột.
2. **Tier 2: Direct Task Competitor Baselines**:
   - *CDC (From Data Imputation to Data Cleaning, AISTATS 2024)*: Phương pháp kết hợp imputer + conformal calibration.
   - *Unsupervised TabPFN (uTabPFN)*: Sử dụng TabPFN extension nguyên bản với conditional likelihood scoring thông thường (không có cơ chế can thiệp context chống self-contamination).
3. **Tier 3: Advanced LLM-based Baselines (Tùy điều kiện tài nguyên)**:
   - *ZeroED (ICDE 2025)* hoặc *ForestED (2025/2026)*: Đo lường khả năng suy luận zero-shot của LLM trên cùng tập dữ liệu con (nếu có API token/compute).
4. **Diagnostic Arms (Chỉ dùng chẩn đoán rò rỉ/cơ chế)**:
   - *No-Crossfit Arm*: Cố tình đưa hàng mục tiêu vào context để định lượng mức độ phồng điểm số do rò rỉ thông tin (leakage diagnostic).
   - *Clean Context Oracle*: Cung cấp context hoàn toàn sạch để đo lường giới hạn trên lý tưởng (theoretical upper bound) của TFM khi không bị self-contamination.

---

## 3. Thước đo và Phân tích Thống kê (Metrics & Statistical Rigor)

- **Thước đo chính**:
  - Cell-level Average Precision (AUPRC).
  - Precision@k, Recall@k, F1@budget $k$ với ngân sách kiểm toán $k \in \{0.01, 0.05, 0.10\}$ tổng số ô.
  - Báo cáo phân tách rạch ròi: Overall, Numerical columns, Categorical columns.
- **Báo cáo phạm vi (Coverage Denominator)**:
  - Báo cáo rõ ràng số lượng ô không thể dự đoán (unsupported text/ID columns, unknown categorical classes). Mẫu số tính AUPRC phải là toàn bộ tập ô hợp lệ của bảng (eligible universe), không được loại bỏ các ô khó để làm đẹp kết quả.
- **Độ tin cậy & Lặp lại (Confidence Intervals & Seeds)**:
  - Chạy tối thiểu 5 random seeds cho context sampling.
  - Báo cáo Macro-average và kết quả riêng trên từng dataset.
  - Sử dụng Cluster Bootstrap theo hàng/thực thể để tính 95% Confidence Intervals; không giả định các ô độc lập (IID).
- **Đo lường chi phí (Compute Accounting)**:
  - Ghi nhận chi tiết: Thời gian tạo context (context construction time), thời gian forward pass, peak memory (RAM/VRAM), số lượng forward calls ($D$ calls per row).

---

## 4. Các thí nghiệm Ablation bắt buộc

1. **Ablation trên Cơ chế Trimming**:
   - `No Trimming` (giữ nguyên context bẩn ban đầu).
   - `Random Removal` (loại bỏ ngẫu nhiên cùng số lượng mẫu context để kiểm soát hiệu ứng giảm kích thước context).
   - `Influence-Aware Trimming` (loại bỏ có định hướng dựa trên negative influence score).
2. **Ablation trên Chiến lược Chọn Context**:
   - `Random Context Selection`.
   - `kNN Context Selection` (chọn các hàng gần nhất trong không gian đặc trưng).
   - `Stratified Context Selection` (chọn đa dạng đại diện theo phân phối nhãn).
3. **Ablation trên Context Size**:
   - Kích thước context $k \in \{32, 64, 128, 256, 512\}$.
4. **Kiểm tra tác động tới nhóm hiếm hợp lệ (Rare-Valid Preservation)**:
   - Đo lường False Positive Rate trên các giá trị thuộc nhóm thiểu số hợp lệ (minority subgroups) trước và sau khi áp dụng Trimming.

---

## 5. Kế hoạch Pilot Tối thiểu (Minimum Viable Pilot)

Trước khi tiến hành bất kỳ confirmatory runs quy mô lớn nào:
1. **Kiểm tra API Phân phối của TabPFN (Step G0)**: Chạy script kiểm tra cục bộ trên CPU với dữ liệu synthetic nhỏ (10 dòng, 3 cột) để kiểm tra đầu ra phân phối số liên tục và phân loại.
2. **Smoke Test trên 1 Dataset nhỏ (Step G1)**: Chạy pipeline trên subset 200 dòng của tập dữ liệu `Beers` hoặc `Hospital` trên CPU. Đo lường AUPRC thô và thời gian chạy.
3. **Đánh giá sơ bộ**:
   - Nếu conditional NLL của TabPFN không phân biệt được lỗi hoặc chạy quá chậm trên CPU: Review lại và quyết định có cần tối ưu hóa/kích hoạt Framing Dự phòng (CS-ED hoặc Dual-ED) hay không.
   - Chưa được chạy compute trả phí hoặc download dataset nặng khi chưa có sự đồng ý của người dùng.
