# Ý tưởng Legal 1 — CertiClause

**Working title (EN):** *CertiClause: Certifying Clause Absence in LLM-Assisted Contract Due Diligence with Shared-Cost Audits*
**Tên tiếng Việt:** Chứng nhận "hợp đồng không chứa điều khoản rủi ro" trong rà soát hợp đồng có LLM hỗ trợ

| Mục | Nội dung |
|---|---|
| Hạng trong nhóm Legal | **1/3** (điểm 4,15/5 ≈ 83/100) |
| Trạng thái | **EXPERT HYPOTHESIS**. Chưa có code. Dữ liệu public có nhãn chuyên gia |
| Kịp ACIIDS 31/10/2026 (1 người) | **Có, nhưng sát.** Lõi thống kê chạy CPU; proxy LLM 7–8B chạy GPU hoặc API |
| Session ACIIDS | **LegalAI:** "Regulatory compliance, risk management, and RegTech"; "Legal benchmarks and expert-based evaluation"; "Analysis of legislation, case law, regulations, and contracts". **SLEAL:** "Legal data quality and validation"; "Human-AI collaboration in legal practice" |
| Đích nâng cấp | SIGIR (A*, ICORE2026 theo handoff), ACL/EMNLP; journal *Artificial Intelligence and Law* (kiểm tra quartile năm hiện hành) |
| **Cảnh báo trùng lõi** | Cùng khung thống kê với **CertiClean**. Không nộp cả hai vào ACIIDS 2027 trừ khi phần phương pháp thật sự khác (mục 11) |

> Không có bảo đảm được nhận bài.

---

## 1. Tóm tắt một đoạn

Trong due diligence (M&A, mua sắm, cấp vốn), luật sư phải khẳng định một danh mục hợp đồng **không chứa** những điều khoản rủi ro: change of control, liability không giới hạn, non-compete, exclusivity, anti-assignment. Khẳng định "không có" là khó nhất: muốn chắc thì phải đọc hết hợp đồng. LLM có thể trả lời "không có điều khoản liên quan" một cách sai lầm. ContractEval (NLLP 2025) báo cáo các model mã nguồn mở trả lời "no related clause" **nhiều hơn mức đúng, kể cả khi điều khoản có tồn tại** (SOURCE-REPORTED). CertiClause biến kết luận "không có" của LLM trên cả danh mục thành một **chứng chỉ thống kê**: trong tập hợp đồng được trả về là "không có điều khoản loại k", tỷ lệ hợp đồng thực ra có điều khoản đó ≤ ε, với xác suất ≥ 1−δ. Chứng chỉ dựa trên một lượt đọc kiểm có ngân sách. Có hai cấu trúc đặc thù của pháp lý:
1. **Bất đối xứng:** tìm thấy điều khoản thì dừng ngay; khẳng định không có thì phải đọc hết.
2. **Chi phí dùng chung:** đọc một đoạn hợp đồng là biết nhãn của **cả 41 loại** điều khoản cùng lúc. Một lần đọc hết một hợp đồng chứng nhận được nhiều loại "vắng mặt" một lúc.

## 2. Vấn đề và bằng chứng

- **Sai số kiểu "bỏ sót" nguy hiểm nhất:** báo nhầm có điều khoản chỉ tốn thời gian đọc lại; bỏ sót một điều khoản change of control có thể làm hỏng một thương vụ.
- **Bằng chứng gián tiếp:** ContractEval dùng tập test CUAD (4.128 cặp hợp đồng–câu hỏi, 41 loại rủi ro, 102 hợp đồng) và thấy model mở thiên về trả lời "không có" (SOURCE-REPORTED qua search).
- **Bằng chứng trực tiếp cần tạo ở Ngày 1:** chạy 2–3 proxy (LLM mở, classifier nhỏ) trên test CUAD. Đo **tỷ lệ "vắng mặt" sai** theo từng loại điều khoản (RQ1).
- **Khoảng trống:** chỉ số precision/recall theo từng câu hỏi không cho luật sư một phát biểu có bảo đảm ở mức danh mục, mà đó là thứ họ cần để ký báo cáo due diligence.

## 3. Công trình gần nhất và ranh giới

| Công trình | Đã làm gì | Ranh giới với CertiClause | Mức xác minh |
|---|---|---|---|
| **Certifying One-Phase TAR** — Lewis, Yang, Frieder, CIKM 2021; Heuristic Stopping Rules for TAR (2021); SAL stopping (DMKD 2023) | Quy tắc dừng có bảo đảm recall cho review tài liệu (e-discovery), một chủ đề, mức collection | **Đối thủ phương pháp gần nhất.** Họ bảo đảm recall của một collection cho một chủ đề. CertiClause chứng nhận **vắng mặt mức từng hợp đồng × từng loại điều khoản** (FDP của tập trả về), với chi phí đọc dùng chung giữa nhiều loại. Phải so sánh trực tiếp với bản QBCB/QPET chuyển thể | VERIFIED (arXiv 2108.12746) |
| CUAD (Hendrycks và cs., NeurIPS 2021 D&B); MAUD; ContractNLI (Koreeda & Manning, Findings EMNLP 2021) | Dataset hợp đồng có nhãn chuyên gia | Nguồn dữ liệu, không phải đối thủ. License: CUAD và ContractNLI ghi CC BY 4.0 theo nguồn thứ cấp; MAUD chưa rõ | Search-level; **kiểm tra license tại repo gốc** |
| ContractEval (NLLP 2025); CLAUSE (Findings EACL 2026) | Benchmark nhận diện rủi ro điều khoản; benchmark phát hiện sai lệch để audit LLM | Đo hiệu năng, không có chứng chỉ | VERIFIED (ACL Anthology listing) |
| CiteGuard (ICML 2026); LabourCrew (arXiv 2609.27814) | FDR conformal cho câu có trích dẫn trong RAG; cổng conformal risk control cho ý kiến pháp lý | Bảo đảm cho **câu trả lời được sinh ra**, cần calibration có nhãn. CertiClause chứng nhận **vắng mặt** trong tài liệu, với audit dừng sớm bất đối xứng | Search-level |
| Conformal selection (Jin & Candès 2023); risk-limiting audits (SHANGRLA, ALPHA, SUITE) | Công cụ thống kê nền | Mượn và trích dẫn | Kiến thức nền |

**Phát biểu novelty:**
1. **C1:** hình thức hóa *clause-absence certification* mức danh mục: vắng mặt theo nhóm (hợp đồng) × nhiều giả thuyết (loại điều khoản).
2. **C2:** audit hai tầng với dừng sớm bất đối xứng, **chi phí đọc dùng chung** giữa các loại, mô hình chi phí theo độ dài văn bản.
3. **C3:** chứng nhận đồng thời K loại, kiểm soát đa giả thuyết (FDP theo loại, kiểm soát family-wise qua K loại), cộng chọn tập lồng nhau.
4. **C4:** quy tắc phân bổ ưu tiên hợp đồng mà **một lần đọc hết giải quyết được nhiều giả thuyết nhất** trên mỗi từ phải đọc.
5. **C5:** thực nghiệm trên CUAD (và ContractNLI/MAUD nếu license cho phép), nhiều proxy LLM.

**Không tuyên bố:** chứng nhận đúng pháp lý tuyệt đối (chỉ tương đối nhãn chuyên gia của dataset); thay thế luật sư; detector điều khoản mới.

## 4. Câu hỏi nghiên cứu và giả thuyết

- **RQ1:** Tỷ lệ "vắng mặt" sai của LLM trên từng loại điều khoản lớn đến đâu? Dị biệt giữa các loại thế nào?
- **RQ2:** Chứng chỉ có hợp lệ thực nghiệm không (tần suất sai ≤ δ qua R lần audit), kể cả với proxy kém?
- **RQ3:** Ở cùng số từ phải đọc, CertiClause chứng nhận được bao nhiêu cặp (hợp đồng, loại) so với TAR chuyển thể, audit đều và Neyman theo từng loại độc lập?
- **RQ4:** Lợi ích đến từ đâu: dừng sớm, chi phí dùng chung, hay phân bổ?

Giả thuyết (EXPERT HYPOTHESIS):
- **H1:** false absence tập trung ở một số loại điều khoản hiếm hoặc diễn đạt đa dạng.
- **H2:** validity giữ theo cấu trúc test.
- **H3:** chi phí dùng chung tạo lợi thế lớn so với audit độc lập theo loại, vì hợp đồng dài và K = 41.
- **H4:** dừng sớm giúp rất nhiều với loại phổ biến, ít với loại hiếm.

## 5. Phát biểu hình thức

- Danh mục hợp đồng g = 1..G. Mỗi hợp đồng gồm các đoạn p có độ dài w_p (từ). Nhãn chuyên gia Z_{gk} = 1 nếu hợp đồng g chứa điều khoản loại k.
- Proxy LLM sinh tập A_k = {g : LLM kết luận không có loại k}. Tập này **đóng băng trước audit**. Họ lồng nhau A_{k,t} theo điểm tin cậy.
- Đại lượng kiểm soát: FDP_k(A_{k,t}) = Σ_{g∈A_{k,t}} Z_{gk} / max(1, |A_{k,t}|).
- Mục tiêu: với tập loại K* khai báo trước, P[∃ k ∈ K* : FDP_k(A_{k, t̂_k}) > ε] ≤ δ.
- Audit đọc đoạn theo thứ tự proxy. Đọc đoạn p tốn w_p và tiết lộ nhãn mọi loại trong đoạn đó. Gặp loại k thì Z_{gk} = 1 được giải quyết. Đọc hết g giải quyết mọi Z_{gk}. Audit dở dang được xử lý bảo thủ.

## 6. Phương pháp

```text
Danh mục hợp đồng ──► chia đoạn ──► proxy (LLM 7–8B + truy hồi đoạn theo loại; hoặc classifier)
        │                                   │
        │                   A_k = hợp đồng "không có loại k" (đóng băng), điểm tin cậy
        │
  Tầng 1: chọn hợp đồng để audit — ưu tiên  Σ_k (giá trị thông tin cho H_k) / số từ dự kiến phải đọc
        │
  Tầng 2: đọc đoạn theo thứ tự nghi ngờ (gộp mọi loại còn mở) ──► cập nhật mọi H_k cùng lúc
        │
  Test tuần tự cho từng loại (betting / hypergeometric) + kiểm soát family-wise qua K*
        │
  Trả về: với mỗi loại k, tập hợp đồng đã chứng nhận "không có k" + ε, δ, số từ đã đọc
```

Chi tiết cần chốt ở Ngày 1–2: dạng test cụ thể (betting confidence sequence cho lấy mẫu không hoàn lại, hoặc hypergeometric cỡ mẫu cố định làm phương án dự phòng); cách gộp K loại (Bonferroni đơn giản trước, closed testing hoặc gộp e-value sau); mô hình chi phí (số từ, có hệ số cho đoạn bảng biểu và phụ lục).

## 7. Thiết kế thực nghiệm

- **Dữ liệu:** CUAD (khoảng 510 hợp đồng EDGAR, 41 loại, hơn 13.000 nhãn); dùng split chuẩn. ContractNLI (607 NDA, nhãn "not mentioned" đóng vai vắng mặt cho từng hypothesis) làm dataset thứ hai. MAUD nếu license cho phép.
- **Proxy:** LLM mở 7–8B (zero-shot và few-shot); classifier nhỏ train trên split train của CUAD. Proxy được phép có giám sát, vì validity không phụ thuộc proxy. Một **proxy ngẫu nhiên** để kiểm validity.
- **Baseline:**

| Mã | Baseline |
|---|---|
| B0 | Tin LLM, không chứng nhận |
| B1 | Audit đều từng hợp đồng, đọc hết, cận chính xác theo loại + Bonferroni |
| B2 | TAR có bảo đảm (QBCB/QPET) chuyển thể cho từng loại |
| B3 | Neyman theo chi phí, **từng loại độc lập** (không dùng chung chi phí đọc) |
| B4 | Conformal selection, hợp đồng calibration được gán nhãn đầy đủ (tính chi phí đọc) |
| B5 | LLM verifier lượt hai (không có bảo đảm) |

- **Chỉ số:** số cặp (hợp đồng, loại) được chứng nhận trên mỗi 10.000 từ đọc; tần suất chứng chỉ sai qua R = 1.000 seed; FDP thực tế; số điều khoản rủi ro bị bỏ sót trong tập trả về.
- **Lưới tham số:** ε ∈ {0.01, 0.05, 0.1}; δ ∈ {0.05, 0.1}; K* ∈ {5 loại rủi ro cao, cả 41 loại}.
- **Ablation:** bỏ dừng sớm; bỏ chi phí dùng chung (audit độc lập); bỏ phân bổ; proxy ngẫu nhiên; chi phí theo đoạn thay vì theo từ.

## 8. Điều kiện tiếp tục / dừng

| Cổng | Kiểm tra | Nếu thất bại |
|---|---|---|
| G1 (Ngày 1) | Proxy có tỷ lệ vắng mặt sai đáng kể ở ≥ 5 loại | Nếu LLM gần như không bỏ sót: chuyển trọng tâm sang chi phí chứng nhận ở ε nhỏ |
| G2 (Ngày 2) | Validity mô phỏng đạt, kể cả proxy ngẫu nhiên | Sửa test; không nộp khi chưa qua |
| G3 | Chi phí dùng chung thắng B3 ở cùng số từ đọc | Bỏ tuyên bố C4; giữ C1–C3, C5 |

## 9. Kế hoạch 6 ngày (1 người)

| Ngày | Việc |
|---|---|
| CN 26/10 | Tải CUAD; chia đoạn; gán nhãn loại cho đoạn từ span chuyên gia; chạy proxy trên test; bảng vắng mặt sai (G1) |
| T2 27/10 | Test tuần tự, audit hai tầng, B1–B3; mô phỏng validity (G2) |
| T3 28/10 | Chi phí dùng chung + phân bổ; B4–B5; thí nghiệm chính |
| T4 29/10 | Ablation, ContractNLI; hình; **20:00 cổng chất lượng** |
| T5 30/10 | Viết bài LNCS |
| T6 31/10 → 01/11 12:00 | Review chéo, sửa, nộp |

## 10. Lộ trình nâng cấp lên Q1/A*

1. Lý thuyết phân bổ khi chi phí dùng chung và nhiều giả thuyết (bài toán kiểu set-cover có thống kê).
2. Nghiên cứu thời gian đọc thật với sinh viên luật hoặc luật sư (thay giả định chi phí theo từ).
3. Thêm MAUD, hợp đồng tiếng Việt (nếu xây được bộ nhãn nhỏ), đa ngôn ngữ.
4. Tích hợp vào workflow rà soát: báo cáo due diligence kèm chứng chỉ.
5. Venue: SIGIR (cộng đồng TAR), ACL/EMNLP; journal *AI and Law*.

## 11. Quan hệ với CertiClean — đọc kỹ trước khi nộp

Hai ý tưởng dùng **cùng khung thống kê** (audit hai tầng, test tuần tự, tập lồng nhau). ACIIDS quét mọi bài bằng phần mềm kiểm tra tương đồng, và **tự đạo văn bị loại ngay, không qua review** (trang submit chính thức). Có hai lựa chọn:
- **An toàn nhất:** đợt này chỉ nộp **một** trong hai. Chọn CertiClause nếu nhóm muốn vào session LegalAI/SLEAL; chọn CertiClean nếu nhắm DADIT.
- **Nếu nộp cả hai:** hai người viết hoàn toàn độc lập. Bài CertiClause phải lấy C3–C4 (nhiều giả thuyết, chi phí dùng chung, mô hình chi phí đọc) làm đóng góp trung tâm, khác hẳn trọng tâm của CertiClean. Không chép đoạn, hình hay công thức trình bày.

## 12. Phản biện dự kiến

| Phản biện | Trả lời |
|---|---|
| "TAR đã có quy tắc dừng có bảo đảm" | TAR bảo đảm recall mức collection cho một chủ đề. Bài này chứng nhận vắng mặt mức hợp đồng cho nhiều loại, với chi phí dùng chung. So sánh trực tiếp với QBCB/QPET |
| "Nhãn CUAD không phải chân lý" | Chứng chỉ tương đối nhãn chuyên gia của dataset; nêu rõ |
| "Chi phí theo từ không thực tế" | Phân tích độ nhạy; bản nâng cấp đo thời gian thật |
| "Hợp đồng EDGAR là của Mỹ" | Nêu giới hạn; hướng mở rộng đa ngôn ngữ |

## 13. Abstract nháp ([·] là placeholder)

> In contract due diligence, the most consequential claims are claims of absence: that no contract in a portfolio contains, for example, a change-of-control or uncapped-liability clause. Large language models make such claims cheaply but unreliably. We introduce CertiClause, which turns LLM absence claims into portfolio-level certificates: for each clause type, the fraction of returned contracts that actually contain the clause is at most ε with probability at least 1−δ. CertiClause exploits two structures of legal review, namely that finding a clause ends the search while confirming absence requires a full read, and that reading a contract reveals all clause types at once. On CUAD [and ContractNLI], CertiClause certifies [·]× more contract–clause pairs per word read than adapted technology-assisted-review stopping rules, while keeping the empirical failure rate below δ.

## 14. Tài liệu tham khảo cốt lõi

- Lewis, Yang, Frieder. *Certifying One-Phase Technology-Assisted Reviews.* CIKM 2021. https://arxiv.org/abs/2108.12746 — VERIFIED
- Yang, Lewis, Frieder. *Heuristic Stopping Rules for Technology-Assisted Review.* https://arxiv.org/abs/2106.09871 — search-level
- SAL-based stopping rules, Data Mining and Knowledge Discovery 2023. https://link.springer.com/article/10.1007/s10618-023-00961-5 — search-level
- ContractEval, NLLP 2025. https://aclanthology.org/2025.nllp-1.19/ — VERIFIED listing
- CLAUSE, Findings EACL 2026. https://arxiv.org/abs/2511.00340 — search-level
- CUAD: https://arxiv.org/abs/2103.06268 ; https://huggingface.co/datasets/theatticusproject/cuad-qa — kiểm tra license
- MAUD: https://arxiv.org/abs/2301.00876 ; ContractNLI: https://arxiv.org/abs/2110.01799
- CiteGuard (ICML 2026): https://github.com/XiangyuJiang01/citeguard ; LabourCrew: https://arxiv.org/abs/2609.27814 — search-level
