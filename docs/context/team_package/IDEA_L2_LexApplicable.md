# Ý tưởng Legal 2 — LexApplicable

**Working title (EN):** *Which Norm Governs? Applicable-Norm Determination beyond Date Filtering — Transitional Provisions, Norm Conflicts and Lex Mitior for Legal LLMs*
**Tên tiếng Việt:** Quy phạm nào được áp dụng? Xác định quy phạm áp dụng vượt ra ngoài lọc theo ngày: điều khoản chuyển tiếp, xung đột quy phạm và nguyên tắc có lợi cho người phạm tội

| Mục | Nội dung |
|---|---|
| Hạng trong nhóm Legal | **2/3** (điểm 3,55/5 ≈ 71/100). **Trần cao nhất** trong nhóm Legal nếu team có người được đào tạo luật |
| Trạng thái | **EXPERT HYPOTHESIS**. Chưa có dữ liệu hay code |
| Kịp ACIIDS 31/10/2026 | **Không.** Cần 6–10 tuần và người gán nhãn có kiến thức luật |
| Session ACIIDS | **SLEAL:** "Causal and temporal reasoning in legal contexts"; "Formal models of norms, regulations, and legal systems"; "Legal reasoning and argumentation". **LegalAI:** "Legal reasoning, argumentation, and evidence modelling"; "Formal, neuro-symbolic, and hybrid Legal AI"; "Legal benchmarks and expert-based evaluation"; "Multilingual and low-resource Legal AI" |
| Đích nâng cấp | ACL/EMNLP (resource + method); ICAIL/JURIX (rank cần kiểm tra); journal *Artificial Intelligence and Law*; ACIIDS 2028 LegalAI |
| Yêu cầu nhân sự | **Bắt buộc** có ít nhất một người học luật (hoặc cố vấn) để thiết kế và kiểm định nhãn |

> Không có bảo đảm được nhận bài.

---

## 1. Tóm tắt một đoạn

Ba công trình năm 2026 về legal QA theo thời gian cùng chỉ ra rằng: trích **ngày của sự kiện** từ tình huống rồi lọc kho văn bản về phiên bản đang có hiệu lực vào ngày đó giải quyết được phần lớn lỗi. Ba công trình đó là benchmark luật Đức 312 câu (arXiv 2605.23497), FiscalQA Pro cho luật thuế Pháp (arXiv 2608.09393) và LegalSearch-R1 cho luật Trung Quốc (arXiv 2605.25920). Trong thực tiễn pháp lý, phiên bản được áp dụng **không phải lúc nào cũng** là phiên bản có hiệu lực vào ngày sự kiện. Có ba nhóm ngoại lệ:
- **Điều khoản chuyển tiếp:** hợp đồng ký trước ngày luật mới có hiệu lực tiếp tục theo luật cũ; vụ việc đang giải quyết theo thủ tục cũ.
- **Hiệu lực hồi tố và nguyên tắc có lợi cho người phạm tội (lex mitior):** áp dụng luật mới nếu nhẹ hơn.
- **Xung đột quy phạm:** văn bản cấp trên thắng cấp dưới (lex superior), văn bản sau thắng văn bản trước (lex posterior), quy định riêng thắng quy định chung (lex specialis). Ngoài ra còn ngoại lệ của chính các nguyên tắc này.

Đây chính là nơi heuristic "lọc theo ngày" thất bại. Tra cứu nhanh trong phiên **không thấy benchmark LLM nào** cho việc xác định quy phạm áp dụng hay giải quyết xung đột quy phạm. LexApplicable đề xuất: (1) benchmark có kiểm định chuyên gia cho các tình huống này; (2) một lớp suy luận neuro-symbolic biên dịch điều khoản chuyển tiếp và thứ bậc văn bản thành luật áp dụng có thể thực thi, trước khi LLM trả lời.

## 2. Vấn đề và động lực

- **Ví dụ (minh họa, cần chuyên gia xác nhận):** một hợp đồng thuê đất ký năm 2022, tranh chấp phát sinh năm 2025. Luật Đất đai 2024 đã có hiệu lực, nhưng điều khoản chuyển tiếp có thể quy định quan hệ phát sinh trước đó tiếp tục áp dụng quy định cũ trong một số trường hợp. Hệ thống "lọc theo ngày tranh chấp" sẽ trích nhầm luật mới.
- **Ví dụ hình sự:** hành vi thực hiện trước khi Bộ luật Hình sự 2015 có hiệu lực nhưng xét xử sau. Nguyên tắc áp dụng quy định có lợi hơn cho người phạm tội có thể đòi áp dụng luật mới, ngược với trực giác "dùng luật tại thời điểm hành vi".
- **Hệ thống pháp luật Việt Nam phù hợp để xây benchmark:** hầu hết luật có điều khoản chuyển tiếp tường minh; thứ bậc Luật → Nghị định → Thông tư rõ ràng; sửa đổi thường xuyên; có Cơ sở dữ liệu quốc gia về văn bản pháp luật (vbpl.vn). Theo hiểu biết của tôi, văn bản quy phạm pháp luật không thuộc đối tượng bảo hộ quyền tác giả tại Việt Nam (Luật Sở hữu trí tuệ, Điều 15). **Cần kiểm tra lại** trước khi phát hành dataset.
- **Lợi thế cạnh tranh của team Việt Nam:** đọc được nguồn gốc tiếng Việt; trùng chủ đề "Multilingual and low-resource Legal AI" của LegalAI.

## 3. Công trình gần nhất và ranh giới

| Công trình | Đã làm gì | Ranh giới | Mức xác minh |
|---|---|---|---|
| Asking For An Old Friend (arXiv 2605.23497) | 312 câu QA luật Đức đã kiểm định chuyên gia: sửa đổi sau cutoff, câu hỏi trước sửa đổi, câu hỏi nhiều điều khoản. RAG có trích ngày sự kiện + lọc phiên bản cải thiện mạnh | Abstract **không đề cập** điều khoản chuyển tiếp, hồi tố, lex mitior hay xung đột quy phạm. Baseline "trích ngày + lọc" của họ là baseline bắt buộc của bài này | VERIFIED (abstract) |
| Temporal Misgrounding in Legal RAG — FiscalQA Pro (arXiv 2608.09393) | Hàng chục nghìn phiên bản điều luật thuế Pháp; retriever theo ngày đạt độ chính xác cao | Giả định ngày áp dụng đã biết | Search-level |
| LegalSearch-R1 (arXiv 2605.25920) | Agent có cửa sổ hiệu lực cho từng phiên bản; 16 bộ luật Trung Quốc | Như trên | Search-level |
| Ontology-driven Graph RAG for legal norms (arXiv 2505.00039); Deterministic Legal Agents (arXiv 2510.06002) | Mô hình hóa phiên bản; đề xuất kiến trúc và benchmark diachronic | Chưa có benchmark thực nghiệm về chuyển tiếp hay xung đột | Search-level |
| Nghiên cứu argumentation về xung đột quy phạm (ví dụ arXiv 2501.11799) | Giải quyết xung đột bằng argumentation và tô màu đồ thị | Không phải benchmark LLM trên văn bản thật | Search-level |
| DeonticBench (arXiv 2604.04443); statute→Prolog/Catala | Suy luận trên luật bằng lập trình logic | Không xử lý câu hỏi phiên bản nào áp dụng | Search-level |

**Phát biểu novelty:**
1. **C1 (resource):** benchmark đầu tiên (theo tra cứu nhanh) cho **xác định quy phạm áp dụng**: chuyển tiếp, hồi tố/lex mitior, xung đột theo thứ bậc, thời gian và tính đặc thù. Có câu đối chứng nơi lọc theo ngày là đủ.
2. **C2 (phân tích):** chứng minh định lượng nơi baseline "trích ngày + lọc phiên bản" thất bại.
3. **C3 (phương pháp):** lớp *applicability compiler*. LLM biên dịch điều khoản chuyển tiếp thành luật áp dụng trong một DSL nhỏ; solver kết hợp thứ bậc và thời gian để chọn quy phạm; LLM chỉ trả lời trên quy phạm đã chọn, kèm giải thích và có thể từ chối trả lời.

**Không tuyên bố:** thay thế thẩm phán hay luật sư; bao phủ mọi học thuyết giải quyết xung đột; đúng ngoài hệ thống pháp luật đã xây.

## 4. Câu hỏi nghiên cứu và giả thuyết

- **RQ1:** LLM và RAG lọc theo ngày sai bao nhiêu ở từng loại tình huống (chuyển tiếp, lex mitior, thứ bậc, đặc thù, đối chứng)?
- **RQ2:** LLM có nhận ra **nguyên tắc** giải quyết xung đột đúng không, hay đúng đáp án vì lý do sai?
- **RQ3:** Lớp applicability compiler cải thiện độ chính xác chọn phiên bản và chất lượng câu trả lời đến đâu so với baseline mạnh nhất?
- **RQ4:** Lỗi còn lại thuộc loại nào: trích sai mốc thời gian, hiểu sai điều khoản chuyển tiếp, hay thiếu metadata thứ bậc?

Giả thuyết (EXPERT HYPOTHESIS): lọc theo ngày tốt ở câu đối chứng nhưng kém rõ ở câu chuyển tiếp và lex mitior; LLM thiên về "luật mới nhất" (recency bias, phù hợp quan sát của 2605.23497); biên dịch thành luật tường minh giảm lỗi chọn phiên bản nhiều hơn chain-of-thought.

## 5. Thiết kế benchmark

| Nhiệm vụ | Đầu vào | Đầu ra | Nhãn vàng |
|---|---|---|---|
| T1 Temporal applicability | Tình huống có nhiều mốc (giao kết, thực hiện, vi phạm, khởi kiện, xét xử) + kho văn bản nhiều phiên bản | Phiên bản và điều khoản được áp dụng | Luật áp dụng tính từ điều khoản chuyển tiếp đã hình thức hóa, rồi chuyên gia kiểm định |
| T2 Norm conflict | Hai hoặc nhiều quy phạm có vẻ cùng áp dụng | Quy phạm thắng + nguyên tắc (superior/posterior/specialis/ngoại lệ) | Chuyên gia gán; ghi lý do |
| T3 End-to-end QA | Câu hỏi tư vấn | Câu trả lời + trích dẫn **đúng phiên bản** | Chuyên gia hoặc LLM-judge đã kiểm định với chuyên gia |

Quy trình xây:
1. Khai thác điều khoản chuyển tiếp và quy định về hiệu lực từ 20–40 luật có sửa đổi lớn, ưu tiên văn bản 2023–2026 để giảm nhiễm dữ liệu huấn luyện.
2. Hình thức hóa luật chuyển tiếp (người học luật + DSL).
3. Sinh tình huống có kiểm soát bằng mẫu và LLM, thay đổi mốc thời gian quanh ngày hiệu lực. Có câu đối chứng.
4. Hai người gán độc lập, phân xử bất đồng, báo cáo độ đồng thuận (Cohen's κ).
5. Mục tiêu khoảng 400–800 câu cho bản đầu. Con số cuối phụ thuộc năng lực gán nhãn.

Có thể thêm EU law (EUR-Lex) làm hệ thống thứ hai cho tính tổng quát (bản nâng cấp).

## 6. Phương pháp — applicability compiler

```text
Tình huống ──► LLM trích dòng thời gian sự kiện + loại quan hệ pháp luật
                         │
Kho văn bản ──► điều khoản chuyển tiếp ──► LLM biên dịch thành luật áp dụng (DSL), có kiểm tra cú pháp và test
           └──► metadata: cấp văn bản, ngày hiệu lực, quan hệ sửa đổi/thay thế
                         │
             Solver: chọn tập quy phạm áp dụng + chuỗi lý do (nguyên tắc nào, điều khoản nào)
                         │
             LLM trả lời CHỈ dựa trên quy phạm đã chọn, kèm trích dẫn phiên bản
                         │
             Từ chối trả lời khi luật mâu thuẫn hoặc thiếu dữ kiện quyết định
```

## 7. Baseline, chỉ số, protocol

- **Baseline:** LLM thuần (2–3 model, có model mở); long-context đưa toàn bộ các phiên bản; RAG thường; **RAG trích ngày + lọc phiên bản** (theo 2605.23497, baseline quyết định); chain-of-thought có kèm toàn văn điều khoản chuyển tiếp; agent kiểu LegalSearch-R1 nếu tái lập được.
- **Chỉ số:** độ chính xác phiên bản áp dụng (T1); độ chính xác quy phạm thắng và nguyên tắc (T2); độ đúng câu trả lời và trích dẫn đúng phiên bản (T3); chất lượng từ chối trả lời; phân tích theo loại câu và độ xa mốc hiệu lực.
- **Protocol:** tách dev/test theo **văn bản luật** (không lẫn tình huống của cùng một luật giữa dev và test); khóa phiên bản model; báo cáo chi phí.

## 8. Điều kiện tiếp tục / dừng

| Cổng | Kiểm tra | Nếu thất bại |
|---|---|---|
| G0 | Có người học luật cam kết thời gian gán nhãn | Không bắt đầu |
| G1 (pilot 60–80 câu) | Baseline lọc theo ngày sai rõ ở câu chuyển tiếp/lex mitior, nhưng tốt ở câu đối chứng | Nếu lọc theo ngày đủ tốt: thu hẹp thành bài benchmark xác nhận, hoặc dừng |
| G2 | Độ đồng thuận gán nhãn chấp nhận được | Sửa hướng dẫn gán nhãn; thu hẹp loại câu |
| G3 | Applicability compiler vượt baseline quyết định | Định vị thành bài resource + phân tích |

## 9. Kế hoạch (6–10 tuần)

Tuần 1: chọn văn bản, hướng dẫn gán nhãn, pilot G1. Tuần 2–4: xây benchmark, gán nhãn kép. Tuần 4–6: baseline và compiler. Tuần 7–8: phân tích lỗi, viết. Tuần 9–10: dự phòng, mở rộng EU law nếu kịp.

## 10. Lộ trình nâng cấp

- ACL/EMNLP: benchmark đa hệ thống (VN + EU), compiler, phân tích. Trần A* thuộc loại cao nhất trong các ý tưởng Legal, **nếu** dữ liệu tốt.
- Journal *AI and Law*: bản mở rộng có lý thuyết hình thức về luật áp dụng.
- ACIIDS 2028 LegalAI/SLEAL: bản rút gọn nếu cần venue khu vực.

## 11. Phản biện dự kiến

| Phản biện | Trả lời |
|---|---|
| "Lọc theo ngày đã giải quyết temporal QA" | Đúng cho câu đối chứng; benchmark đo riêng các loại ngoại lệ mà lọc theo ngày không thể đúng theo cấu trúc |
| "Tình huống sinh tự động thiếu tự nhiên" | Chuyên gia kiểm định; thêm tập con tình huống từ bản án hoặc giải đáp pháp luật công khai nếu có |
| "Chỉ một hệ thống pháp luật" | Bản nâng cấp thêm EU law; DSL thiết kế độc lập hệ thống |
| "Nhãn pháp lý có thể tranh cãi" | Báo cáo đồng thuận; giữ nhãn "tranh cãi" làm loại riêng |

## 12. Rủi ro

Phụ thuộc chuyên môn luật (rủi ro lớn nhất); chi phí gán nhãn; nhiễm dữ liệu huấn luyện (giảm bằng văn bản 2023–2026); license phát hành dataset (kiểm tra quy định Việt Nam).

## 13. Abstract nháp ([·] là placeholder)

> Recent work shows that extracting the fact date and filtering legislation to the version in force fixes most temporal errors of legal LLMs. We argue that this heuristic is wrong by construction in a large class of cases: transitional provisions, retroactivity and the more-lenient-law principle, and conflicts resolved by lex superior, lex posterior or lex specialis. We introduce LexApplicable, an expert-validated benchmark of [N] applicable-norm determination problems built from [Vietnamese] legislation, and an applicability compiler that translates transitional provisions and norm hierarchies into executable rules before answer generation. Date-filtered retrieval reaches [·]% on control items but only [·]% on transitional and conflict items, while our approach reaches [·]%.

## 14. Tài liệu tham khảo cốt lõi

- Asking For An Old Friend: https://arxiv.org/abs/2605.23497 — VERIFIED (abstract)
- Temporal Misgrounding in Legal RAG (FiscalQA Pro): https://arxiv.org/abs/2608.09393 — search-level
- Can LLMs Time Travel? (LegalSearch-R1): https://arxiv.org/abs/2605.25920 — search-level
- Ontology-Driven Graph RAG for Legal Norms: https://arxiv.org/abs/2505.00039 — search-level
- Deterministic Legal Agents: https://arxiv.org/abs/2510.06002 — search-level
- Policy-Adaptable Methods for Resolving Normative Conflicts: https://arxiv.org/abs/2501.11799 — search-level
- DeonticBench: https://arxiv.org/abs/2604.04443 — search-level
- Cơ sở dữ liệu quốc gia về văn bản pháp luật: https://vbpl.vn — kiểm tra điều khoản sử dụng
