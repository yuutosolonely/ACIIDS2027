# Ý tưởng 3 — TabFM-ED

**Working title (EN):** *Masked In-Context Likelihood: Tabular Foundation Models as Training-Free Cell-Level Error Detectors under Self-Contamination*
**Tên tiếng Việt:** Mô hình nền tảng dạng bảng làm bộ phát hiện lỗi mức ô không cần huấn luyện, khi ngữ cảnh chính là bảng bẩn

| Mục | Nội dung |
|---|---|
| Hạng (Claude) | **3/5**. Người dùng chưa chọn |
| Trạng thái | **EXPERT HYPOTHESIS**. Chưa cài TabPFN/TabICL; chưa đo GPU/VRAM. Benchmark RAHA public |
| Khả năng kịp ACIIDS 31/10/2026 | **Thấp–trung bình.** Bản ACIIDS cần khoảng 7–10 ngày-người. Với 2 người có GPU sẵn, bản thu hẹp (4 dataset, 2 backbone, CDC + 2 baseline) khả thi nhưng rủi ro; cổng chất lượng tối 29/10 |
| Session phù hợp | **DADIT** (data quality); **ADMTA** (neural networks applied to data mining); main track "foundation models" |
| Đích nâng cấp | KDD/ICDE nếu có phân tích cơ chế và benchmark rộng; KBS/ESWA/Information Sciences/DMKD cho journal (kiểm tra quartile năm hiện hành) |
| Quan hệ với Codex | Giữ phần đáng giá của **V2-TFM** (lựa chọn context ảnh hưởng suy luận) và đặt vào bài toán **có ground truth**: context bị nhiễm dòng bẩn |

> Không có bảo đảm được nhận bài.

---

## 1. Tóm tắt một đoạn

Các phương pháp phát hiện lỗi hiện nay đều có điểm yếu riêng. Nhóm thứ nhất cần nhãn (Raha/Baran). Nhóm thứ hai cần ràng buộc viết tay (HoloClean). Nhóm thứ ba gọi LLM API theo từng dòng, vừa tốn chi phí vừa có thể kém trên domain lạ. Nhóm cuối train imputer cho từng cột (Conformal Data Cleaning, AISTATS 2024). Tabular foundation model (TFM) như TabPFN v2 hay TabICL dự đoán **bất kỳ cột nào từ các cột còn lại chỉ bằng một forward pass in-context**, kèm phân phối dự đoán. Đây là một thước đo tự nhiên cho độ hợp lý có điều kiện của từng ô, không cần train và không cần API. Khó khăn cốt lõi là **tự nhiễm bẩn**: context chính là bảng bẩn. Dòng lỗi trong context làm lệch dự đoán, và cách chọn context (ngẫu nhiên, láng giềng gần hay đã cắt tỉa) tương tác với lỗi. TabFM-ED đề xuất điểm *masked in-context likelihood* cho từng ô có cross-fitting, một quy trình **context chống nhiễm bẩn** (cắt tỉa lặp), và một nghiên cứu cơ chế: TFM bắt được loại lỗi nào, bỏ sót loại nào, và hiệu năng suy giảm theo mức bẩn của context ra sao.

## 2. Vấn đề và động lực

- **Tính thực tiễn:** chi phí bằng 0 USD API, chạy trên 1 GPU, không cần nhãn, không cần catalogue.
- **Khoảng trống khoa học:** lý thuyết của TFM giả định context sạch. Một bài 2026 nghiên cứu chiều ngược lại, tức làm sạch dữ liệu *cho* TFM (arXiv 2604.25154). Một bài khác phân tích độ bền nhiễu của attention trong TabPFN (arXiv 2604.04868). Tìm kiếm nhanh trong phiên **không thấy** công trình dùng TFM làm bộ phát hiện lỗi mức ô trên RAHA. Kết luận này **chưa phải tra cứu toàn diện**.
- **Câu hỏi cơ chế (kế thừa V2-TFM):** chọn context "liên quan nhất" (kNN) có thể kéo theo đúng các dòng cùng mẫu lỗi, khiến lỗi trông hợp lý. Context ngẫu nhiên đại diện hơn nhưng nhiễu hơn. Câu hỏi này ở đây **đo được bằng nhãn lỗi thật**, không còn là giả thuyết trừu tượng.

## 3. Công trình gần nhất và ranh giới đóng góp

| Công trình | Đã làm gì | Ranh giới với TabFM-ED | Mức xác minh |
|---|---|---|---|
| **Conformal Data Cleaning (CDC)** — Jäger & Biessmann, AISTATS 2024 | Train imputer theo cột + conformal; gắn cờ ô ngoài tập dự đoán | **Đối thủ gần nhất.** TabFM-ED khác ở ba điểm: không train (in-context); xử lý context bẩn tường minh; dùng phân phối dự đoán hỗn hợp kiểu dữ liệu. **Phải thắng hoặc ngang CDC với chi phí setup thấp hơn** | VERIFIED |
| **ZeroED** — ICDE 2025 | LLM reasoning + classifier, zero-shot error detection; báo cáo cải thiện F1 trên 7 dataset | Baseline zero-shot mạnh dùng LLM | VERIFIED (arXiv 2504.05345) |
| Model-Aware Data Cleaning for TFMs (arXiv 2604.25154) | Làm sạch để TFM dự đoán tốt hơn | Chiều ngược lại: ở đây TFM làm detector | Search-level |
| Noise Immunity in In-Context Tabular Learning (arXiv 2604.04868) | Phân tích độ bền nhiễu của attention TabPFN | Nền tảng cho phân tích tự nhiễm bẩn; phải trích dẫn | Search-level |
| AnoLLM (ICLR 2025); detector LLM zero-shot | Điểm bất thường / phát hiện lỗi bằng LLM | Baseline | Kiến thức nền |
| Raha (SIGMOD 2019), Baran (PVLDB 2020), dBoost, HoloClean | Phát hiện/sửa lỗi cổ điển | Baseline chuẩn | Kiến thức nền |
| TabPFN v2 (Nature 2025), TabICL / TabICLv2 | TFM; TabPFN v2 khoảng ≤10k mẫu/≤500 đặc trưng; TabICL xử lý đến 500k mẫu | Backbone; giới hạn kích thước và **license phải kiểm tra** | SOURCE-REPORTED; license **UNVERIFIED** |

**Phát biểu novelty (hẹp):**
1. **C1:** điểm *masked in-context likelihood* mức ô cho TFM, có cross-fitting (ô không nằm trong context của chính nó), xử lý cột số (mật độ hoặc tail từ phân phối dự đoán) và cột phân loại.
2. **C2:** **context chống tự nhiễm bẩn:** cắt tỉa lặp các dòng nghi ngờ khỏi context, và so sánh có kiểm soát các chiến lược context (ngẫu nhiên, kNN, phân tầng, cắt tỉa, hỗn hợp tham chiếu + cục bộ).
3. **C3:** nghiên cứu cơ chế: đường liều–đáp ứng theo tỷ lệ lỗi; phân loại lỗi TFM bắt được (outlier, vi phạm kiểu phụ thuộc hàm, swap, giá trị phân loại sai) và lỗi bỏ sót (typo trong văn bản tự do, mã hóa missing).
4. **C4:** đánh giá so với CDC, ZeroED, Raha và detector LLM ở **cùng điều kiện**, có cost accounting (GPU-giây, USD).

**Không tuyên bố:** TFM tốt hơn mọi phương pháp ở mọi loại lỗi; bảo đảm conformal khi context bẩn (chỉ phân tích thực nghiệm, trừ khi chứng minh được).

## 4. Câu hỏi nghiên cứu và giả thuyết

- **RQ1:** TFM in-context, không train, đạt hiệu năng phát hiện lỗi mức ô bao nhiêu so với CDC, ZeroED, Raha và detector LLM?
- **RQ2:** Tự nhiễm bẩn làm suy giảm hiệu năng thế nào theo tỷ lệ lỗi, và cắt tỉa lặp khôi phục được bao nhiêu?
- **RQ3:** Context kNN có làm lỗi có hệ thống "trông hợp lý" hơn context ngẫu nhiên không? (kiểm định cơ chế)
- **RQ4:** TFM bổ sung cho detector LLM ngữ nghĩa ở loại lỗi nào? Lai hai loại có vượt từng loại không?

Giả thuyết (EXPERT HYPOTHESIS):
- **H1:** TFM mạnh ở lỗi kiểu phụ thuộc giữa cột và outlier số; yếu ở typo trong văn bản tự do.
- **H2:** cắt tỉa lặp cải thiện rõ khi tỷ lệ lỗi cao (Flights, Tax).
- **H3:** kNN context có hại khi lỗi có hệ thống (cùng nguồn sai), có lợi khi lỗi ngẫu nhiên.
- **H4:** lai TFM + LLM có tính bổ sung.

## 5. Phương pháp

```text
Bảng bẩn D̃ ──► mã hóa cột (số / phân loại / văn bản tự do → đặc trưng mẫu: độ dài, lớp ký tự, pattern)
       │
  Với mỗi cột j:  K-fold theo dòng ──► context C_j^(-fold) ──► TFM dự đoán p(x_ij | x_i,-j)
       │                                   ▲
       │            cắt tỉa lặp: bỏ top-q% dòng nghi ngờ khỏi context, chạy lại (2–3 vòng)
       │
  Điểm ô s_ij = −log p (phân loại) | −log mật độ hoặc tail hai phía (số)
       │
  Chuẩn hóa theo cột (rank / hiệu chỉnh) ──► điểm dòng = max hoặc tổng điểm ô
       │
  Ngưỡng: top-k theo ngân sách | conformal trên phần dư context đã cắt tỉa (thực nghiệm)
       │
  (tùy chọn) lai với điểm LLM ngữ nghĩa ──► nối với Ý tưởng 1 như một proxy mới
```

Ghi chú kỹ thuật:
- Cột ID và cột gần duy nhất (khóa, số điện thoại) không dự đoán trực tiếp được. Chuyển sang đặc trưng định dạng, hoặc loại khỏi mục tiêu và báo cáo rõ.
- Bảng lớn (Tax, khoảng 200k dòng) vượt giới hạn context của TabPFN v2. Dùng context con lấy mẫu, chia khối, hoặc TabICL. Đo chi phí.
- Cố định seed, phiên bản model và checkpoint; ghi license.

## 6. Thiết kế thực nghiệm

- **Dữ liệu:** RAHA Hospital, Flights, Beers, Rayyan, Tax (lấy mẫu), Movies (public). Thêm REIN nếu tải được (**UNVERIFIED**). Tiêm lỗi có kiểm soát trên bản clean (BART hoặc trình sinh lỗi bằng LLM) để có đường liều–đáp ứng; **ghi rõ là synthetic**.
- **Backbone:** TabPFN v2 (hoặc phiên bản mới hơn nếu license cho phép), TabICL. Cần tối thiểu 2 backbone.
- **Baseline:** CDC (code công khai), ZeroED (kiểm tra code), Raha (20 dòng có nhãn) và Baran nếu kịp, dBoost/IsolationForest/LOF, detector vi phạm FD, AnoLLM, LLM zero-shot.
- **Chỉ số:** P/R/F1 mức ô tại ngân sách, AUPRC mức ô, AUC mức dòng, F1 theo loại lỗi, thời gian, VRAM, USD.
- **Protocol:** mọi siêu tham số (q, số vòng, K) chọn trên dev; báo cáo test một lần; bootstrap theo dòng/ô và theo dataset; 5 seed.
- **Ablation:** không cross-fitting (đo leakage); không cắt tỉa; các chiến lược context; từng backbone; đặc trưng văn bản tự do bật/tắt.

## 7. Điều kiện tiếp tục / dừng

| Cổng | Kiểm tra | Nếu thất bại |
|---|---|---|
| G0 (Ngày 1) | Cài được TabPFN/TabICL, license cho nghiên cứu, chạy được trên GPU hiện có | Đổi backbone hoặc dừng |
| G1 | Trên ≥ 3 dataset, TFM-ED ≥ CDC hoặc ngang CDC nhưng setup rẻ hơn rõ | Nếu thua rõ: chuyển thành bài phân tích cơ chế (tự nhiễm bẩn) hoặc dừng |
| G2 | Cắt tỉa lặp có lợi đo được ở mức bẩn cao | Bỏ tuyên bố C2; giữ phân tích |

## 8. Kế hoạch thời gian

- **Bản ACIIDS (khoảng 7–10 ngày):** Ngày 1 cài đặt và G0; Ngày 2–3 điểm ô + cross-fitting trên 4 dataset; Ngày 4 cắt tỉa và chiến lược context; Ngày 5–6 baseline CDC/ZeroED/Raha; Ngày 7 ablation; Ngày 8–10 viết. Với 2 người chạy song song (một người điểm TFM, một người baseline), có thể nén vào 6 ngày, nhưng chỉ nộp nếu qua G0–G1 trước tối 29/10.
- **Bản A*/Q1 (6–8 tuần):** thêm backbone, REIN, phân tích lý thuyết đơn giản về độ lệch do nhiễm bẩn, nghiên cứu lai với LLM, artifact.

## 9. Lộ trình nâng cấp

1. Lý thuyết: độ lệch của dự đoán in-context dưới nhiễm bẩn ε-contamination; điều kiện để cắt tỉa hội tụ.
2. Mở rộng sang sửa lỗi (imputation in-context cho ô bị gắn cờ) và so sánh với Baran.
3. Lai với Ý tưởng 1: TFM-ED làm proxy cho chứng nhận. Một "pipeline tin cậy" hoàn chỉnh có thể thành bài journal tổng hợp.
4. Venue: KDD (ADS hoặc research), ICDE; journal KBS/ESWA/DMKD.

## 10. Phản biện dự kiến

| Phản biện | Trả lời |
|---|---|
| "Chỉ là CDC thay imputer bằng TabPFN" | Phần mới gồm tự nhiễm bẩn khi in-context, chiến lược context có kiểm chứng, không train. So sánh trực tiếp với CDC; nếu không vượt thì không tuyên bố |
| "TFM không xử lý văn bản tự do" | Nêu rõ giới hạn; lai với LLM; báo cáo theo loại lỗi |
| "Tiêm lỗi synthetic thiên lệch" | Kết quả chính trên lỗi thật của RAHA; synthetic chỉ cho đường liều–đáp ứng |
| "License TabPFN" | Kiểm tra từ Ngày 1; có phương án TabICL |

## 11. Rủi ro

- Novelty bị phủ nếu có preprint 2026 làm đúng việc này. **Bắt buộc tra cứu lại** (arXiv, ICDE/VLDB/KDD 2026) khi chốt thuật toán.
- Hiệu năng TFM trên bảng nhiều cột văn bản (Rayyan, Movies) có thể kém. Đây cũng là một phát hiện.
- Phần cứng chưa đo (VRAM). Cần kiểm kê phần cứng trước.

## 12. Abstract nháp ([·] là placeholder)

> Tabular foundation models predict any column from the others in a single in-context forward pass, which suggests a training-free and API-free measure of how plausible each cell is. We study this idea for cell-level error detection and identify its central obstacle: the context is the dirty table itself. We propose masked in-context likelihood scores with cross-fitting and an iterative context-trimming procedure that limits self-contamination. On [k] benchmarks with real errors, our detector achieves [·] cell-level F1 compared with [·] for conformal data cleaning and [·] for LLM-based zero-shot detection, at zero API cost. A controlled analysis shows that [mechanism finding].

## 13. Tài liệu tham khảo cốt lõi

- Jäger, Biessmann, AISTATS 2024 (CDC): https://proceedings.mlr.press/v238/jager24a — VERIFIED
- ZeroED, ICDE 2025: https://arxiv.org/abs/2504.05345 — VERIFIED
- Model-Aware Data Cleaning for TFMs: https://arxiv.org/abs/2604.25154 — search-level
- Noise Immunity in In-Context Tabular Learning: https://arxiv.org/abs/2604.04868 — search-level
- TabICL: https://arxiv.org/abs/2502.05564 — search-level
- Hollmann và cs., TabPFN v2, Nature 2025 — kiến thức nền; kiểm tra metadata và license
- CURED demonstrator (mô tả CDC): https://arxiv.org/abs/2607.20140 — search-level
