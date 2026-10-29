# Ý tưởng 4 — EquiSchema

**Working title (EN):** *Same Facts, Different Predictions? Auditing Storage Invariance and Role Sensitivity of Relational Deep Learning and Relational Foundation Models*
**Tên tiếng Việt:** Cùng dữ kiện, khác dự đoán? Kiểm toán tính bất biến theo cách lưu trữ và độ nhạy vai trò của học sâu quan hệ

| Mục | Nội dung |
|---|---|
| Hạng (Claude) | **4/5**. Người dùng chưa chọn |
| Nguồn gốc | Tinh chỉnh từ **V2-ROLE** của Codex theo hướng study-first, bổ sung prior bị bỏ sót (RDB2G-Bench, 4DBInfer) |
| Trạng thái | **EXPERT HYPOTHESIS**. Chưa tải RelBench hay RT checkpoint; chưa xây rewrite nào |
| Khả năng kịp ACIIDS 31/10/2026 | **Không.** Cần 6–10 tuần |
| Session phù hợp (nếu nộp ACIIDS sau) | **GDAIS** (graph representation learning); **DADIT** (relational DB, normalization/denormalization); **DMPI** |
| Đích chính | Datasets & Benchmarks track (NeurIPS) hoặc KDD; VLDB EA&B. Journal: TKDE/DMKD. Deadline và rank phải kiểm tra khi chọn |
| Loại bài | Phân tích + benchmark có chứng nhận; phương pháp chỉ khi vượt được baseline canonical view |

> Không có bảo đảm được nhận bài. Ý tưởng này đa dạng hóa danh mục, ở cộng đồng relational DL, khác với các Ý tưởng 1–3.

---

## 1. Tóm tắt một đoạn

Học sâu quan hệ (RelBench, RelGNN) và các relational foundation model (như Relational Transformer, ICLR 2026) học trực tiếp trên cơ sở dữ liệu nhiều bảng. Hai cơ sở dữ liệu **chứa cùng dữ kiện** nhưng khác cách lưu trữ không nên cho dự đoán khác nhau. Ví dụ là tách một bảng thành hai bảng 1:1, gộp bảng chiều vào bảng sự kiện, hay vật chất hóa một quan hệ thành bảng liên kết. Ngược lại, đổi **vai trò** (buyer ↔ seller) có thể đổi nhãn, nên mô hình phải nhạy với nó. RT tự thừa nhận chưa phân biệt các FK như buyer_id/seller_id cùng trỏ về một bảng. RDB2G-Bench (NeurIPS 2025 D&B) cho thấy cách mô hình hóa đồ thị thay đổi hiệu năng đến khoảng 10%. EquiSchema là một **kiểm toán có chứng nhận** gồm bốn phần. Thứ nhất, sinh các rewrite **được chứng minh bảo toàn thông tin** bằng SQL round-trip. Thứ hai, đo độ bất đồng dự đoán theo từng thực thể và worst-view. Thứ ba, đo khả năng phân biệt vai trò bằng các cặp role-swap. Thứ tư, chẩn đoán tầng nào làm mất thông tin: encoding, sampling hay encoder. Các biện pháp đơn giản (role embedding, canonical view, sampling theo logical facts) được đánh giá như baseline khắc phục.

## 2. Công trình gần nhất và ranh giới

| Công trình | Đã làm gì | Ranh giới | Mức xác minh |
|---|---|---|---|
| **RDB2G-Bench** — NeurIPS 2025 D&B | Benchmark khoảng 50k cặp (graph model, hiệu năng) trên 5 RDB, 12 task; cách mô hình hóa đồ thị thay đổi hiệu năng đến 10% | Tìm cách **chọn** biểu diễn tốt nhất cho **một** schema. EquiSchema kiểm tra **bất biến** giữa các schema **tương đương đã chứng nhận** và độ nhạy vai trò, ở mức từng dự đoán | VERIFIED (proceedings/arXiv 2506.01360) |
| **4DBInfer** | Toolbox/benchmark graph-centric trên RDB, nhiều cách xây đồ thị | Như trên; cần đọc kỹ để tránh trùng | Theo hiểu biết là NeurIPS 2024 D&B; **UNVERIFIED** trong phiên |
| **Relational Transformer** — ICLR 2026 | Model khoảng 22M, bounded BFS, relational attention; tự nêu giới hạn buyer/seller FK | Đối tượng kiểm toán chính; giới hạn đã được tác giả nêu, nên **không tuyên bố phát hiện đầu tiên** | VERIFIED (handoff, full text local) |
| **Castor** — SIGMOD 2017 | Học quan hệ độc lập schema qua dependencies | Nền tảng lý thuyết bất biến; phải trích dẫn | VERIFIED (handoff) |
| **RelGNN** — ICML 2025 | Composite message passing cho bridge/hub | Đối tượng kiểm toán | AGENT-REPORTED |
| EvoSchema (PVLDB 2025), SQLHD, *Same Data Different Schemas* (aiDM 2026) | Độ bền của Text-to-SQL với thay đổi schema | Bài toán khác (NL→SQL), nhưng cùng tinh thần. Trích dẫn để định vị | AGENT-REPORTED |

**Phát biểu đóng góp (study-first):**
1. **C1:** một họ rewrite bảo toàn thông tin có **chứng nhận** (round-trip SQL và kiểm tra bảo toàn nhãn/timestamp), cùng các cặp role-swap có nhãn thay đổi kiểm chứng được.
2. **C2:** chỉ số kiểm toán theo từng thực thể: tỷ lệ bất đồng giữa view tương đương, worst-view performance, role-identifiability rate, logical coverage.
3. **C3:** chẩn đoán theo tầng, nhờ các cặp đầu vào có encoding giống nhau nhưng nhãn khác (thiếu identifiability), và cặp encoding khác nhưng thông tin giống (thiếu invariance).
4. **C4:** đánh giá các biện pháp đơn giản, có chi phí. Chỉ nâng thành bài phương pháp nếu sampler mới **vượt canonical SQL view không vật chất hóa** về đường biên chi phí–chất lượng.

**Không tuyên bố:** phát hiện đầu tiên về role loss hay schema independence; định lý mới cho lập luận identifiability chuẩn (cùng encoding mà khác nhãn thì không predictor nào phân biệt được).

## 3. Câu hỏi nghiên cứu

- **RQ1:** Các mô hình relational DL hiện đại thay đổi dự đoán đến mức nào dưới rewrite bảo toàn thông tin? Có khác biệt giữa GNN, RT và baseline đặc trưng tổng hợp + GBDT không?
- **RQ2:** Mô hình nào phân biệt được vai trò khi các FK cùng trỏ về một bảng? Tác động thực tế lên task tự nhiên lớn đến đâu?
- **RQ3:** Thông tin bị mất ở tầng nào: schema/token encoding, neighbor sampling (ngân sách hop vật lý) hay encoder?
- **RQ4:** Biện pháp rẻ nhất đạt cả bất biến và nhạy vai trò là gì, và tốn bao nhiêu?

Giả thuyết (EXPERT HYPOTHESIS): ngân sách hop/fanout vật lý là nguồn bất ổn chính dưới decomposition và reification; FK-role embedding sửa được phần lớn lỗi vai trò; canonical view + sampling theo logical ID đạt bất biến gần tuyệt đối với chi phí thấp. Nếu đúng thì đó là **khuyến nghị thực hành**, không phải thuật toán mới.

## 4. Thiết kế

- **Rewrite (cố định trước, có chứng nhận):** R1 tách dọc giữ khóa (1:1); R2 phi chuẩn hóa N:1 (gộp thuộc tính chiều vào bảng sự kiện); R3 vật chất hóa FK thành bảng liên kết; R4 đổi tên bảng/cột giữ ngữ nghĩa; tổ hợp với độ sâu tăng dần. Mỗi rewrite có T và T⁻¹ bằng SQL; kiểm tra T⁻¹(T(D)) = D, nhãn task và cutoff thời gian không đổi.
- **Role-swap:** chọn task có vai trò thật, ví dụ hai FK cùng trỏ về một bảng. **Data gate:** phải tìm được task tự nhiên trong RelBench có tính chất này. Nếu không có, phải xây task có kiểm chứng và ghi rõ.
- **Dữ liệu:** RelBench rel-f1, rel-stack; thêm rel-avito/rel-trial nếu RAM cho phép. Giữ temporal split chính thức.
- **Mô hình:** RT (checkpoint công khai), RelGNN, baseline GNN của RelBench, LightGBM/CatBoost trên đặc trưng tổng hợp (DFS). Thêm relational foundation model khác nếu truy cập được (**UNVERIFIED**).
- **Baseline khắc phục:** thêm FK-role embedding; tăng fanout/hop; schema augmentation khi train; canonical SQL view không vật chất hóa + indexed joins + sampling theo logical ID; back-map về schema gốc (oracle khi có mapping).
- **Chỉ số:** metric task gốc; tỷ lệ bất đồng dự đoán (phân loại) hoặc |Δ| (hồi quy) theo thực thể; worst-view; role-identifiability; RAM/VRAM/latency/chi phí tiền xử lý.
- **Thống kê:** paired theo thực thể; bootstrap theo thực thể và theo task; nhiều seed huấn luyện, để tách bất ổn do rewrite khỏi bất ổn do seed. **Bắt buộc:** baseline "cùng schema, khác seed".

## 5. Điều kiện tiếp tục / dừng

| Cổng | Kiểm tra | Nếu thất bại |
|---|---|---|
| G0 | Cài RelBench và RT, chạy được 1 task trên phần cứng hiện có | Thu hẹp mô hình hoặc dừng |
| G1 | Bất đồng do rewrite **vượt rõ** bất đồng do seed trên ≥ 2 database | Nếu không: kết quả âm có giá trị (mô hình đã bất biến), nhưng khó thành bài A*. Cân nhắc dừng |
| G2 | Có task tự nhiên mà vai trò ảnh hưởng nhãn | Nếu không: chỉ còn trục bất biến; giảm tham vọng |

## 6. Kế hoạch thời gian (6–10 tuần)

Tuần 1–2: G0, xây R1–R3 có chứng nhận trên rel-f1, đo bất đồng so với seed (G1). Tuần 3–4: role-swap, chẩn đoán theo tầng. Tuần 5–6: các biện pháp khắc phục và chi phí. Tuần 7–8: mở rộng database, viết. Tuần 9–10: dự phòng, artifact.

## 7. Lộ trình nâng cấp

- D&B track: phát hành bộ rewrite có chứng nhận và harness kiểm toán như benchmark mở.
- Bài phương pháp (chỉ khi G-method đạt): sampler theo logical facts thắng canonical view về chi phí, có chứng minh đẳng cấu lân cận dưới coupling seed.
- Hướng phụ: kiểm toán độ bền của relational DL với lỗi dữ liệu (tiêm lỗi kiểu BART), nối với Ý tưởng 1–3.

## 8. Phản biện dự kiến

| Phản biện | Trả lời |
|---|---|
| "RDB2G-Bench đã chỉ ra biểu diễn ảnh hưởng hiệu năng" | Họ tối ưu lựa chọn biểu diễn cho một schema. Chúng ta kiểm toán bất biến mức dự đoán giữa schema tương đương có chứng nhận, cộng độ nhạy vai trò và chẩn đoán theo tầng |
| "Chỉ cần canonical view là xong" | Đó có thể chính là phát hiện và khuyến nghị. Bài trình bày trung thực, không bịa thuật toán |
| "Rewrite nhân tạo" | Ghi rõ là controlled transformations; bổ sung lịch sử refactoring thật nếu tìm được |

## 9. Rủi ro

Thiết lập RT/RelBench tốn thời gian; RAM cho join lớn; thiếu task vai trò tự nhiên; kết quả có thể "mô hình đã đủ bất biến" khi tính theo seed. Đây là lý do xếp hạng 4: chất lượng khoa học tốt và hiện tượng gần như chắc chắn tồn tại (ngân sách hop thay đổi theo schema), nhưng cần hạ tầng lớn nhất, thời gian dài nhất và không kịp deadline ACIIDS.

## 10. Tài liệu tham khảo cốt lõi

- RDB2G-Bench: https://arxiv.org/abs/2506.01360 ; https://proceedings.neurips.cc/paper_files/paper/2025/hash/b0cbac3acd497f5ab2b2ca83c6c6bc56-Abstract-Datasets_and_Benchmarks_Track.html — VERIFIED
- Relational Transformer, ICLR 2026: https://proceedings.iclr.cc/paper_files/paper/2026/hash/7107d4d2e837bde2171c6b71b5bde954-Abstract-Conference.html — VERIFIED (handoff)
- Castor, SIGMOD 2017: https://josepicado.com/papers/Castor_SIGMOD2017.pdf — VERIFIED (handoff)
- RelBench: https://github.com/snap-stanford/relbench ; RT code: https://github.com/snap-stanford/relational-transformer
- RelGNN (ICML 2025): https://openreview.net/pdf?id=XXh3zmw2Uy — AGENT-REPORTED
- 4DBInfer — **UNVERIFIED** metadata; tra cứu trước khi trích dẫn
