# Xếp hạng ý tưởng và kế hoạch chia việc cho team

**Ngày:** 25/10/2026. **Người đọc:** trưởng nhóm và các thành viên sẽ nhận việc.
**Phạm vi:** xếp hạng toàn bộ ý tưởng đã xét theo **giá trị nội tại**. Không phụ thuộc code, log hay dự án cũ nào. Mọi ý tưởng dùng **dữ liệu công khai**, tối đa **1 GPU**, khung thời gian **2–3 tháng**. Chi tiết kỹ thuật từng ý tưởng nằm trong các file `IDEA_*.md` cùng thư mục.

> Không ý tưởng nào có bảo đảm được nhận bài. Thứ hạng dưới đây là đánh giá chuyên môn (EXPERT HYPOTHESIS) trước thực nghiệm, không phải xác suất được nhận.

---

## 1. Bảng xếp hạng cuối

| Hạng | Ý tưởng | Một câu | Loại bài | Kịp ACIIDS 31/10 (có team)? | Đích nâng cấp | Số người | GPU |
|---|---|---|---|---|---|---|---|
| **1** | [CertiClean](IDEA_1_CertiClean.md) | Chứng nhận rằng tập dòng mà detector kết luận "sạch" chỉ chứa tối đa ε% dòng lỗi, nhờ một lượt kiểm tay nhỏ | Phương pháp + bảo đảm thống kê | **Có** | SIGMOD/VLDB/ICDE; TKDE, VLDB Journal | 2 | Không bắt buộc |
| **2** | [VeriRule](IDEA_2_VeriRule.md) | Kiểm định luật dữ liệu (FD/DC) do LLM đề xuất, kiểm soát tỷ lệ chấp nhận nhầm luật sai | Phương pháp + bảo đảm thống kê | **Có điều kiện** (bản FD/CFD) | VLDB/ICDE; TKDE, Information Systems | 2 | Không |
| **3** | [TabFM-ED](IDEA_3_TabFM-ED.md) | Dùng tabular foundation model phát hiện lỗi từng ô, không huấn luyện, chống nhiễm bẩn ngữ cảnh | Thực nghiệm + phân tích cơ chế | **Có điều kiện** (bản thu hẹp) | KDD/ICDE; KBS, ESWA, DMKD | 1–2 | **Có** |
| **4** | [EquiSchema](IDEA_4_EquiSchema.md) | Kiểm toán: mô hình học trên CSDL nhiều bảng có giữ dự đoán khi đổi cách lưu trữ, có phân biệt vai trò không | Phân tích + benchmark | Không (6–10 tuần) | Datasets & Benchmarks track (NeurIPS/KDD); TKDE | 2 | **Có** + RAM |
| **5** | [CertiNeg](IDEA_5_CertiNeg.md) | Chứng nhận kết quả truy vấn "không tồn tại" trên toán tử LLM | Phương pháp + hệ thống | Không (6–8 tuần) | VLDB/SIGMOD | 1–2 | Ít (encoder đóng băng) |

Rank và quartile của venue/journal phải kiểm tra lại theo ICORE và JCR/SJR năm hiện hành khi chốt nơi nộp. Trong hồ sơ hiện mới xác minh SIGMOD và KDD là A* (ICORE2026).

## 2. Cách chấm điểm

Thang 1–5 cho mỗi tiêu chí; điểm tổng = tổng có trọng số, tối đa 5,0 (quy đổi thang 100 = điểm × 20). Đây là đánh giá chuyên môn **trước thực nghiệm**, không phải đo lường.

Mốc điểm cho từng tiêu chí: **5** = đã có bằng chứng thực nghiệm, không còn nghi ngờ đáng kể; **4** = mạnh, rủi ro còn lại nhỏ; **3** = trung bình, phụ thuộc kết quả pilot; **2** = yếu, có lý do cụ thể để nghi ngờ; **1** = gần như bị loại. Vì chưa ý tưởng nào có pilot, điểm 5 gần như chỉ xuất hiện ở tiêu chí khả thi và fit.

| Tiêu chí | Trọng số | Ý nghĩa |
|---|---:|---|
| Novelty | 25% | Khoảng cách với công trình gần nhất sau tra cứu nhanh |
| Significance | 20% | Tầm quan trọng của vấn đề với cộng đồng và thực tiễn |
| Feasibility | 20% | Làm được với 1 GPU, dữ liệu public, 2–3 tháng |
| An toàn trước baseline | 15% | Điểm cao = ít nguy cơ một baseline đơn giản giải quyết hết |
| Tiềm năng Q1/A* | 10% | Đường nâng cấp rõ ràng |
| Fit ACIIDS | 10% | Khớp special session (DADIT, DMPI, ADMTA, GDAIS) |

| Ý tưởng | Novelty | Significance | Feasibility | An toàn baseline | Q1/A* | Fit | **Tổng** |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 CertiClean | 4 | 4 | 5 | 3 | 4 | 5 | **4.15** |
| 2 VeriRule | 4 | 4 | 4 | 3 | 4 | 5 | **3.95** |
| 3 TabFM-ED | 3 | 4 | 4 | 3 | 3 | 4 | **3.50** |
| 4 EquiSchema | 3 | 4 | 3 | 3 | 4 | 3 | **3.30** |
| 5 CertiNeg | 3 | 4 | 3 | 2 | 4 | 4 | **3.25** |
| V1-SQL (Text-to-SQL hỏi lại) | 1 | 4 | 4 | 2 | 3 | 4 | 2.85 |
| V2-TFM thuần (context selection cho TFM) | 2 | 3 | 4 | 2 | 3 | 3 | 2.80 |
| V2-API (truy hồi theo xung đột API) | 3 | 4 | 2 | 1 | 4 | 2 | 2.70 |
| V2-ID (identity refinement cho GraphRAG) | 2 | 3 | 3 | 2 | 3 | 4 | 2.70 |
| V1-TIME (RAG theo hiệu lực thời gian) | 2 | 3 | 2 | 2 | 3 | 3 | 2.40 |
| V1-GCP (conformal đồ thị, nhãn trễ) | 2 | 3 | 2 | 2 | 3 | 3 | 2.40 |
| V1-MMCP (conformal đa phương thức off-policy) | 2 | 3 | 2 | 2 | 3 | 2 | 2.30 |

Ghi chú:
- **Quy đổi thang 100:** CertiClean 83, VeriRule 79, TabFM-ED 70, EquiSchema 66, CertiNeg 65; các ý tưởng bị loại 46–57. Thứ tự tương đối quan trọng hơn con số tuyệt đối.
- **Điểm sẽ thay đổi sau pilot:** ví dụ, nếu CertiClean qua cổng G2–G3 (validity đạt, thứ tự proxy giảm rõ số ô phải kiểm so với baseline) thì "an toàn baseline" lên 4 và novelty có cơ sở lên 4–5, tổng khoảng 4,3–4,5. Nếu thua cost-aware Neyman thì tổng giảm còn khoảng 3,8.
- **Hạng 4 và 5 gần nhau.** EquiSchema đứng trên vì hiện tượng gần như chắc chắn tồn tại, và rủi ro không tương quan với Ý tưởng 1. Giá trị của CertiNeg phụ thuộc phần phân bổ audit của Ý tưởng 1 có thắng baseline hay không.
- **Ý tưởng 1–3 cùng mảng data quality.** Đây là lợi thế khi chia team: dùng chung dữ liệu, harness đánh giá và module thống kê (mục 4). Ý tưởng 4 đa dạng hóa sang relational deep learning.

## 3. Vì sao các ý tưởng khác không vào top 5

| Ý tưởng | Lý do chính |
|---|---|
| V1-SQL | Đã có tiền lệ rất gần: EIG clarification (arXiv 2507.06467), PleaSQLarify, DPC |
| V2-TFM thuần | Mảng đông (DistPFN, LoCalPFN, VIP-COP, importance-sampled attention). Phần đáng giá được đưa vào TabFM-ED, nơi có ground truth |
| V2-API | Traceback và type checker đã định vị xung đột miễn phí, nên baseline sinh–chạy–sửa cùng ngân sách nhiều khả năng hấp thụ lợi ích. Thiếu benchmark hợp thành đa thư viện; hạ tầng container nặng; lệch chủ đề ACIIDS |
| V2-ID | Query-driven entity resolution đã thiết lập ý "chỉ xử lý thực thể truy vấn cần" (PVLDB 2013, TKDE 2017, PVLDB 2015). Lỗi tự nhiên hiếm, chi phí gán nhãn lớn |
| V1-TIME / V1-GCP / V1-MMCP | Trùng prior (VersionRAG, T-GRAG; delayed ACI; COPP) và cần lý thuyết chưa có |

## 3b. Nhóm Legal AI / SLEAL (bổ sung 25/10/2026)

Dành cho session **LegalAI** và **SLEAL** của ACIIDS. Chấm cùng thang và trọng số như mục 2.

| Hạng | Ý tưởng | Một câu | Novelty | Sig. | Feas. | An toàn baseline | Q1/A* | Fit | **Tổng** | Kịp 31/10? |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| L1 | [CertiClause](IDEA_L1_CertiClause.md) | Chứng nhận "danh mục hợp đồng không chứa điều khoản rủi ro" từ kết luận của LLM | 4 | 4 | 5 | 3 | 4 | 5 | **4.15** | Có (sát) |
| L2 | [LexApplicable](IDEA_L2_LexApplicable.md) | Benchmark + phương pháp xác định quy phạm áp dụng: điều khoản chuyển tiếp, xung đột quy phạm, lex mitior | 4 | 4 | 2 | 3 | 4 | 5 | **3.55** | Không |
| L3 | [LexConsolidate](IDEA_L3_LexConsolidate.md) | Hợp nhất văn bản pháp luật bằng LLM + executor + verifier, đối chiếu bản chính thức | 3 | 4 | 3 | 2 | 4 | 5 | **3.35** | Rất sát |

Ghi chú:
- **LexApplicable có trần cao nhất** trong nhóm Legal. Nếu team có người học luật cam kết gán nhãn, khả thi lên 3–4 và tổng lên 3,75–3,95.
- **CertiClause và CertiClean dùng chung khung thống kê.** ACIIDS quét tương đồng và loại thẳng bài tự đạo văn. Đợt này chỉ nên nộp **một** trong hai, hoặc nộp cả hai với phần phương pháp viết độc lập và đóng góp trung tâm khác nhau (xem `IDEA_L1_CertiClause.md` mục 11).
- **Hướng Legal đã loại sau tra cứu:**
  - Temporal legal RAG thông thường: đã có 3 benchmark năm 2026 (Đức, Pháp, Trung Quốc), và lọc theo ngày giải quyết phần lớn.
  - Citation verification có bảo đảm: CiteGuard (ICML 2026), LabourCrew.
  - Hỏi lại khi thiếu dữ kiện: InsufficiencyBench (2026).
  - Statute→code: DeonticBench, benchmark Catala (NLLP 2025), "By Their Fruits", "Know Your Limits".
  - Dự đoán bản án và truy hồi pháp lý thông thường: quá đông.

**Xếp hạng chung cả 8 ý tưởng:** CertiClean 4,15 = CertiClause 4,15 > VeriRule 3,95 > LexApplicable 3,55 > TabFM-ED 3,50 > LexConsolidate 3,35 > EquiSchema 3,30 > CertiNeg 3,25.

## 4. Hạ tầng dùng chung — làm trước, Ngày 1–2

Ba module này giúp các nhóm chạy song song mà không làm trùng việc.

| Module | Nội dung | Ý tưởng dùng | Người phụ trách |
|---|---|---|---|
| **M1 `audit_stats`** | Cận trên hypergeometric chính xác; betting confidence sequence cho lấy mẫu không hoàn lại; e-process và e-BH; fixed-sequence testing cho tập lồng nhau; bộ mô phỏng validity (R seed) | 1, 2, 5 | R1 (Thống kê) |
| **M2 `dq_bench`** | Tải RAHA; nhãn mức ô từ diff clean/dirty; loại lỗi; metric P/R/F1 mức ô và dòng; giao diện detector chuẩn (`score_cells`, `commit_rows`); detector cơ bản: outlier theo cột, vi phạm FD, LLM zero-shot; wrapper Raha/CDC | 1, 2, 3 | R2 (Kỹ sư dữ liệu) |
| **M3 `infra`** | Git repo; cấu trúc thư mục; config + seed; log kết quả có commit hash; template LaTeX Springer LNCS; script sinh bảng/hình | Tất cả | R0 (Trưởng nhóm) hoặc R2 |

Cấu trúc repo đề xuất:

```text
aciids2027/
├── common/
│   ├── audit_stats/      # M1
│   └── dq_bench/         # M2
├── ideas/
│   ├── certiclean/
│   ├── verirule/
│   ├── tabfm_ed/
│   ├── equischema/
│   └── certineg/
├── prereg/               # ngưỡng, cổng go/no-go, seed, danh sách dataset — commit TRƯỚC khi chạy
├── results/              # mỗi file kèm commit hash + config
└── papers/<idea>/        # LaTeX LNCS
```

## 5. Vai trò

| Mã | Vai trò | Kỹ năng cần | Ý tưởng | Việc Ngày 1 | Việc Ngày 2 |
|---|---|---|---|---|---|
| **R0** | Trưởng nhóm / điều phối / viết chính | Viết khoa học, đọc phản biện, quản lý cổng | Tất cả | Chốt phân công; tạo repo (M3); chia sẻ thư mục này; khóa file `prereg/` | Review thiết kế thí nghiệm từng nhóm; dựng khung bài LNCS |
| **R1** | Thống kê | Xác suất, kiểm định, confidence sequence, e-value | 1 (chính), 2 (e-BH), 5 | M1 bản tối thiểu: hypergeometric UCB + mô phỏng validity | Betting CS WoR, fixed-sequence, e-BH; viết mệnh đề P1–P3 |
| **R2** | Kỹ sư dữ liệu / benchmark | Python, pandas, xử lý CSV, viết harness | 1 (chính), hỗ trợ 2, 3 | M2: tải RAHA, diff nhãn ô, kiểm tay 50 ô | Detector outlier + FD + LLM zero-shot; bảng FDP mở đầu cho Ý tưởng 1 |
| **R3** | DB & ràng buộc | FD/DC, SQL, prompt LLM | 2 (chính) | Cài TANE/HyFD; prompt LLM sinh luật; định nghĩa đơn vị vi phạm | Liệt kê vi phạm trên 4 dataset; nối M1 để chạy e-process |
| **R4** | ML / GPU | PyTorch, TabPFN/TabICL, chạy baseline | 3 (chính) | Kiểm license TabPFN/TabICL; smoke test trên GPU (cổng G0) | Điểm ô có cross-fitting trên 2 dataset; chạy CDC |
| **R5** | Relational deep learning | GNN, RelBench, PyTorch Geometric | 4 (chính) | Cài RelBench + RT; chạy 1 task rel-f1 | Viết rewrite R1–R3 bằng SQL (DuckDB) với kiểm tra round-trip |
| **R6** | Data pipeline đa phương thức (tùy chọn) | Ảnh/văn bản, encoder đóng băng | 5 | Data gate iWildCam (timestamp, camera ID) | Cache dự đoán encoder; dựng nhóm camera-tuần |

Một người có thể giữ hai vai nếu team nhỏ (ví dụ R0 kiêm R1).

## 6. Phân công theo quy mô team

| Số người | Phân công | Bài nộp ACIIDS 31/10 |
|---|---|---|
| **2** | Cả hai làm CertiClean (R1 + R2, một người kiêm R0) | 1 bài: CertiClean |
| **3** | R1, R2 → CertiClean; R3 → VeriRule (R1 hỗ trợ e-BH khoảng 20% thời gian) | CertiClean + VeriRule có điều kiện |
| **4** | Như trên + R4 → TabFM-ED | CertiClean + tối đa 2 bài có điều kiện |
| **5** | Như trên + R0 riêng (chỉ điều phối, viết, review chéo) | Như trên, chất lượng viết tốt hơn |
| **6–7** | Như trên + R5 (1–2 người) → EquiSchema chạy song song, **không nhắm ACIIDS** | Như trên; EquiSchema nhắm D&B 2027 |
| Sau 01/11 | R1/R2 chuyển sang CertiNeg (dùng lại M1) và bản mở rộng A* của CertiClean | — |

**Khuyến nghị số bài nộp ACIIDS:** CertiClean là bài chắc chắn. Mỗi bài có điều kiện chỉ được nộp khi qua cổng chất lượng ngày 29/10 (mục 7) **và** có một người viết chính riêng. Nếu trưởng nhóm không đủ sức review kỹ, giới hạn ở 2 bài. Quy định số bài mỗi tác giả của ACIIDS: **UNVERIFIED**, kiểm tra trên trang submit.

## 7. Lịch sprint ACIIDS (26/10 → 01/11/2026, giờ Việt Nam)

| Ngày | Hạ tầng chung | CertiClean (R1, R2) | VeriRule (R3) | TabFM-ED (R4) | Trưởng nhóm (R0) |
|---|---|---|---|---|---|
| CN 26/10 | M1 tối thiểu, M2 tải RAHA + nhãn ô, M3 repo | Nhãn ô; chạy 3 detector; bảng FDP mở đầu (G1) | Sinh luật (LLM + TANE); đơn vị vi phạm | License + smoke test GPU (G0) | Phân công; khóa `prereg/` |
| T2 27/10 | M1 đầy đủ (betting, e-BH, fixed-sequence) | Tầng 2 theo proxy; tập lồng nhau; B1–B5; mô phỏng validity (G2) | Liệt kê vi phạm 4 dataset; e-process | Điểm ô + cross-fitting 4 dataset | Review thiết kế; khung bài |
| T3 28/10 | Sửa lỗi M1/M2 theo phản hồi | Thí nghiệm chính 6 dataset × detector | e-BH + validity; baseline B1–B5 | Cắt tỉa context; baseline CDC + 1 khác | Viết Intro/Related cho cả 3 bài |
| T4 29/10 | — | Ablation; hình | Thí nghiệm chính; ablation | Ablation; hình | **20:00: cổng chất lượng** |
| T5 30/10 | — | Viết đầy đủ | Viết (nếu qua cổng) | Viết (nếu qua cổng) | Review chéo: mỗi bài được người nhóm khác đọc như "Reviewer 2" |
| T6 31/10 | — | Sửa theo review, kiểm số liệu | Như trên | Như trên | Kiểm format LNCS, ẩn danh |
| T7 01/11 | — | **Nộp trước 12:00** (hạn chót 18:59) | Nộp nếu đạt | Nộp nếu đạt | Xác nhận submission trên EasyChair |

**Cổng chất lượng 29/10, 20:00.** Bài chỉ được nộp khi đạt **tất cả** điều kiện sau:
1. Validity hoặc tính đúng của phương pháp đã kiểm bằng mô phỏng hoặc thí nghiệm, không còn lỗi đã biết.
2. Có bảng chính so sánh với baseline mạnh nhất ở cùng ngân sách, trên ≥ 3 dataset.
3. Có ít nhất một ablation chứng minh thành phần chính có tác dụng, **hoặc** bài đã được định vị lại trung thực theo kết quả.
4. Mọi số trong bảng truy được về commit + config + log.

## 8. Giai đoạn 2 (11/2026 → 01/2027): đường lên Q1/A*

| Luồng | Việc | Đích (kiểm tra deadline khi chốt) |
|---|---|---|
| CertiClean mở rộng | Lý thuyết phân bổ theo chi phí; nghiên cứu người dùng đo thời gian kiểm; thêm detector | SIGMOD/VLDB/ICDE hoặc TKDE |
| CertiNeg | Dùng lại M1; data gate iWildCam/SemBench; tích hợp plan | VLDB/SIGMOD |
| EquiSchema | Rewrite có chứng nhận, role-swap, chẩn đoán theo tầng | D&B track 2027 |
| VeriRule / TabFM-ED | Mở rộng DC hoặc thêm backbone, tùy kết quả sprint | VLDB/ICDE/KDD hoặc journal Q1 |

**Không** nộp cùng nội dung ở hai nơi. Bản journal mở rộng từ bài hội nghị phải theo chính sách tỷ lệ nội dung mới của journal đích.

## 9. Quy tắc làm việc nhóm

1. **Git từ Ngày 1.** Không commit API key; dùng `.env`.
2. **Đăng ký trước:** ngưỡng, cổng go/no-go, seed, danh sách dataset vào `prereg/` trước khi chạy thí nghiệm chính. Không chỉnh theo test set.
3. **Truy vết:** mỗi số trong bài có commit hash + config + đường dẫn log.
4. **Tác giả:** thống nhất danh sách và thứ tự tác giả từng bài **ngay hôm nay**. Gợi ý: người phụ trách chính là tác giả thứ nhất; người làm module dùng chung đứng tên ở các bài dùng module đó.
5. **Ranh giới đóng góp:** CertiClean và CertiNeg dùng chung engine nhưng đóng góp khoa học phải khác nhau. CertiClean và VeriRule dùng chung M1 nhưng là hai bài toán khác nhau. Mỗi bài trích dẫn bài kia nếu cần.
6. **Ẩn danh:** metadata ACIIDS ghi double-blind (chi tiết UNVERIFIED). Không ghi tên, không để link repo lộ danh tính trong bài.
7. **Đồng bộ:** họp 15 phút mỗi sáng: hôm qua làm gì, hôm nay làm gì, đang bị chặn ở đâu. Ghi vào một file log chung.
8. **Trung thực kết quả:** kết quả âm vẫn ghi lại. Không lọc dataset sau khi xem kết quả. Không tuyên bố vượt quá bằng chứng.

## 10. Việc ngay hôm nay

- [ ] R0: chốt quy mô team và gán vai trò theo mục 6; tạo repo; gửi thư mục này cho cả team.
- [ ] Mỗi thành viên: đọc file `IDEA_*.md` của mình, đặc biệt các mục "Công trình gần nhất", "Điều kiện dừng" và "Phản biện dự kiến".
- [ ] R2: tải RAHA từ https://github.com/BigDaMa/raha, viết loader và diff nhãn ô.
- [ ] R1: hypergeometric UCB + mô phỏng validity bản tối thiểu.
- [ ] R3/R4/R5: cài môi trường, chạy smoke test, ghi cấu hình phần cứng (GPU, VRAM, RAM) vào `prereg/hardware.md`.
- [ ] Cả team: thống nhất danh sách tác giả.

## 11. Thông tin cần để tinh chỉnh kế hoạch

1. Số người và kỹ năng chính của từng người (thống kê, DB, ML/GPU, GNN).
2. GPU (model, VRAM) và RAM máy chạy.
3. Ngân sách API LLM (chỉ cần cho detector LLM và VeriRule; khoảng vài USD đến vài chục USD).
4. Ưu tiên của nhóm: tối đa số bài ACIIDS 2027, hay ưu tiên một bài A* chất lượng cao.
