# Ý tưởng Legal 3 — LexConsolidate

**Working title (EN):** *Executable Legislative Consolidation: LLM Extraction and Verified Application of Amendments against Official Point-in-Time Texts*
**Tên tiếng Việt:** Hợp nhất văn bản pháp luật tự động có kiểm chứng: LLM trích xuất và áp dụng sửa đổi, đối chiếu với bản hợp nhất chính thức

| Mục | Nội dung |
|---|---|
| Hạng trong nhóm Legal | **3/3** (điểm 3,35/5 ≈ 67/100). Ground truth tự động tốt nhất trong nhóm Legal |
| Trạng thái | **EXPERT HYPOTHESIS**. Chưa tải dữ liệu, chưa có code |
| Kịp ACIIDS 31/10/2026 (1 người) | **Rất sát.** Chỉ bản hẹp: dữ liệu UK, 1–2 năm văn bản sửa đổi, chỉ sửa đổi dạng văn bản. Rủi ro cao |
| Session ACIIDS | **SLEAL:** "Standards and frameworks for legal knowledge representation"; "Legal data quality and validation"; "Semantic web technologies for legal informatics"; "Interoperability of legal knowledge systems". **LegalAI:** "Analysis of legislation, case law, regulations, and contracts"; "Legal datasets, corpora, and language resources" |
| Đích nâng cấp | ACL/EMNLP (resource + method), JURIX/ICAIL (rank cần kiểm tra); journal *Artificial Intelligence and Law* |
| Không cần | Người học luật để gán nhãn (ground truth lấy từ bản chính thức) |

> Không có bảo đảm được nhận bài.

---

## 1. Tóm tắt một đoạn

Luật thay đổi qua văn bản sửa đổi, ví dụ "In section 3(2), for 'X' substitute 'Y'" hay "Sửa đổi, bổ sung khoản 2 Điều 5 như sau: …". Muốn biết luật hiện hành nói gì, phải **hợp nhất** các sửa đổi vào văn bản gốc. Việc này tốn nhiều công sức và thường chậm. Trang developer của legislation.gov.uk nói rõ có những "effects" **chưa được áp dụng** vào văn bản hiển thị (unapplied effects), và dữ liệu API có thể chậm so với thực tế (VERIFIED qua trang developer/limitations). Hệ thống RAG pháp lý dùng văn bản hợp nhất cũ sẽ trả lời theo luật đã hết hiệu lực. LexConsolidate đặt hợp nhất văn bản thành một bài toán **có ground truth thực thi được**:
1. LLM trích các sửa đổi thành **thao tác có kiểu** trong một DSL nhỏ (đích, loại thao tác, nội dung, ngày hiệu lực).
2. Một bộ thực thi tất định áp dụng các thao tác lên văn bản có cấu trúc.
3. Bộ kiểm tra xác minh hậu điều kiện, rồi đối chiếu kết quả với bản hợp nhất chính thức tại cùng thời điểm.

Hệ thống từ chối và chuyển cho người khi đích sửa đổi mơ hồ, hoặc khi sửa đổi không thuần văn bản.

## 2. Vấn đề và động lực

- **Thực tiễn:** UK phân biệt effects đã áp dụng và chưa áp dụng; có effects được đánh dấu sẽ không áp dụng, kèm ghi chú lý do (VERIFIED, trang changes/developer). Việt Nam có văn bản hợp nhất (VBHN) do cơ quan ban hành thực hiện thủ công (**UNVERIFIED** về độ phủ trên vbpl.vn; cần kiểm tra).
- **Nối với temporal legal RAG:** các công trình 2026 (benchmark luật Đức, FiscalQA Pro, LegalSearch-R1) đều giả định đã có kho phiên bản hợp nhất chính xác. LexConsolidate tạo ra chính kho đó, và đo chất lượng của nó.
- **Ground truth không cần chuyên gia:** bản point-in-time chính thức trước và sau sửa đổi cho phép chấm tự động ở mức ký tự và cấu trúc.
- **Chống nhiễm dữ liệu huấn luyện:** chọn văn bản sửa đổi ban hành sau cutoff của các model (2025–2026).

## 3. Công trình gần nhất và ranh giới

| Công trình | Đã làm gì | Ranh giới | Mức xác minh |
|---|---|---|---|
| NLP hợp nhất văn bản cổ điển: trích "modificatory provisions" (các nhóm Ý, ví dụ Spinosa và cs., ICAIL 2009); mô hình hóa sửa đổi trong Akoma Ntoso | Luật và văn phạm cho câu sửa đổi | Thời kỳ trước LLM; không có executor + verifier + đối chiếu point-in-time quy mô lớn. **Cần tra cứu lại** các bài LLM-based consolidation 2024–2026 trước khi chốt novelty | Metadata **UNVERIFIED** |
| Temporal legal RAG 2026 (2605.23497, 2608.09393, 2605.25920) | Truy hồi theo phiên bản | Dùng kho phiên bản có sẵn; không tạo hay kiểm tra kho | Search-level |
| Ontology-driven Graph RAG for legal norms (2505.00039) | Mô hình phiên bản thành node | Không có bài toán áp dụng sửa đổi | Search-level |
| Trình theo dõi thay đổi bán thủ công (ví dụ tracker EU AI Act) | Ghi lại từng thay đổi theo điều | Thủ công, không phải phương pháp | Search-level |

**Phát biểu novelty:**
1. **C1 (resource):** benchmark hợp nhất có ground truth thực thi được từ dữ liệu chính thức, có tách theo thời gian để chống nhiễm dữ liệu huấn luyện. Phân loại theo kiểu sửa đổi: insert, substitute, repeal, renumber, nhiều thao tác lồng nhau, sửa đổi không thuần văn bản.
2. **C2 (method):** extract → DSL → execute → verify → repair, có từ chối trả lời. So sánh với LLM viết lại trực tiếp toàn văn và với parser luật.
3. **C3 (metric):** **collateral edit rate**, tức tỷ lệ thay đổi ngoài ý muốn ở phần không bị sửa. Đây là lỗi nguy hiểm của LLM viết lại trực tiếp mà accuracy thông thường không thấy.

**Không tuyên bố:** thay thế biên tập viên pháp lý; xử lý đúng mọi sửa đổi không thuần văn bản (ví dụ "applied with modifications", "as if"); hợp nhất có giá trị pháp lý chính thức.

## 4. Câu hỏi nghiên cứu và giả thuyết

- **RQ1:** Parser luật xử lý được bao nhiêu phần trăm sửa đổi theo từng loại? Phần còn lại khó ở đâu?
- **RQ2:** LLM + DSL + executor có vượt LLM viết lại trực tiếp về độ chính xác và collateral edits không?
- **RQ3:** Bộ kiểm tra và vòng sửa lỗi giảm lỗi bao nhiêu? Từ chối trả lời có đúng chỗ không?
- **RQ4 (nâng cấp):** Phương pháp có chuyển được sang tiếng Việt (VBHN), vốn có văn phong sửa đổi khác UK?

Giả thuyết (EXPERT HYPOTHESIS):
- **H1:** văn phong sửa đổi UK rất công thức, nên parser luật đã xử lý tốt phần lớn **sửa đổi văn bản đơn giản**. Đây là killer baseline phải đo trung thực.
- **H2:** LLM viết lại trực tiếp có collateral edit đáng kể.
- **H3:** lợi thế của phương pháp nằm ở sửa đổi nhiều thao tác, tham chiếu lồng, và văn phong không công thức.

## 5. Phương pháp

```text
Văn bản gốc (XML có cấu trúc) + văn bản sửa đổi
          │
  LLM trích thao tác:  {đích: act/section/subsection/para/"từ X", loại: insert|substitute|repeal|renumber,
                        nội dung, ngày hiệu lực/điều kiện}
          │
  Kiểm tra trước: đích tồn tại và DUY NHẤT? chuỗi "X" có xuất hiện đúng một lần?
          │  (không đạt) ──► sửa thao tác với thông báo lỗi │ hoặc từ chối → người
  Executor tất định áp dụng thao tác
          │
  Kiểm tra sau: nội dung mới có mặt, nội dung cũ biến mất, cấu trúc hợp lệ, phần khác KHÔNG đổi
          │
  Văn bản hợp nhất tại thời điểm t ──► đối chiếu bản point-in-time chính thức
```

## 6. Dữ liệu

- **UK (bản chính):** legislation.gov.uk, XML có cấu trúc và bảng effects (provision bị ảnh hưởng, loại effect, đã/chưa áp dụng). License: theo hiểu biết là Open Government Licence (**kiểm tra lại**). Lấy cặp (văn bản trước, văn bản sửa đổi, văn bản sau) cho các effect **đã áp dụng**. Trang developer cảnh báo dữ liệu có thể chậm; chỉ dùng effect đã áp dụng làm ground truth.
- **Tách thời gian:** dev = văn bản sửa đổi trước 2025; test = 2025–2026 (sau cutoff model).
- **Việt Nam (nâng cấp):** văn bản gốc + văn bản sửa đổi + VBHN trên vbpl.vn, nếu đủ độ phủ (**UNVERIFIED**). Tạo hướng "Multilingual and low-resource Legal AI".

## 7. Baseline, chỉ số, protocol

- **Baseline:**
  - Parser luật/văn phạm cho mẫu UK phổ biến: **bắt buộc**, có thể là killer baseline.
  - LLM viết lại trực tiếp toàn văn: 2–3 model, có model mở.
  - LLM + DSL nhưng không có verifier.
  - Oracle trích xuất (thao tác vàng) + executor, làm trần của phần thực thi.
- **Chỉ số:** P/R/F1 mức thao tác (đích, loại, nội dung); exact match mức provision sau hợp nhất; edit distance; **collateral edit rate**; precision của từ chối trả lời; chi phí và độ trễ. Tất cả phân tích theo loại effect.
- **Protocol:** chọn ngưỡng trên dev; test một lần; báo cáo mọi loại effect, kể cả loại thua.

## 8. Điều kiện tiếp tục / dừng

| Cổng | Kiểm tra | Nếu thất bại |
|---|---|---|
| G1 (Ngày 1–2) | Trích được ≥ 500 effect đã áp dụng, kèm văn bản trước/sau đúng thời điểm | Thu hẹp phạm vi hoặc dừng |
| G2 | Đo độ phủ của parser luật theo loại | Nếu parser giải quyết gần hết cả loại khó: chuyển trọng tâm sang benchmark + tiếng Việt |
| G3 | Phương pháp thắng LLM viết lại trực tiếp về collateral edit và thắng parser ở loại khó | Định vị thành bài resource + phân tích |

## 9. Kế hoạch

- **Bản ACIIDS hẹp (1 người, rủi ro cao):** Ngày 1 pipeline dữ liệu UK; Ngày 2 parser + LLM viết lại trực tiếp; Ngày 3 DSL + executor + verifier; Ngày 4 thí nghiệm và cổng chất lượng; Ngày 5–6 viết. Chỉ nộp nếu qua G1–G3 trước 20:00 ngày 29/10.
- **Bản đầy đủ (3–5 tuần):** toàn bộ loại effect, thêm tiếng Việt, phân tích lỗi sâu, công bố dataset.

## 10. Lộ trình nâng cấp

1. Thêm tiếng Việt (VBHN) và EU (EUR-Lex consolidated versions) để chứng minh tổng quát hóa.
2. Xử lý sửa đổi không thuần văn bản bằng biểu diễn hình thức (ví dụ "áp dụng với sửa đổi").
3. Ứng dụng: phân loại và gợi ý xử lý tồn đọng unapplied effects, có đánh giá với biên tập viên.
4. Venue: ACL/EMNLP (resource track), JURIX/ICAIL; journal *AI and Law*.

## 11. Phản biện dự kiến

| Phản biện | Trả lời |
|---|---|
| "Văn phong UK công thức, regex là đủ" | Báo cáo trung thực độ phủ của parser. Đóng góp nằm ở loại khó, collateral edits, tiếng Việt, và bộ kiểm tra/từ chối |
| "Đã có nghiên cứu hợp nhất từ lâu" | Đúng, và trích dẫn. Phần mới là LLM + executor + verifier với đánh giá point-in-time quy mô lớn, có tách thời gian |
| "Ground truth chính thức có thể chậm/sai" | Chỉ dùng effect đã áp dụng; báo cáo các trường hợp bất nhất như một phát hiện data quality |

## 12. Rủi ro

Parser luật quá mạnh trên UK (rủi ro lớn nhất về novelty); xử lý XML phức tạp; license dữ liệu; độ phủ VBHN tiếng Việt chưa rõ.

## 13. Abstract nháp ([·] là placeholder)

> Legal retrieval systems assume an accurate, up-to-date consolidated text of legislation, yet consolidation is laborious and official databases list amendments that have not yet been applied. We cast consolidation as an executable task: an LLM extracts amendments into typed edit operations, a deterministic executor applies them to structured legislation, and a verifier checks pre- and post-conditions before the result is compared with official point-in-time texts. On [N] amendments enacted after the models' training cutoff, our pipeline reaches [·] provision-level exact match, compared with [·] for a rule-based parser and [·] for direct LLM rewriting, which also introduces collateral edits in [·]% of unaffected provisions.

## 14. Tài liệu tham khảo cốt lõi

- legislation.gov.uk developer limitations: https://www.legislation.gov.uk/developer/limitations — VERIFIED (qua search)
- Ví dụ trang effects: https://www.legislation.gov.uk/changes/affecting/asp/2018/9
- Asking For An Old Friend: https://arxiv.org/abs/2605.23497 ; FiscalQA Pro: https://arxiv.org/abs/2608.09393 ; LegalSearch-R1: https://arxiv.org/abs/2605.25920
- Ontology-Driven Graph RAG for Legal Norms: https://arxiv.org/abs/2505.00039
- Spinosa và cs., ICAIL 2009 (NLP cho hợp nhất văn bản) — metadata **UNVERIFIED**, tra cứu trước khi trích dẫn
