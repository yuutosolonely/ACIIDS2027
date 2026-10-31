# Idea 3 — Thiết kế nghiên cứu cho ACIIDS 2027

> **Thiết kế hiện hành, 2026-10-30:** bổ sung decision brief và checkpoint Claude `0aff63e` xác nhận Path A. Thực thi amendment `prereg/PREREGISTRATION_V2_1.md`: five-fold row primary; observed-key LEO secondary trên hospital/flights/beers; final encoder transductive dirty-only; nested pass-1 trong outer training pool; q=0.15; phân tích mô tả theo source table và row-bootstrap, không verdict xuyên dataset. Random có cùng số hàng loại và chi phí nested được báo riêng, thêm accounted matched-compute sum. TFM numeric score là predictive tail, không density; DDCcore/LGBM/TFM raw không được gắn nhãn tái lập reference DDC/CDC/uTabPFN. Bỏ automatic pivot và các ablation chưa có trong v2.1 khỏi yêu cầu xác nhận hiện hành. Nội dung đề xuất gốc dưới đây giữ làm lịch sử; amendment v2.1 thay các lựa chọn xung đột. Freeze còn chờ development validation, không có confirmatory results.

Cập nhật: 2026-10-29.
> **Đối soát 2026-10-30:** tác giả đã chọn NO-GO cho hạn ACIIDS này (`docs/DECISION_BRIEF_20261030.md`). Nội dung dưới đây giữ vai trò thiết kế đề xuất gốc; fallback không tự cấp quyền pivot. Candidate v2 ở `prereg/PREREGISTRATION_V2.md` chưa được xác nhận quyền hạn/đóng băng; các thay đổi phương pháp phải được chấp thuận và đồng bộ ở đây trước khi dùng làm protocol hiện hành. Trạng thái và task tiếp theo: `docs/STATE.md`, `ROADMAP.md`.

Đề xuất sửa candidate (chưa chấp thuận): tính pass 1 bằng nested cross-fitting trong từng outer training pool; không tái dùng ma trận score toàn bảng để purification. Bản triển khai thử chỉ được kiểm trên fixture/fake predictor. Chi phí tăng, group boundary, final-pass transductive preprocessing và đơn vị thống kê vẫn cần quyết định trước freeze; xem `experiments/tfm/README.md`.

Đề xuất phương pháp cụ thể để tác giả rà: `docs/proposals/V2_AMENDMENT_20261030.md`. Khuyến nghị strict group/inductive boundary và kết quả theo từng source table; conditions/seeds là repeated measurements. Đây chưa phải quyết định chấp thuận hoặc thay đổi protocol gốc.
Working title: **CRIC-ED: Contamination-Resilient In-Context Likelihood for Cell-Level Error Detection in Tabular Foundation Models**
(Tên trong source card ban đầu: TabFM-ED; xem `docs/BRAINSTORM.md` để biết toàn bộ 3 hướng phân tích).
Stage: **Proposal / Hypothesis / Protocol Design (Đang xem xét dưới dạng đề xuất nghiên cứu; chưa chốt quyết định cuối cùng; chưa có kết quả thực nghiệm benchmark).**

---

## 1. Bài toán và mục tiêu nghiên cứu
Cho một bảng dữ liệu bẩn $\tilde{X} \in \mathbb{R}^{N \times D}$ gồm các cột số (numerical) và cột phân loại (categorical), hoàn toàn không có nhãn lỗi trong pha suy luận. Mục tiêu là tính điểm nghi ngờ lỗi (anomaly/error score) $S_{i,j}$ cho từng ô riêng biệt $(i,j)$ bằng Tabular Foundation Model (TFM) pre-trained mà không cần cập nhật trọng số (training-free).

Trọng tâm nghiên cứu là điều tra hiện tượng **Tự nhiễm bẩn ngữ cảnh (Self-Contamination)**: khi các ô lỗi trong bảng được nạp vào làm in-context prompt, chúng gây méo phân phối dự báo và làm "bình thường hóa" lỗi (Context Normalization), đặc biệt khi lỗi xuất hiện có cấu trúc. Đề tài phát triển và đánh giá cơ chế Context Intervention & Influence Trimming để khắc phục hiện tượng này.

---

## 2. Câu hỏi nghiên cứu (RQs) & Yêu cầu chứng minh
1. **RQ1 (Cell-ED vs Baselines)**: Conditional TFM Likelihood có đạt cell-level AUPRC vượt trội hơn classical baselines (DDC, Isolation Forest) và modern baselines (CDC, unsupervised TabPFN) trên cùng protocol và budget không?
2. **RQ2 (Cấu trúc lỗi trong Context)**: Lỗi phân tán ngẫu nhiên (random) và lỗi tập trung theo nhóm/nguồn (clustered) trong context làm suy giảm điểm số và thứ hạng của ô đích như thế nào?
3. **RQ3 (Trimming vs Rare-Valid Preservation)**: Cơ chế can thiệp context (random vs kNN vs influence-aware trimming) có tạo ra sự đánh đổi giữa việc loại bỏ lỗi context và việc vô tình xóa bỏ các nhóm mẫu hiếm nhưng hợp lệ (rare-valid subgroups) không?
4. **RQ4 (Hiệu năng tính toán)**: Đánh đổi giữa chi phí inference ($D$ bài toán ICL cho mỗi dòng) và độ chính xác so với các giải pháp imputation/statistical detection.

*Lưu ý Novelty*: Việc "dùng TFM tính conditional likelihood" hoặc "cross-fitting" đã xuất hiện trong prior work (uTabPFN, ZEN, TACTIC). Điểm mới cần chứng minh là: **định vị lỗi ở cấp ô (cell localization) trên dữ liệu bảng dị thể dưới sự can thiệp của self-contamination**, tách bạch khỏi bài toán row anomaly detection.

---

## 3. Hợp đồng phương pháp (Methodological Invariants)
- **Column Masking**: Mỗi cột mục tiêu $j$ được coi là biến phụ thuộc trong bài toán học có giám sát $X_{-j} \to X_j$. Giá trị quan sát $x_{i,j}$ không được làm feature đầu vào.
- **Cross-fitting / Leave-Row-Out**: Khi chấm điểm cho ô ở hàng $i$, toàn bộ hàng $i$ (hoặc entity group liên quan) tuyệt đối không được xuất hiện trong tập context.
- **Tách bạch điểm số theo kiểu dữ liệu**: Cột phân loại dùng Categorical Negative Log-Likelihood (NLL). Cột số dùng continuous density / tail score từ phân phối dự báo. Báo cáo phân tách theo từng loại cột; không tùy tiện coi xác suất rời rạc và mật độ liên tục là một thước đo đồng nhất.
- **Bảo toàn ranh giới thông tin**: Giá trị sạch thật và nhãn lỗi thuộc về evaluation harness; mã nguồn thuật toán detector tuyệt đối không được truy cập.
- **Kiểm soát rủi ro Trimming**: Không dùng nhãn thật để chọn tỷ lệ tỉa $q$. Mọi kết quả trimming phải so sánh có đối chứng với matched random-removal và kiểm tra tỷ lệ báo động giả trên các nhóm hiếm hợp lệ.
- **Không suy diễn bảo đảm Conformal vô căn cứ**: Không tự ý tuyên bố "conformal coverage guarantees" khi context bị bẩn nếu không có chứng minh lý thuyết tương ứng.

---

## 4. Ràng buộc Backbone & Hạ tầng
- Backbone chính: **TabPFN v2** (đã hỗ trợ phân phối liên tục và phân loại).
- Backbone khảo sát: **TabICL** (lưu ý: TabICL v1 chỉ hỗ trợ classification; không dùng cho regression trừ khi có checkpoint v2 tương ứng).
- Nguyên tắc an toàn: Không tự ý tải checkpoint nặng khi chưa có ủy quyền rõ ràng. Mọi kiểm thử ban đầu thực hiện trên CPU smoke test với dữ liệu synthetic/toy trước khi chạy confirmatory runs.

---

## 5. Tiêu chí Tiếp tục / Dừng (Go / No-Go Gates)
- **G0 (Setup & Interface Gate)**: Pinned package, license tương thích, checkpoint nạp được trên môi trường local, API trả về phân phối xác suất hợp lệ.
- **G1 (Protocol & Baseline Gate)**: Protocol cell-level công bằng, baseline DDC, CDC và uTabPFN chạy được trên cùng một tập ô đánh giá (eligible-cell universe).
- **G2 (Empirical Mechanism Gate)**: Hiệu quả của Context Intervention / Trimming vượt trội hơn giải thích giản đơn về mặt tăng compute hoặc giảm mẫu khó.
- *Nếu không qua G2*: Kích hoạt ngay Framing Dự phòng 1 (CS-ED: Abstention trên rare-valid cells) hoặc Framing Dự phòng 2 (Dual-ED: Thống kê robust + LLM semantic).
