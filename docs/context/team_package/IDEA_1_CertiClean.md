# Ý tưởng 1 — CertiClean

**Working title (EN):** *CertiClean: Certifying the "Clean" Output of Label-Free Data Error Detectors with Cost-Aware Risk-Limiting Audits*
**Tên tiếng Việt:** Chứng nhận tập dòng được kết luận "sạch" của bộ phát hiện lỗi không nhãn, bằng kiểm toán giới hạn rủi ro có tính đến chi phí

| Mục | Nội dung |
|---|---|
| Hạng (Claude, 25/10/2026) | **1/5**. Người dùng chưa chọn |
| Trạng thái | Phương pháp: **EXPERT HYPOTHESIS**, chưa có code. Failure mode: có tín hiệu sơ bộ (mục 2.2); bằng chứng chính phải tái lập trên detector công khai ở Ngày 1 |
| Khả năng kịp ACIIDS 31/10/2026 AoE | **Cao nhất trong 5 ý tưởng**: dữ liệu public có ground truth mức ô, detector proxy công khai và rẻ, lõi thống kê chạy CPU. Cần 2 người chuyên trách |
| Session ACIIDS phù hợp | **DADIT**: "Trustworthy and Intelligent Data Management → Data reliability, consistency, quality, and availability". **DMPI**: "Statistical and stochastic methods for complex data" |
| Đích nâng cấp | SIGMOD/VLDB/ICDE (bản tổng quát hóa + lý thuyết phân bổ); TKDE/VLDB Journal (bản mở rộng). Xếp hạng/quartile phải kiểm tra lại khi chọn venue |
| Loại bài | Phương pháp + bảo đảm thống kê + đánh giá thực nghiệm |

> Không có bảo đảm được nhận bài. Tài liệu này nhằm tối đa hóa xác suất được nhận bằng bằng chứng failure thật, bảo đảm có thể kiểm chứng, baseline mạnh và tính tái lập.

---

## 1. Tóm tắt một đoạn

Các bộ phát hiện lỗi dữ liệu bảng không cần nhãn, dựa trên LLM, đang quyết định dòng nào "đủ sạch" để chuyển xuống downstream. Các thước đo như AUC hay F1 mức dòng không cho biết **tập dòng được cam kết sạch thực sự sạch đến đâu**. Tín hiệu sơ bộ từ một detector LLM không nhãn cho thấy tỷ lệ dòng bị cam kết sạch nhưng thực ra có lỗi dao động **từ 5% đến 100%** tùy dataset và cấu hình (mục 2.2). Hiện tượng này cần được tái lập trên các detector công khai. Khi không có nhãn, người vận hành không biết mình đang ở chế độ nào. CertiClean là một lớp chứng nhận **không phụ thuộc detector**. Với một ngân sách audit nhỏ của con người, nó trả về **tập con lớn nhất** trong tập được cam kết sạch mà tỷ lệ phát hiện sai (FDP) mức dòng ≤ ε, với xác suất ≥ 1−δ theo phép ngẫu nhiên của thiết kế audit. CertiClean khai thác một bất đối xứng chi phí: chỉ cần tìm **một** ô lỗi để bác bỏ một dòng "sạch", còn muốn xác nhận dòng sạch thì phải kiểm **mọi** ô. Proxy của detector chỉ quyết định **thứ tự và phân bổ** audit. Tính hợp lệ của chứng chỉ không phụ thuộc chất lượng proxy.

## 2. Vấn đề và bằng chứng đã có

### 2.1 Bằng chứng chính cần tạo ở Ngày 1 (độc lập, chỉ dùng công cụ công khai)

1. Tải RAHA (Hospital, Flights, Beers, Rayyan, Tax, Movies) và tạo nhãn mức ô từ diff `dirty.csv`/`clean.csv`.
2. Chạy 3–4 detector công khai (mục 8.2). Với mỗi detector, tạo tập commit-clean bằng ngưỡng cố định trước (quantile điểm rủi ro, hoặc quyết định "clean" của detector LLM).
3. Báo cáo FDP thực tế của từng tập theo dataset × detector. Đây là bảng mở đầu bài (RQ1).

### 2.2 Tín hiệu sơ bộ (tùy chọn) — log của một detector LLM không nhãn trước đây

Không bắt buộc cho dự án; chỉ cho biết hiện tượng có tồn tại. Định nghĩa: `decision == "clean"` là commit-clean; `y_true == "err"` là dòng có ít nhất một ô lỗi. Số liệu VERIFIED, tính ngày 25/10/2026.

| Run (log) | Dataset | Số dòng commit-clean | Trong đó thực ra có lỗi | FDP thực tế | Tỷ lệ dòng lỗi trên toàn test |
|---|---|---:|---:|---:|---:|
| `main_hospital_maled_test600` (HAND) | Hospital | 79 | 4 | 5.1% | 25.0% |
| `auto_hospital_test_full` (AUTO) | Hospital | 430 | 75 | 17.4% | 25.0% |
| `main_flights_test_full` (HAND) | Flights | 17 | 6 | 35.3% | 80.6% |
| `auto_flights_test_full` (AUTO) | Flights | 493 | 253 | 51.3% | 80.6% |
| `auto_rayyan_test_full` (AUTO) | Rayyan | 149 | 103 | 69.1% | 76.8% |
| `auto_beers_test_full` (AUTO) | Beers | 711 | 711 | 100% | 100% |
| `main_beers_test_full` (HAND) | Beers | 32 | 32 | 100% | 100% |

**Diễn giải có kiểm soát:**
- Tập commit-clean chỉ "giàu dòng sạch" hơn ngẫu nhiên một chút ở cấu hình AUTO. Ví dụ, FDP 17.4% so với prevalence 25% trên Hospital. Cấu hình HAND sạch hơn nhưng commit ít hơn nhiều. Đây chính là đánh đổi giữa kích thước tập và độ sạch mà chứng nhận theo tập lồng nhau cần xử lý.
- Detector này hiệu chỉnh ngưỡng phía commit-err theo coverage, **không** kiểm soát FDP phía commit-clean. Phần lớn detector hiện nay cũng vậy, nên đây là khoảng trống chung.
- Benchmark RAHA có prevalence mức dòng cao (Flights, Rayyan, Beers). Một phần FDP cao đến từ điều đó. Với Beers, đáp án đúng là **không chứng nhận được gì**. Đây là sanity check tốt: hệ thống phải dám trả về tập rỗng.
- Các số trên là thống kê mô tả log hiện có, không phải kết quả của phương pháp mới.

### 2.3 Vì sao đây là vấn đề quan trọng

Quyết định vận hành thường là "có cho bảng này đi tiếp không?", không phải "AUC bao nhiêu?". Detector không nhãn tiện lợi nhưng không tự đo được độ tin cậy của chính nó trên một bảng mới. Người dùng cần một **phát biểu có bảo đảm về những gì được cho qua**, với chi phí con người nhỏ và đo được.

## 3. Công trình gần nhất và ranh giới đóng góp

| Công trình | Đã làm gì | Còn thiếu so với CertiClean | Mức xác minh |
|---|---|---|---|
| **DQM** — Chung, Krishnan, Kraska, PVLDB 10(11), 2017 | Species estimators ước lượng số lỗi chưa phát hiện sau khi crowd làm sạch | Không có bảo đảm hữu hạn mẫu cho **một tập được chọn**; không thiết kế audit theo proxy; không có ngữ nghĩa "dòng sạch = mọi ô sạch" | VERIFIED (metadata + abstract) |
| **SampleClean** — Wang và cs., SIGMOD 2014 | Làm sạch một mẫu để ước lượng kết quả truy vấn tổng hợp kèm khoảng tin cậy | Mục tiêu là aggregate query, không phải chứng nhận tập output của detector | Metadata theo hiểu biết; **UNVERIFIED** trong phiên |
| **Conformal Data Cleaning (CDC)** — Jäger & Biessmann, AISTATS 2024 | Imputer theo từng cột + conformal sets, gắn cờ ô nằm ngoài tập | Bảo đảm miscoverage **mức ô**, cần train imputer và calibration gần exchangeable; không chứng nhận FDP của tập dòng; không có thiết kế chi phí audit | VERIFIED (PMLR) |
| **Conformal selection** — Jin & Candès, JMLR 2023; conformal e-values cho dữ liệu phân cấp (arXiv 2501.02514); post-hoc conformal selection với e-variables (arXiv 2604.11305) | Chọn tập có kiểm soát FDR nhờ calibration có nhãn | Calibration cần **nhãn đầy đủ** từng dòng. Gán nhãn "sạch" cho dòng calibration đòi kiểm mọi ô, nên đắt. Đây là **baseline bắt buộc** với cùng chi phí gán nhãn | Search-level; cần đọc full text |
| **PPI, Active inference, Stratified PPI** | Kết hợp dự đoán proxy và nhãn người để suy luận hợp lệ | Ước lượng trung bình. Không có ngữ nghĩa "tồn tại lỗi trong nhóm", không có dừng sớm bất đối xứng, không chọn tập lồng nhau | Kiến thức nền; metadata cần kiểm tra |
| **Allocating Human Oversight in AI-Enabled Analytics** — Ye, Lyu, Tao, arXiv 2604.12497 (2026) | Phân bổ ngân sách nhãn người giữa các task bằng tuned PPI + UCB; tham chiếu oracle là Neyman | Mục tiêu ước lượng, không phải chứng nhận tập; không có ngữ nghĩa nhóm/any-error, không có dừng sớm bất đối xứng | VERIFIED (abstract) |
| **Risk-limiting audits** (SHANGRLA, ALPHA, SUITE / "Sweeter than SUITE") | Kiểm toán bầu cử tuần tự bằng test supermartingale, có phân tầng | Nền tảng phương pháp **được mượn và trích dẫn**, không được nhận là của mình. Bối cảnh khác: không có cấu trúc ô-trong-dòng, không có proxy LLM | Metadata **UNVERIFIED** trong phiên |
| **Evergreen** (arXiv 2604.26180) | Kiểm chứng quantified claims, early stopping, confidence sequences | Bối cảnh analytics ngữ nghĩa; là đối thủ chính cho Ý tưởng 5. Cần trích dẫn | Handoff đã đọc |
| Detector LLM không nhãn (ZeroED, ICDE 2025; LLMClean; pipeline LLM-as-judge) | Phát hiện lỗi không cần hoặc cần ít nhãn | Sinh ra tập commit-clean nhưng không chứng nhận độ sạch của tập đó; là đối tượng CertiClean bao lên | ZeroED VERIFIED; còn lại search-level |

**Phát biểu novelty (khẳng định hẹp, kiểm chứng được):**
1. **C1 — Bài toán:** hình thức hóa *false-clean certification* cho detector không nhãn. Đây là một bài toán "vắng mặt mức nhóm" (dòng là nhóm các ô; mở rộng thành thực thể là nhóm các dòng) trên một tập commit đã đóng băng.
2. **C2 — Thiết kế audit hai tầng:** tầng 1 lấy mẫu dòng với xác suất bao gồm đã biết; tầng 2 kiểm các ô theo thứ tự proxy và **dừng ở ô lỗi đầu tiên**. Test anytime-valid (betting supermartingale cho lấy mẫu không hoàn lại) hợp lệ **bất kể chất lượng proxy**. Dòng audit dở dang được xử lý bảo thủ.
3. **C3 — Chứng nhận tập lồng nhau:** fixed-sequence testing trên họ ngưỡng A_1 ⊇ … ⊇ A_T, trả về tập lớn nhất chứng nhận được, với kiểm soát lỗi family-wise.
4. **C4 — Phân bổ theo chi phí:** chọn tầng audit tiếp theo để **tối đa bằng chứng (log-wealth) trên mỗi ô được kiểm**, khai thác chi phí bất đối xứng. So sánh trực tiếp với cost-aware Neyman allocation.
5. **C5 — Nghiên cứu thực nghiệm:** 6 dataset RAHA × nhiều detector (LLM và không LLM), có kiểm tra validity qua hàng nghìn lần ngẫu nhiên hóa audit.

**Không tuyên bố:** lý thuyết conformal/RLA mới tự thân; chứng nhận "sự thật" ngoài nhãn tham chiếu; một detector mới; bảo đảm cho dữ liệu tương lai ngoài bảng đang audit.

## 4. Câu hỏi nghiên cứu và giả thuyết

- **RQ1:** Rủi ro false-clean của detector không nhãn lớn và biến thiên đến mức nào giữa các detector và dataset?
- **RQ2:** CertiClean có đạt validity thực nghiệm không, tức tần suất chứng chỉ sai ≤ δ qua R lần audit? Kể cả khi proxy kém hoặc ngẫu nhiên?
- **RQ3:** Cùng ngân sách ô được kiểm, CertiClean có chứng nhận **nhiều dòng hơn**, hoặc đạt chứng chỉ với **ít ô hơn**, so với uniform audit, cost-aware Neyman, conformal selection và PPI không?
- **RQ4:** Thành phần nào tạo ra lợi ích: thứ tự proxy trong dòng, phân tầng, phân bổ thích nghi hay chọn tập lồng nhau?

Giả thuyết (EXPERT HYPOTHESIS):
- **H1:** rủi ro false-clean dị biệt lớn giữa detector và dataset. Có tín hiệu sơ bộ ở mục 2.2.
- **H2:** validity giữ được theo cấu trúc test (Ville's inequality), độc lập với proxy.
- **H3:** dừng sớm theo proxy giảm mạnh chi phí với bảng rộng (Hospital 20 cột, Movies 17, Tax 15 theo header) khi điểm nghi ngờ mức ô của detector có thông tin. Lợi ích nhỏ với bảng hẹp (Flights 7 cột).
- **H4:** chọn tập lồng nhau chứng nhận được tập lớn hơn so với chứng nhận "tất cả hoặc không gì", khi rủi ro tập trung ở dòng có điểm proxy cao.

## 5. Phát biểu bài toán hình thức

- Bảng có các dòng g = 1..G; dòng g có k_g ô. Nhãn tham chiếu của ô là e_{gj} ∈ {0,1}, trong đó 1 là lỗi so với bản clean. Dòng lỗi được định nghĩa là Z_g = max_j e_{gj}.
- Detector cho điểm rủi ro s_g và tập commit-clean A. Tập này được **đóng băng trước audit**. Họ lồng nhau A_t = {g ∈ A : s_g ≤ t_t}, với t_1 > … > t_T cố định trước.
- Đại lượng cần kiểm soát: FDP(A_t) = Σ_{g∈A_t} Z_g / max(1, |A_t|).
- Mục tiêu: trả về t̂ sao cho P_audit[ FDP(A_t̂) > ε ] ≤ δ. Xác suất lấy theo phép ngẫu nhiên của thiết kế audit; nhãn được coi là cố định, và lỗi của detector có thể tương quan tùy ý.
- Oracle audit: `inspect(g, j)` trả e_{gj} với chi phí c (mức ô), cộng chi phí cố định c_0 mỗi dòng.
- Tầng 2: thứ tự σ_g lấy từ proxy (điểm nghi ngờ từng ô). Dừng khi gặp e = 1. Chi phí τ_g bằng vị trí ô lỗi đầu tiên nếu Z_g = 1, và bằng k_g nếu Z_g = 0.
- Hết ngân sách giữa chừng một dòng thì gán Z_g = 1 (bảo thủ) cho cận trên. Cách này giữ validity.

## 6. Phương pháp đề xuất

```text
Detector bất kỳ (LLM zero-shot, ZeroED, Raha, FD-violation, outlier...) ──► điểm s_g + tập commit-clean A (đóng băng)
                                   │
                    Họ tập lồng nhau A_1 ⊇ A_2 ⊇ … ⊇ A_T (ngưỡng cố định trước)
                                   │
   Tầng 1: lấy mẫu dòng (uniform / phân tầng theo bin của s_g, xác suất đã ghi lại)
                                   │
   Tầng 2: kiểm ô theo thứ tự proxy ──► gặp lỗi: Z_g=1, dừng │ hết ô: Z_g=0
                                   │
   Cập nhật test supermartingale cho từng H_t: FDP(A_t) > ε
                                   │
   Fixed-sequence: từ tập an toàn nhất đến lớn nhất ──► trả về A_t̂ lớn nhất bác bỏ được H_t
                                   │
   Phân bổ tiếp theo: tầng có (kỳ vọng tăng log-wealth) / (kỳ vọng chi phí ô) lớn nhất
```

**Các bước cụ thể:**
1. **Đóng băng.** Ghi hash của A, của s_g và của các ngưỡng t trước khi rút mẫu audit đầu tiên. Nếu sửa A sau audit thì phải dùng epoch mới.
2. **Thiết kế tầng 1.** Phiên bản cơ bản: lấy mẫu đều không hoàn lại trong A_1. Mẫu rơi vào A_t là mẫu đều của A_t (có điều kiện theo số lượng), nên dùng chung được cho mọi H_t. Phiên bản phân tầng: các bin theo s_g, xác suất π_h đã biết, kết hợp các tầng bằng union-intersection kiểu SUITE hoặc test có trọng số. **Quyết định kỹ thuật ở Ngày 1:** chọn dạng test cụ thể.
3. **Tầng 2.** Thứ tự ô theo điểm nghi ngờ mức ô của detector (các trường detector LLM chỉ ra, hoặc điểm vi phạm FD/outlier theo cột), rồi ngẫu nhiên. Ghi lại τ_g.
4. **Test.** H_t: Σ_{g∈A_t} Z_g ≥ ε|A_t|. Dùng betting confidence sequence cho lấy mẫu không hoàn lại với biến bị chặn [0,1]. Bác bỏ khi wealth ≥ 1/δ. Phương án dự phòng đơn giản, hợp lệ và dễ trình bày: cận trên hypergeometric chính xác với cỡ mẫu cố định.
5. **Chọn tập lồng nhau.** Test lần lượt H_T (tập nhỏ, an toàn) → H_{T−1} → …, dừng ở lần đầu không bác bỏ được. Fixed-sequence giữ FWER ≤ δ, không cần hiệu chỉnh đa kiểm định.
6. **Phân bổ theo chi phí (đóng góp C4).** Tại mỗi bước, chọn tầng h tối đa E[Δ log W] / E[cost_h], với E[cost_h] = p̂_h·E[τ | Z=1] + (1−p̂_h)·k̄_h + c_0. Các ước lượng p̂_h và E[τ] được học tuần tự (predictable). Tính predictable giữ validity.

**Đầu ra cho người dùng:** tập A_t̂ đã chứng nhận, ε, δ, số ô đã kiểm, các lỗi tìm thấy trong audit (lợi ích phụ: được sửa luôn), và tập "không chứng nhận được" kèm lý do.

## 7. Mục tiêu lý thuyết — CHƯA chứng minh

| Mệnh đề | Nội dung dự kiến | Ghi chú |
|---|---|---|
| P1 (validity) | Với mọi proxy và mọi cấu hình nhãn cố định, P(chứng nhận sai) ≤ δ | Hệ quả của Ville's inequality với supermartingale dưới H_t; phải viết rõ điều kiện predictable |
| P2 (bảo thủ) | Gán Z = 1 cho dòng audit dở dang vẫn giữ validity | Đơn điệu của test |
| P3 (tập lồng nhau) | Fixed-sequence trên họ ngưỡng cố định trước cho FWER ≤ δ | Chuẩn (Learn-then-Test style); không nhận là mới |
| P4 (chi phí) | E[cost] = Σ π_g (Z_g τ_g + (1−Z_g) k_g) + c_0 Σ π_g; điều kiện để thứ tự proxy giảm E[τ \| Z=1] | Phần có thể thành đóng góp |
| R1 (giới hạn) | Với ε = 0 và không có giả định thêm, phải kiểm mọi ô của mọi dòng | Lập luận zero-vs-one quen thuộc; trình bày như nhận xét, không phải định lý mới |
| Mục tiêu A* | Tối ưu của quy tắc phân bổ "growth-per-cost" so với Neyman theo chi phí, hoặc cận regret | Chỉ theo đuổi ở bản nâng cấp |

## 8. Thiết kế thực nghiệm

### 8.1 Dữ liệu — public (https://github.com/BigDaMa/raha)

| Dataset (RAHA) | Số dòng | Số cột (header `clean.csv`, VERIFIED) | Ghi chú |
|---|---:|---:|---|
| Hospital | ≈1.000 | 20 | Bảng rộng; nhóm thực thể theo ProviderNumber |
| Flights | ≈2.376 | 7 | Bảng hẹp; nhóm thực thể theo chuyến bay |
| Beers | ≈2.410 | 11 | Mọi dòng có lỗi; sanity check "chứng nhận rỗng" |
| Rayyan | ≈1.000 | 11 | Domain học thuật; detector LLM thường yếu |
| Tax | ≈200.000 | 15 | Kiểm tra quy mô; cần detector rẻ |
| Movies | ≈7.390 | 17 | Bảng rộng |

Số dòng tính bằng `wc -l` trừ header, nên có thể lệch nếu CSV có xuống dòng trong ô. Ground truth mức ô lấy từ diff `dirty.csv` và `clean.csv`.

### 8.2 Detector — proxy tạo tập commit

1. **LLM zero-shot detector:** model mở 7–8B chạy trên GPU (hoặc API rẻ), prompt theo dòng, trả về quyết định clean/error và danh sách ô nghi ngờ.
2. **ZeroED** (ICDE 2025), nếu code công khai chạy được.
3. **Raha** (cần khoảng 20 dòng có nhãn; ghi rõ là bán giám sát).
4. **Vi phạm FD:** khám phá FD xấp xỉ bằng công cụ mở, điểm ô theo số vi phạm.
5. **Outlier/pattern theo cột** kiểu dBoost hoặc IsolationForest.
6. **Proxy ngẫu nhiên** để kiểm validity khi proxy vô dụng.

### 8.3 Baseline chứng nhận

| Mã | Baseline | Mục đích |
|---|---|---|
| B0 | Tin detector, không chứng nhận | Cho thấy rủi ro |
| B1 | Uniform row audit, kiểm hết dòng, cận hypergeometric chính xác | Mốc thống kê cổ điển |
| B2 | B1 + dừng sớm với thứ tự ô ngẫu nhiên | Tách lợi ích của thứ tự proxy |
| B3 | Phân tầng + cost-aware Neyman + Horvitz–Thompson + cận trên | **Baseline quyết định cho C4** |
| B4 | Conformal selection (Jin–Candès) với nhãn calibration mua bằng cùng chi phí ô | Đối thủ "chọn tập có FDR" trực tiếp |
| B5 | PPI / stratified PPI ước lượng FDP của A cố định | Đối thủ suy luận có proxy |
| B6 | DQM species estimator | Minh họa: không có bảo đảm hữu hạn mẫu |
| Oracle | Nhãn đầy đủ | Trần tham chiếu |

### 8.4 Chỉ số
- **Kích thước tập được chứng nhận** |A_t̂| (và tỷ lệ so với |A|) tại ε, δ cho trước.
- **Số ô được kiểm** để đạt chứng chỉ, và đường cong "dòng được chứng nhận theo ngân sách".
- **Tần suất chứng chỉ sai** qua R = 1.000 seed audit. Phải ≤ δ; báo khoảng tin cậy của chính tần suất này.
- FDP thực tế của tập trả về; số lỗi tìm thấy trong audit; thời gian chạy.
- Lưới tham số: ε ∈ {0.01, 0.02, 0.05, 0.10}, δ ∈ {0.05, 0.10}, tỷ lệ c_0/c ∈ {0, 1, 5}.

### 8.5 Protocol
- Tập commit đóng băng từ các run có sẵn. Nhãn ô chỉ được "mở" khi có lệnh inspect.
- Các phương pháp dùng **cùng seed** (paired) và cùng ngân sách ô.
- Ngưỡng t và các bin phân tầng cố định trước khi xem kết quả audit.
- Báo cáo mọi dataset, kể cả nơi không chứng nhận được gì. Không lọc dataset sau khi xem kết quả.

### 8.6 Ablation
Bỏ thứ tự proxy (ngẫu nhiên); bỏ phân tầng; Neyman thay cho growth-per-cost; một ngưỡng thay cho họ lồng nhau; proxy ngẫu nhiên; thay đổi tỷ lệ chi phí; nhóm theo thực thể (Hospital theo ProviderNumber, Flights theo mã chuyến) thay vì theo dòng.

## 9. Điều kiện tiếp tục / dừng (cố định trước)

| Cổng | Kiểm tra | Nếu thất bại |
|---|---|---|
| G1 (Ngày 1) | Nhãn ô từ diff đúng (kiểm tay 50 ô); ≥ 3 detector chạy được và sinh tập commit; ≥ 2 dataset có FDP của tập commit đáng kể | Nếu mọi detector đều đã rất sạch: động lực yếu, chuyển trọng tâm sang chi phí chứng nhận ở ε nhỏ |
| G2 (Ngày 2) | Validity mô phỏng: tần suất sai ≤ δ với mọi proxy, kể cả proxy ngẫu nhiên | Sửa test; không công bố khi chưa qua |
| G3 (Ngày 2–3) | Trên ≥ 2 dataset, thứ tự proxy + dừng sớm giảm rõ số ô so với B1/B2 ở cùng chứng chỉ | Nếu không: định vị bài theo C1+C2+C3+C5 (vẫn đủ cho ACIIDS); bỏ tuyên bố C4 |
| G4 (bản A*) | Growth-per-cost thắng cost-aware Neyman (B3) ở cùng validity | Nếu không: không nộp A* với tuyên bố phân bổ; chuyển trọng tâm sang Ý tưởng 5 hoặc lý thuyết |

## 10. Kế hoạch 6 ngày cho ACIIDS (26/10 → 01/11/2026 18:59 UTC+7)

| Ngày | Việc | Đầu ra |
|---|---|---|
| CN 26/10 | Tải RAHA, tạo nhãn ô từ diff. Chạy 3–4 detector công khai, tạo tập commit. Cài B1, B2. Chọn dạng test (betting WoR hoặc hypergeometric) | Bảng nhãn ô, bảng FDP mở đầu; G1 |
| T2 27/10 | Cài tầng 2 theo proxy, tập lồng nhau, B3–B5. Mô phỏng validity R = 1.000 | G2, G3 sơ bộ |
| T3 28/10 | Chạy đủ 6 dataset × detector. Viết các mệnh đề P1–P4 | Bảng chính, hình ngân sách |
| T4 29/10 | Ablation, nhóm thực thể, Tax (quy mô). Vẽ hình | Bảng ablation |
| T5 30/10 | Viết bài LNCS 12–15 trang (template Springer LNCS) | Bản thảo đầy đủ |
| T6 31/10 → 01/11 sáng | Tự review, kiểm số liệu, ẩn danh, nộp EasyChair trước **01/11 18:59 giờ Việt Nam** | Submission |

Nguyên tắc: nếu đến tối 29/10 chưa qua G2, **không nộp** một bài có bảo đảm sai. Chuyển sang venue sau. Phân công 2 người (thống kê + kỹ sư dữ liệu): xem `01_RANKING_AND_TEAM_PLAN_VI.md`.

## 11. Lộ trình nâng cấp lên Q1 / A*

1. **Lý thuyết phân bổ:** tối ưu hoặc cận regret cho quy tắc growth-per-cost với chi phí bất đối xứng (C4). Đây là phần quyết định cho SIGMOD/VLDB.
2. **Tổng quát hóa nhóm:** dòng → thực thể → truy vấn phủ định ngữ nghĩa (Ý tưởng 5). Một khung, nhiều thể hiện.
3. **Nghiên cứu người dùng thật:** 2–3 annotator đo thời gian kiểm ô và dòng trên một tập con Hospital/Tax, để thay giả định chi phí bằng số đo.
4. **Auditor có nhiễu:** chứng chỉ tương đối với auditor có tỷ lệ lỗi đã ước lượng.
5. **Thêm detector:** ZeroED, Raha/Baran, CDC. Thêm dataset REIN.
6. **Artifact hệ thống:** hook vào pipeline (ví dụ bước kiểm định kiểu Great Expectations), mã nguồn mở, có cost accounting.
7. **Bản journal:** thêm tối thiểu phần lý thuyết, nghiên cứu người dùng và tổng quát hóa. Kiểm tra chính sách mở rộng bài hội nghị của journal đích.

## 12. Phản biện dự kiến và cách trả lời

| Phản biện | Trả lời chuẩn bị sẵn |
|---|---|
| "Chỉ là stratified sampling / RLA áp vào data cleaning" | Trích dẫn RLA là nền tảng. Đóng góp được đo **so với** cost-aware Neyman và conformal selection ở cùng chi phí. Phần mới gồm cấu trúc ô-trong-dòng với dừng sớm bất đối xứng, tập lồng nhau, và bằng chứng failure trên detector thật |
| "Nhãn RAHA không hoàn hảo" | Chứng chỉ được phát biểu tương đối với nhãn tham chiếu; nêu rõ trong phần giới hạn |
| "Sao không gán nhãn rồi train detector có giám sát?" | Chứng nhận trực giao với detector: áp dụng cho mọi detector, kể cả detector có giám sát |
| "Prevalence cao làm commit-clean vô nghĩa" | Đó chính là điều chứng nhận phơi bày. Với Beers, hệ thống trả về tập rỗng là đúng |
| "Chi phí audit là mô phỏng" | Phân tích độ nhạy theo c_0/c. Bản A* có đo thời gian người thật |
| "Detector yếu thì chứng nhận vô nghĩa" | Validity không phụ thuộc detector. Detector yếu chỉ làm tập được chứng nhận nhỏ đi, và bài báo cáo điều đó như một kết quả |

## 13. Rủi ro và giảm thiểu

| Rủi ro | Mức | Giảm thiểu |
|---|---|---|
| Thời gian 6 ngày | Cao | Phạm vi tối thiểu: B1–B5, 4 dataset nhỏ, 3 detector. Tax/Movies chỉ là phụ |
| Sai sót thống kê ở test phân tầng tuần tự | Trung bình | Phương án dự phòng: hypergeometric cỡ mẫu cố định, chính xác và dễ kiểm. Mô phỏng validity bắt buộc |
| Lợi ích C4 nhỏ | Trung bình | Cổng G3/G4. Bài ACIIDS vẫn đứng được nhờ C1–C3, C5 |
| Chi phí chạy detector LLM trên Tax (200k dòng) | Thấp–TB | Lấy mẫu con; dùng detector rẻ cho Tax |
| Quy tắc ẩn danh ACIIDS chưa rõ | Thấp | Metadata nói double-blind: ẩn tên, tự trích dẫn ở ngôi thứ ba |

## 14. Khung bài báo (LNCS, mục tiêu khoảng 14 trang)

1. Introduction (1,5 tr): ví dụ Hospital; bảng FDP của các detector công khai; ba đóng góp.
2. Related work (1,5 tr): error detection không nhãn; data quality estimation (DQM, SampleClean); conformal/PPI/RLA.
3. Problem formulation (1 tr).
4. CertiClean (3 tr): hai tầng, test, tập lồng nhau, phân bổ.
5. Guarantees (1 tr): P1–P4, R1.
6. Experiments (4 tr): setup, validity, hiệu quả ngân sách, ablation, quy mô.
7. Discussion & limitations (0,5 tr).
8. Conclusion; References (1,5 tr).

**Abstract nháp. Chỉ điền số sau khi chạy; mọi [·] là placeholder:**

> Label-free error detectors built on large language models increasingly decide which rows of a table are clean enough to pass downstream. We show that such "clean" decisions can be unreliable in ways that row-level accuracy metrics hide: across [k] public benchmarks and [m] detectors, the fraction of committed-clean rows that actually contain errors ranges from [x]% to [y]%. We introduce CertiClean, a detector-agnostic certification layer that, given a small human audit budget, returns the largest subset of committed rows whose false-clean proportion is at most ε with probability at least 1−δ. CertiClean exploits a cost asymmetry, namely that refuting a clean row needs one erroneous cell while confirming it needs all cells, through proxy-ordered two-stage audits and anytime-valid tests whose validity does not depend on proxy quality. On [six] datasets, CertiClean certifies [·]× more rows than uniform auditing at the same inspection budget while keeping the empirical certificate failure rate below δ.

## 15. Tài liệu tham khảo cốt lõi (trạng thái xác minh)

- Chung, Krishnan, Kraska. *A Data Quality Metric (DQM): How to Estimate the Number of Undetected Errors in Data Sets.* PVLDB 10(11), 2017. https://arxiv.org/abs/1611.04878 — VERIFIED
- Jäger, Biessmann. *From Data Imputation to Data Cleaning — Automated Cleaning of Tabular Data Improves Downstream Predictive Performance.* AISTATS 2024. https://proceedings.mlr.press/v238/jager24a — VERIFIED
- Ye, Lyu, Tao. *Allocating Human Oversight in AI-Enabled Analytics.* arXiv 2604.12497, 2026. https://arxiv.org/abs/2604.12497 — VERIFIED (abstract)
- *Selection from Hierarchical Data with Conformal e-values.* arXiv 2501.02514 — search-level
- *Beyond Fixed False Discovery Rates: Post-Hoc Conformal Selection with E-Variables.* arXiv 2604.11305 — search-level
- Jin, Candès. *Selection by Prediction with Conformal p-values.* JMLR 2023 — kiến thức nền; kiểm tra metadata
- Waudby-Smith, Ramdas. Betting confidence sequences; confidence sequences cho lấy mẫu không hoàn lại — kiến thức nền; kiểm tra metadata
- Stark và cs. SHANGRLA, ALPHA; Spertus & Stark, "Sweeter than SUITE" — kiến thức nền; kiểm tra metadata
- Angelopoulos và cs. Prediction-Powered Inference (Science 2023); Learn-then-Test — kiến thức nền; kiểm tra metadata
- Wang và cs. SampleClean, SIGMOD 2014 — kiến thức nền; kiểm tra metadata
- Lee và cs. *Evergreen.* arXiv 2604.26180 — handoff
- Mahdavi và cs. Raha (SIGMOD 2019), Baran (PVLDB 2020); dữ liệu public: https://github.com/BigDaMa/raha
- ZeroED, ICDE 2025: https://arxiv.org/abs/2504.05345 — VERIFIED
