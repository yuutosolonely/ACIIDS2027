# Ý tưởng 2 — VeriRule

**Working title (EN):** *VeriRule: Trust-but-Verify Validation of LLM-Proposed Integrity Constraints with Human-Checked Violations and False-Discovery Control*
**Tên tiếng Việt:** Kiểm định ràng buộc toàn vẹn do LLM đề xuất bằng kiểm tra vi phạm có người xác nhận, kèm kiểm soát tỷ lệ chấp nhận sai

| Mục | Nội dung |
|---|---|
| Hạng (Claude) | **2/5**. Người dùng chưa chọn |
| Trạng thái | **EXPERT HYPOTHESIS**. Chưa có code phương pháp. Xây từ công cụ mở: FD discovery (TANE/HyFD), LLM API hoặc model mở, RAHA public |
| Khả năng kịp ACIIDS 31/10/2026 | **Trung bình nếu có 2 người chuyên trách**, với bản thu hẹp (chỉ FD/CFD, 3–4 dataset). Bản đầy đủ có DC cần 3–4 tuần. Chỉ nộp khi qua cổng chất lượng tối 29/10 |
| Session phù hợp | **DADIT** (data reliability/consistency/quality); **DMPI** (statistical methods); **ADMTA** (rule mining) |
| Đích nâng cấp | VLDB/SIGMOD/ICDE nếu có DC đầy đủ, nghiên cứu chuyên gia và lý thuyết phân bổ; TKDE/Information Systems cho bản journal. Kiểm tra rank/quartile khi chọn |
| Loại bài | Phương pháp + bảo đảm thống kê + đánh giá trên benchmark có ground truth |

> Không có bảo đảm được nhận bài.

---

## 1. Tóm tắt một đoạn

Phát hiện lỗi dựa trên ràng buộc (FD, CFD, denial constraint) mạnh và dễ giải thích, nhưng chỉ hữu ích khi **ràng buộc đúng**. Thuật toán khám phá DC tự động sinh ra phần lớn ràng buộc sai: Martin và cs. (VLDB 2025) báo cáo tỷ lệ DC sai **hiếm khi dưới 95%** (SOURCE-REPORTED, qua kết quả tìm kiếm). LLM đề xuất được ràng buộc hợp lý về ngữ nghĩa (LLMClean, Cocoon, TabClean). Tuy vậy, cách chấp nhận hiện nay dựa trên heuristic. Ví dụ phổ biến là loại ràng buộc khi tỷ lệ dòng vi phạm vượt một ngưỡng (như 10%), hoặc dùng LLM-as-judge như một luận văn TU Wien. Không cách nào có bảo đảm thống kê. Vấn đề cốt lõi là **mỗi vi phạm mang hai nghĩa**: dữ liệu sai, hoặc ràng buộc sai (một ngoại lệ thật). VeriRule để con người kiểm một mẫu nhỏ các vi phạm. Mỗi lần kiểm trả lời cùng lúc hai câu hỏi: ô này có lỗi không (làm sạch), và luật này có ngoại lệ thật không (kiểm định). Một e-process tuần tự cho từng luật, kết hợp e-BH, kiểm soát **FDR của tập luật được chấp nhận** dưới phụ thuộc tùy ý giữa các luật. Phân bổ thích nghi dồn công sức vào luật gần ranh giới quyết định và có ích nhiều cho downstream.

## 2. Vấn đề và động lực

- **Khám phá thuần dữ liệu overfit:** trên một instance hữu hạn, rất nhiều FD/DC "đúng ngẫu nhiên", ví dụ khi vế trái gần là khóa. Martin và cs. quy nguyên nhân cho định nghĩa validity hiện hành (SOURCE-REPORTED).
- **LLM bổ sung ngữ nghĩa nhưng có thể bịa:** một luật hợp lý về ngữ nghĩa vẫn có thể sai trên dữ liệu cụ thể (ngoại lệ hợp pháp). Ngược lại, luật đúng vẫn bị vi phạm nhiều khi dữ liệu bẩn.
- **Heuristic tỷ lệ vi phạm trộn hai nguồn sai:** ngưỡng 10% không phân biệt được "dữ liệu bẩn nhiều" với "luật sai". Nó loại nhầm luật đúng trên bảng bẩn, và giữ nhầm luật sai trên bảng sạch.
- **Nhu cầu thực tiễn:** catalogue ràng buộc viết tay dễ "mục nát" khi schema đổi (tham chiếu cột không còn tồn tại), còn catalogue tự sinh thì thiếu kiểm định. VeriRule biến catalogue tự sinh thành **catalogue có kiểm định**.

## 3. Công trình gần nhất và ranh giới đóng góp

| Công trình | Đã làm gì | Còn thiếu so với VeriRule | Mức xác minh |
|---|---|---|---|
| Martin và cs., VLDB 2025, *How and why false denial constraints are discovered* (và LIMA, PVLDB 2026) | Phân tích vì sao DC sai được khám phá; đề xuất định nghĩa validity mới; khám phá DC tăng dần | Không dùng ngữ nghĩa LLM; không có kiểm định có người với bảo đảm FDR | SOURCE-REPORTED (search) |
| LLMClean (arXiv 2404.18681) | LLM sinh ontological FD, kể cả denial dependencies, để làm sạch | Không có cơ chế chấp nhận luật có bảo đảm | VERIFIED (arXiv listing) |
| Luận văn TU Wien 2025: LLM sinh data quality rules + LLM-as-judge chấm vi phạm | Gần nhất về pipeline | Judge LLM không được hiệu chỉnh; không có kiểm soát lỗi chấp nhận | Search-level |
| Cocoon; TabClean (arXiv 2606.25388) | LLM suy luận luật ngữ nghĩa / chương trình làm sạch tái sử dụng | Không kiểm định thống kê luật | Search-level |
| FDX — Zhang, Guo, Rekatsinas, SIGMOD 2020 | Khám phá FD trên dữ liệu nhiễu bằng góc nhìn thống kê | Không dùng nhãn người; không FDR trên tập luật; không có LLM | Kiến thức nền; kiểm tra metadata |
| Reliable FDs — Mandros và cs., KDD 2017 | Hiệu chỉnh thiên lệch do may rủi khi đo độ mạnh FD | Không phân biệt lỗi dữ liệu với ngoại lệ | Kiến thức nền |
| Relative trust — Beskales và cs., ICDE 2013; Chiang & Miller, ICDE 2011 | Sửa đồng thời dữ liệu và ràng buộc theo nguyên lý thay đổi tối thiểu | Không có bảo đảm thống kê; không dùng nhãn người hay LLM | Kiến thức nền |
| e-BH — Wang & Ramdas, JRSSB 2022; online FDR / multi-armed testing | Công cụ FDR với e-value dưới phụ thuộc tùy ý | Công cụ được mượn, không nhận là mới | Kiến thức nền |

**Phát biểu novelty:**
1. **C1:** hình thức hóa việc chấp nhận luật do LLM đề xuất như **kiểm định đa giả thuyết dựa trên vi phạm có người xác nhận**, với định nghĩa validity tương đối nhãn tham chiếu và có dung sai θ.
2. **C2:** e-process theo luật trên mẫu vi phạm không hoàn lại, kết hợp e-BH. Kết quả là FDR hợp lệ dưới optional stopping và phụ thuộc tùy ý giữa các luật (vi phạm chồng lấn).
3. **C3:** **nhãn dùng hai lần (dual-use):** mỗi lần kiểm vừa là bằng chứng cho test vừa là một lỗi được xác nhận và sửa. Phân bổ tối ưu theo cả bằng chứng lẫn "lỗi tìm được trên mỗi lần kiểm".
4. **C4:** đánh giá trên benchmark có bản clean. Đo FDR và power ở mức luật, F1 phát hiện lỗi downstream, và khả năng tổng quát hóa sang phần dữ liệu giữ lại.

**Không tuyên bố:** LLM tự biết luật đúng; luật được chấp nhận đúng ngoài phạm vi dữ liệu và định nghĩa tham chiếu; thuật toán khám phá DC mới.

## 4. Câu hỏi nghiên cứu và giả thuyết

- **RQ1:** Heuristic hiện hành (tỷ lệ vi phạm, LLM-as-judge) có FDR mức luật bao nhiêu trên benchmark có ground truth?
- **RQ2:** VeriRule có đạt FDR ≤ α thực nghiệm không, và với bao nhiêu lần kiểm?
- **RQ3:** Ở cùng số lần kiểm, VeriRule có cho F1 phát hiện lỗi downstream tốt hơn khám phá thuần dữ liệu, LLM + heuristic và LLM-as-judge không?
- **RQ4:** Thứ tự ưu tiên theo LLM prior và phân bổ thích nghi đóng góp bao nhiêu? Lợi ích dual-use lớn đến đâu?

Giả thuyết (EXPERT HYPOTHESIS):
- **H1:** heuristic có FDR cao hoặc power thấp, tùy mức bẩn của bảng.
- **H2:** validity giữ được theo cấu trúc e-BH.
- **H3:** phần lớn luật ứng viên được quyết định với rất ít lần kiểm, vì luật sai thường lộ ngoại lệ sớm còn luật đúng có vi phạm toàn là lỗi.
- **H4:** lỗi tìm được trong quá trình kiểm định chiếm phần đáng kể so với lỗi mà detector phát hiện.

## 5. Phát biểu bài toán hình thức (bản nháp cần chuẩn hóa)

- Bảng bẩn D̃, bản tham chiếu D (clean). Ứng viên φ_1..φ_m (FD X→Y, CFD, DC đơn giản, luật miền/định dạng) do LLM đề xuất, cùng các ứng viên từ thuật toán khám phá.
- Với mỗi φ, tập đơn vị vi phạm V_φ trên D̃. Với FD, đây là các tuple thuộc tập tối thiểu cần xóa để thỏa φ (kiểu g3) hoặc các cặp xung đột. Với DC, đây là các cặp tuple vi phạm.
- Nhãn ẩn của một đơn vị v: **lỗi** (vi phạm biến mất trên D) hoặc **ngoại lệ** (vi phạm còn trên D).
- φ **hợp lệ** khi số ngoại lệ ≤ θ·N, với θ = 0 cho luật chính xác. Kèm điều kiện **không tầm thường** khai báo trước (ví dụ vế trái không gần khóa, đo bằng reliable-FD measure), để loại luật "đúng ngẫu nhiên".
- H_0^φ: φ không hợp lệ. Lấy mẫu đều không hoàn lại từ V_φ, xây e-process cho tỷ lệ ngoại lệ, chấp nhận φ khi bác bỏ H_0^φ qua e-BH ở mức α.
- **Giả định cần đo, không mặc định:** ngoại lệ trên D xuất hiện thành vi phạm trên D̃. Có thể sai khi lỗi tình cờ che ngoại lệ; báo cáo tần suất.
- Luật không có vi phạm trên D̃ không kiểm được bằng vi phạm. Phân loại riêng là "hợp lệ trên instance" và đánh giá tổng quát hóa trên phần dữ liệu giữ lại.

## 6. Phương pháp đề xuất

```text
Profile + mẫu dòng ──► LLM đề xuất luật (kèm độ tin prior) ─┐
Thuật toán khám phá (TANE/HyFD, DC đơn giản) ──────────────┴─► Tập ứng viên + bộ lọc "không tầm thường"
                                   │
                  Liệt kê vi phạm V_φ trên bảng bẩn
                                   │
   Vòng lặp ngân sách: chọn luật φ* = argmax  [E Δlog e_φ · w_φ + λ·P(lỗi | vi phạm)] / chi phí
                                   │
   Người kiểm 1 vi phạm ──► nhãn {lỗi, ngoại lệ} ──► cập nhật e_φ ; nếu lỗi: ghi nhận sửa
                                   │
   Dừng: hết ngân sách hoặc mọi luật đã quyết ──► e-BH(α) ──► tập luật chấp nhận
                                   │
   Phát hiện lỗi bằng luật được chấp nhận + danh sách lỗi đã xác nhận
```

Chi tiết:
1. **Đề xuất:** 1–3 lời gọi LLM mỗi bảng (profile cột + mẫu dòng), xuất luật ở cú pháp máy đọc được kèm điểm tin cậy prior. Prior chỉ dùng để **ưu tiên**, không bao giờ tham gia tính validity.
2. **Bộ lọc không tầm thường:** tiêu chí khai báo trước (support, độ gần khóa của vế trái). Ghi lại số luật bị lọc.
3. **e-process:** betting test cho tỷ lệ ngoại lệ trong lấy mẫu không hoàn lại. Có thể dùng hypergeometric cố định cỡ mẫu làm phương án dự phòng.
4. **Phân bổ:** chính sách predictable giữ validity của từng e-process. Khi quyết định thì dùng e-BH trên các e-value đã dừng.
5. **Phương án tiết kiệm (tùy chọn):** LLM-as-judge làm proxy cho từng vi phạm, chỉ để ưu tiên hoặc làm control variate. Tuyệt đối không thay nhãn người trong chứng chỉ.

## 7. Mục tiêu lý thuyết — CHƯA chứng minh

- **P1:** FDR ≤ α cho tập luật chấp nhận, dưới phụ thuộc tùy ý và quy tắc dừng thích nghi. Dựa trên tính chất của e-BH với e-process đã dừng; cần viết đúng điều kiện.
- **P2:** cận số lần kiểm kỳ vọng cho luật hợp lệ (mọi vi phạm là lỗi) và luật sai (tỷ lệ ngoại lệ ρ > θ).
- **P3 (nâng cấp):** chính sách phân bổ đồng tối ưu "bằng chứng + lỗi tìm được" theo một hàm lợi ích khai báo trước.

## 8. Thiết kế thực nghiệm

- **Dữ liệu:** RAHA Hospital, Flights, Beers, Rayyan, Tax, Movies (public, có bản clean/dirty). Có thể thêm lỗi tiêm có kiểm soát (BART, hoặc trình sinh lỗi "authentic" bằng LLM, arXiv 2507.10934) để đo theo mức bẩn. Bộ DC chuẩn của HoloClean cho Hospital/Tax nếu tải được (**UNVERIFIED**).
- **Ground truth luật:** validity và tầm thường tính trên D. Tổng quát hóa đo trên tách dòng giữ lại.
- **Baseline:**

| Mã | Baseline |
|---|---|
| B1 | TANE/HyFD (FD) và DC discovery cơ bản với ngưỡng xấp xỉ |
| B2 | FDX |
| B3 | LLM đề xuất + ngưỡng tỷ lệ vi phạm (heuristic phổ biến) |
| B4 | LLM đề xuất + LLM-as-judge chấm vi phạm |
| B5 | Kiểm vi phạm lấy mẫu đều, test cố định cỡ mẫu + BH |
| Oracle | Luật đúng trên D / bộ DC chuẩn nếu có |

- **Chỉ số:** FDR và power mức luật; số lần kiểm; P/R/F1 phát hiện lỗi mức ô khi dùng luật chấp nhận; số lỗi tìm được trong kiểm định; tổng quát hóa; chi phí LLM (USD) và thời gian.
- **Protocol:** α ∈ {0.05, 0.1}; θ ∈ {0, 0.005, 0.01}; ngân sách kiểm ∈ {50, 100, 200, 500}; R ≥ 200 seed lấy mẫu; tách dev/test cho mọi siêu tham số; báo cáo mọi dataset.
- **Ablation:** bỏ LLM prior; bỏ phân bổ thích nghi; bỏ bộ lọc tầm thường; LLM-as-judge thay người; chỉ FD so với FD + DC.

## 9. Điều kiện tiếp tục / dừng

| Cổng | Kiểm tra | Nếu thất bại |
|---|---|---|
| G1 | Trên ≥ 3 dataset, B3/B4 có FDR mức luật cao rõ hoặc power thấp rõ | Nếu heuristic đã tốt: động lực yếu, chuyển trọng tâm sang dual-use cleaning hoặc dừng |
| G2 | Validity mô phỏng đạt | Sửa test trước khi viết |
| G3 | Ở cùng số lần kiểm, F1 downstream ≥ baseline tốt nhất trên ≥ 2 dataset | Định vị thành bài phân tích + bảo đảm; bỏ tuyên bố hiệu quả |

## 10. Kế hoạch thời gian

- **Sprint ACIIDS 6 ngày (2 người, bản FD/CFD):** Ngày 1 sinh ứng viên (LLM + TANE/HyFD) và liệt kê vi phạm trên 4 dataset. Ngày 2 e-process, e-BH, mô phỏng validity (dùng chung module thống kê với Ý tưởng 1). Ngày 3 thí nghiệm chính. Ngày 4 ablation và cổng chất lượng (tối 29/10). Ngày 5–6 viết. Nếu chưa qua G1–G2 thì không nộp.
- **Bản đầy đủ (3–4 tuần):** thêm DC, dataset, lỗi tiêm có kiểm soát, nghiên cứu chuyên gia. Dùng chung bộ công cụ audit/e-process với Ý tưởng 1, nên chi phí cận biên thấp.

## 11. Lộ trình nâng cấp lên Q1 / A*

1. DC tổng quát và CFD; ràng buộc liên bảng (FK, tổng hợp).
2. Nghiên cứu với chuyên gia thật: đo chi phí kiểm vi phạm và độ đồng thuận.
3. Bảo trì luật khi schema hoặc dữ liệu tiến hóa: kiểm định lại tăng dần, xử lý hiện tượng schema rot.
4. Lý thuyết phân bổ dual-use (P3).
5. Tích hợp với Ý tưởng 1: luật đã kiểm định làm proxy cho chứng nhận dòng sạch.

## 12. Phản biện dự kiến và cách trả lời

| Phản biện | Trả lời |
|---|---|
| "Relative trust đã cân bằng sửa dữ liệu và sửa luật" | Các phương pháp đó dựa trên thay đổi tối thiểu, không có bảo đảm thống kê, không dùng nhãn người hay ngữ nghĩa LLM. VeriRule so sánh và trích dẫn trực tiếp |
| "LLM-as-judge rẻ hơn người" | Thực nghiệm đo FDR của judge-only. Judge được giữ như proxy ưu tiên, không thay chứng chỉ |
| "FD là chủ đề cũ" | Đóng góp nằm ở cơ chế chấp nhận có bảo đảm cho luật do LLM đề xuất; có DC và CFD |
| "Validity phụ thuộc θ" | Phân tích độ nhạy; θ khai báo trước theo nhu cầu nghiệp vụ |

## 13. Rủi ro

- Ground truth "luật đúng" dễ tranh cãi. Giảm thiểu bằng định nghĩa vận hành rõ (validity trên D + không tầm thường + tổng quát hóa) và báo cáo cả ba.
- Liệt kê vi phạm DC theo cặp có độ phức tạp O(n²). Giới hạn DC hai tuple trên vị từ đơn giản và lấy mẫu cặp.
- Thời gian. Đây là lý do xếp sau Ý tưởng 1 cho deadline 31/10.

## 14. Khung bài và abstract nháp ([·] là placeholder)

Cấu trúc: Intro (ví dụ luật "ZIP → City" đúng nhưng bị vi phạm do lỗi, và luật "HospitalName → Phone" sai do chuỗi bệnh viện) → Related → Problem → VeriRule → Guarantees → Experiments → Limitations.

> Integrity constraints are among the most effective and interpretable signals for data error detection, but only when they are correct. Automatically discovered constraints are dominated by spurious ones, and constraints proposed by large language models come without any guarantee. We present VeriRule, which validates LLM-proposed constraints by having humans inspect a small sample of their violations, where each inspection both tests the rule and confirms or repairs a data error. Sequential e-values combined with the e-BH procedure control the false discovery rate of accepted rules under arbitrary dependence. On [k] benchmarks, VeriRule accepts rules with FDR ≤ [α] using [·] inspections and improves downstream detection F1 by [·] over [baseline].

## 15. Tài liệu tham khảo cốt lõi

- Martin và cs. *How and why false denial constraints are discovered*, VLDB 2025 — https://upcommons.upc.edu/entities/publication/50c84d70-d4b4-4013-af3a-fa32dc9262bf/full; các bài PVLDB 19: https://www.vldb.org/pvldb/vol19/p4762-martin.pdf, https://www.vldb.org/pvldb/vol19/p2086-martin.pdf — search-level, cần đọc full text
- LLMClean, arXiv 2404.18681 — https://arxiv.org/abs/2404.18681
- TabClean, arXiv 2606.25388 — https://arxiv.org/abs/2606.25388 — search-level
- Luận văn TU Wien (LLM-generated data quality rules): https://repositum.tuwien.at/handle/20.500.12708/221852 — search-level
- *Towards Practical Benchmarking of Data Cleaning Techniques: On Generating Authentic Errors via LLMs*, arXiv 2507.10934 — search-level
- FDX (SIGMOD 2020); Mandros và cs. (KDD 2017); Beskales và cs. (ICDE 2013); Chiang & Miller (ICDE 2011); Wang & Ramdas e-BH (JRSSB 2022) — kiến thức nền, kiểm tra metadata trước khi trích dẫn
