# Brainstorm Nghiên cứu — Đánh giá & Định hướng lại Idea 3 cho ACIIDS 2027

Cập nhật: 2026-10-29.
Trạng thái: Đánh giá lại toàn diện từ bằng chứng thực tế; không mặc định giữ nguyên framing, novelty hay phương pháp cũ.

---

## 1. Vấn đề thực tế và nhu cầu người dùng (Real-World Need)

Trong phân tích dữ liệu bảng thực tế (y tế, tài chính, vận tải, quản trị doanh nghiệp), dữ liệu thu thập thường xuyên bị nhiễm lỗi ở **cấp độ từng ô (cell-level errors)**: lỗi nhập liệu (typo), sai lệch đơn vị đo, swap cột dữ liệu, lỗi trôi cảm biến (sensor drift), hoặc sai định dạng. 

Người dùng thực tế (data practitioners, domain analysts) đối mặt với hai khó khăn cốt lõi:
1. **Thiếu nhãn lỗi khi triển khai (Zero-shot / Unsupervised deployment)**: Dán nhãn thủ công từng ô bị lỗi trên các bảng dữ liệu hàng trăm nghìn dòng là bất khả thi về mặt chi phí và thời gian.
2. **Nhu cầu định vị chính xác vị trí ô lỗi (Cell-level localization)**: Các phương pháp phát hiện dị biệt truyền thống thường chỉ chấm điểm cả hàng (Row anomaly detection). Nếu một hàng gồm 50 cột bị gán nhãn là "bất thường", người dùng vẫn không biết can thiệp, kiểm tra hay sửa chữa vào ô nào.

Gần đây, các mô hình Tabular Foundation Model (TFM: tiêu biểu là TabPFN, TabICL) mở ra tiềm năng lớn cho in-context learning trên dữ liệu bảng mà không cần huấn luyện lại trên tập đích. Tuy nhiên, khi đưa bảng dữ liệu bẩn vào làm in-context prompt, **chính các ô bẩn trong context sẽ gây nhiễm bẩn suy luận (Self-Contamination)**. Nếu các lỗi xuất hiện theo cấu trúc (lỗi theo nguồn, theo cụm, batch sensor), context bẩn sẽ "bình thường hóa" lỗi (Context Normalization), khiến mô hình ICL gán likelihood cao cho ô sai, làm detector mù trước lỗi hệ thống.

---

## 2. Định nghĩa chính xác Task & Ranh giới thông tin (Task & Boundaries)

- **Task**: Unsupervised / Training-free Cell-Level Error Detection (Cell-ED) trên dữ liệu bảng dị thể (Mixed-Type Tabular Data).
- **Đơn vị dự đoán**: Từng ô $x_{i,j}$ (hàng $i$, cột $j$).
- **Đầu vào**: Bảng bẩn $\tilde{X} \in \mathbb{R}^{N \times D}$ gồm $D$ cột dị thể (numerical và categorical). Không có nhãn lỗi $Y \in \{0, 1\}^{N \times D}$ trong pha suy luận.
- **Đầu ra**: Ma trận điểm số bất thường $S \in \mathbb{R}^{N \times D}$, trong đó $S_{i,j} \in \mathbb{R}$ càng cao thì độ nghi ngờ ô $(i,j)$ bị lỗi càng lớn; hoặc nhãn nhị phân $\hat{Y}_{i,j} \in \{0, 1\}$ tại một ngân sách kiểm toán (audit budget) $k$.
- **Thước đo đánh giá (Metrics)**: Cell-level AUPRC (Area Under Precision-Recall Curve), Precision@k, Recall@k, F1@budget $k$. Báo cáo tách bạch cho cột số (numerical) và cột phân loại (categorical).
- **Ranh giới thông tin & Phòng chống rò rỉ (Information Boundaries & Leakage Control)**:
  - *Leave-Row-Out / Cross-Fitting*: Khi tính điểm cho ô $(i,j)$, toàn bộ hàng $i$ (hoặc entity group chứa hàng $i$) KHÔNG được xuất hiện trong tập context. Ô $(i,j)$ tuyệt đối không được tự làm context cho chính nó.
  - *Target-Feature Dropping*: Cột mục tiêu $j$ không được làm feature đầu vào trong prompt dự đoán cho ô $(i,j)$ (mỗi cột $j$ đóng vai trò là nhãn mục tiêu trong một bài toán học có giám sát giả lập $X_{-j} \to X_j$).
  - *Clean Value Insulation*: Giá trị sạch và nhãn lỗi thật chỉ được phép đọc bởi script đánh giá (evaluation harness); detector code tuyệt đối không được truy cập.
- **Tách bạch nhiệm vụ (Task Separation)**:
  - *Cell Error Detection $\neq$ Row Anomaly Detection*: Các công trình như TACTIC, ZEN, TaskBridge, FoMo-0D chỉ dự đoán điểm số 1 chiều cho hàng $s_i \in \mathbb{R}$. Việc gán lặp điểm số của hàng cho mọi ô trong hàng là phi lý và làm sai lệch benchmark.
  - *Cell Error Detection $\neq$ Supervised Label Attribution*: TICDA giải quyết bài toán label-error detection cho 1 cột target định sẵn trong supervised learning; Cell-ED phải quét toàn bộ $N \times D$ ô của bảng dữ liệu không nhãn.
  - *Cell Error Detection $\neq$ Data Imputation*: CDC dùng imputer để thay thế missing value, nhưng giá trị bị lỗi trong Cell-ED đang có mặt và tự gây méo phân phối quan sát.

---

## 3. Các hướng nghiên cứu khả thi (3 Candidate Directions)

### Hướng 1 (Khuyến nghị): Contamination-Resilient In-Context Likelihood for Cell Error Detection (CRIC-ED)
- **Ý tưởng cốt lõi**: Sử dụng TFM pre-trained (TabPFN) ở chế độ conditional feature prediction để gán điểm bất thường dựa trên Negative Log-Likelihood (NLL). Giải quyết hiện tượng self-contamination bằng cơ chế Context Intervention & Influence-Aware Context Selection.
- **Cơ chế**:
  1. Xây dựng $D$ bài toán conditional prediction: Với mỗi cột $j$, coi $X_j$ là target và $X_{-j}$ là features.
  2. Đo lường NLL của giá trị quan sát dưới phân phối dự báo của TFM.
  3. Áp dụng Context Intervention (so sánh likelihood của cùng một ô query dưới các tập context ngẫu nhiên vs kNN vs stratified) để phát hiện khi nào context bị chi phối bởi các cụm lỗi có cấu trúc.
  4. Trimming có kiểm soát: Loại bỏ các mẫu context có độ ảnh hưởng bất thường mà vẫn bảo toàn các mẫu hiếm hợp lệ (rare-valid control).
- **Đóng góp dự kiến**: Phân tích cơ chế đầu tiên về tác động của self-contamination cấp ô lên TFM conditional likelihood và đề xuất giải pháp pruning/selection bảo vệ độ nhạy phát hiện lỗi.

### Hướng 2 (Dự phòng 1): Context-Sensitivity & Abstention for Tabular Cell Error Detection (CS-ED)
- **Ý tưởng cốt lõi**: Nhắm vào điểm yếu lớn nhất của các mô hình phát hiện dị biệt: **Báo động giả trên các nhóm thiểu số hiếm nhưng hợp lệ (False alarms on rare-valid subgroups)**.
- **Cơ chế**:
  1. Thay vì chỉ xuất ra 1 điểm số duy nhất từ 1 tập context cố định, lấy mẫu nhiều tập context hợp lệ (multi-context resampling) để đo độ biến thiên điểm số (Context Sensitivity / Prediction Variance).
  2. Tách biệt Epistemic Uncertainty (độ không chắc chắn do thiếu dữ liệu tương đồng trong context) khỏi Aleatoric Corruption (lỗi sai thực sự).
  3. Kích hoạt cơ chế **Selective Abstention** (từ chối phán đoán): Khi detector không đủ bằng chứng để phân biệt ô hiếm hợp lệ với ô lỗi, hệ thống trả về cờ "Abstain" thay vì cảnh báo sai, giúp tối ưu hóa Precision-Coverage curve cho người dùng.
- **Đóng góp dự kiến**: Khung phát hiện lỗi có khả năng tự biết điểm mù và từ chối phán đoán, giảm thiểu chi phí kiểm toán oan cho các mẫu hiếm.

### Hướng 3 (Dự phòng 2 - Không dùng TFM Backbone): Dual-View Coordinate-Wise Deviance & Semantic Reasoning (Dual-ED)
- **Ý tưởng cốt lõi**: Hoàn toàn độc lập với TFM backbone (loại bỏ phụ thuộc TabPFN/TabICL, không bị giới hạn bởi context window hay license/compute).
- **Cơ chế**:
  1. *Numerical View*: Sử dụng robust coordinate-wise estimators mở rộng từ DDC (Detecting Deviating Data Cells) và Cellwise MCD, tính toán standardized deviation có tính đến tương quan chéo mạnh giữa các biến số.
  2. *Categorical/Text View*: Áp dụng association rule verification hoặc prompt LLM zero-shot cục bộ để kiểm tra tính nhất quán ngữ nghĩa giữa các thuộc tính định danh/chuỗi.
  3. Kết hợp hai góc nhìn thông qua quantile calibration trên phân phối quan sát.
- **Đóng góp dự kiến**: Phương pháp hybrid nhanh, mở rộng được cho bảng dữ liệu lớn bất kỳ, không bị giới hạn bộ nhớ GPU hay rào cản checkpoint.

---

## 4. Related Work / SOTA gần nhất cho từng hướng (Verified Primary Sources)

| Công trình | Năm / Nguồn | Nhiệm vụ chính | Kết quả & Giới hạn chính | Liên hệ với Idea 3 |
| :--- | :--- | :--- | :--- | :--- |
| **CDC** (Jäger et al.) | AISTATS 2024 | Cell error detection / Imputation | Dùng imputer + conformal calibration. Đòi hỏi clean calibration set và assumption IID; không xử lý được self-contamination khi toàn bộ bảng bị bẩn. | Baseline gần nhất về cell-level task. Thay imputer bằng TFM thuần túy KHÔNG PHẢI là novelty đủ mạnh. |
| **TabPFN v2 / Nature** (Hollmann et al.) | Nature 2025 | Tabular Foundation Model / Density | Đã có sẵn năng lực density estimation và anomaly scoring trong extension. | Backbone tiềm năng. Không thể tuyên bố "lần đầu dùng TFM cho anomaly". |
| **uTabPFN Extension** (PriorLabs) | Code 2025-2026 | Unsupervised feature scoring | Cung cấp hàm conditional likelihood, nhưng chủ yếu cho row anomaly / imputation; chưa tối ưu cho cell-level error localization dưới context bẩn. | Implementation baseline trực tiếp cần audit và đo đạc. |
| **TACTIC** (Preprint) | 2026-03 | Row anomaly detection | Nghiên cứu sự mất ổn định của uTabPFN khi context bị bẩn, nhưng CHỈ ĐO ROW-LEVEL AUROC. | Chứng minh hiện tượng bẩn context ở cấp hàng; ta mở rộng nghiên cứu sang cấp ô (cell-level). |
| **ZEN / FOCUS** (Preprint) | 2026-10 | Row anomaly detection | ZEN dùng frozen embeddings + kNN scoring; FOCUS adapt weights. Dùng leave-one-fold-out embeddings. | Cho thấy cross-fitting hay nearest neighbor thuần túy không mới; delta phải nằm ở cell localization. |
| **TaskBridge** (Preprint) | 2026-09 | Row anomaly detection | Xây dựng virtual ICL tasks quanh TFM cho row anomaly. | Minh chứng row anomaly đang rất nóng, nhưng cell error detection vẫn là địa hạt riêng cần khai phá. |
| **TICDA** (Preprint) | 2026-10 | Supervised label-error detection | Dùng surrogate influence trên embeddings để lọc nhãn sai trong classification có giám sát. | Liên quan đến context pruning, nhưng TICDA chỉ làm cho 1 cột nhãn target, không làm cho mọi ô bảng dị thể. |
| **ZeroED / ForestED** | ICDE 2025 / arXiv 2025-2026 | Cell error detection qua LLM | ZeroED dùng LLM reasoning sinh pseudo-labels; ForestED dùng ensembling LLM decision trees. | LLM-based cell-ED baselines. Token cost cao, suy luận chậm, cần kiểm chứng trên cùng universe. |
| **DDC / Cellwise MCD** (Rousseeuw et al.) | Technometrics 2018 / JASA 2023 | Robust cellwise numeric deviance | Ước lượng độ lệch từng ô dựa trên ma trận tương quan robust. | Baseline cổ điển vững chắc cho cột số, giúp kiểm chứng xem TFM có thực sự mang lại lợi ích hơn thống kê robust không. |

---

## 5. Bảng so sánh giữa các hướng (Comparison Matrix)

| Tiêu chí | Hướng 1: CRIC-ED (Khuyến nghị) | Hướng 2: CS-ED (Dự phòng 1) | Hướng 3: Dual-ED (Dự phòng 2) |
| :--- | :--- | :--- | :--- |
| **Novelty còn lại** | **Khá cao**: Phân tích cơ chế self-contamination và đề xuất mitigation đầu tiên ở cấp ô cho TFM. | **Cao**: Đóng góp bài toán abstention / false alarm mitigation trên rare subgroups. | **Trung bình**: Kết hợp các thành phần sẵn có (robust stats + LLM reasoning). |
| **Mức độ trùng lặp prior work** | Rủi ro overlap với TACTIC (row-level) và TICDA (label-level) nếu không làm rõ bài toán cấp ô. | Thấp: Ít nghiên cứu xét riêng rare-valid cell abstention trên tabular data. | Rủi ro bị coi là incremental combination của DDC và ZeroED. |
| **Dữ liệu cần có** | Benchmark chuẩn (RAHA: Hospital, Beers, Flights, Rayyan). | Benchmark RAHA kèm nhãn subgroup / tần suất để kiểm tra rare-valid. | Benchmark RAHA mixed-type. |
| **Compute & Tài nguyên** | Trung bình: Cần GPU/CPU chạy TabPFN forward passes ($D$ bài toán ICL cho mỗi hàng). | Cao hơn: Cần multiple context resampling (3–5x forward passes). | Thấp: Cột số chạy CPU cực nhanh; cột text chỉ tốn prompt LLM khi cần. |
| **Rủi ro kỹ thuật** | Giới hạn context length của TabPFN; hỗ trợ phân phối số liên tục (regression distribution API). | Không tách được epistemic uncertainty của rare-valid khỏi error cells. | Chất lượng phụ thuộc vào ngưỡng kết hợp quantile. |
| **Khả năng hoàn thành cho ACIIDS 2027** | **Khả thi**: Có thể dựng protocol sạch, chạy pilot CPU/GPU nhỏ và viết bài hoàn chỉnh. | Khá thách thức do cần nhiều thí nghiệm ablation về uncertainty. | **Rất khả thi**: Không phụ thuộc vào TFM weights hay GPU lớn. |
| **Độ phù hợp ACIIDS 2027** | **Rất cao**: Phù hợp hoàn hảo với track DADIT (Data Analysis, Data Quality, Intelligent Information). | Cao: Phù hợp track ADMTA hoặc AI Methodology. | Cao: Phù hợp Intelligent Database Systems. |

---

## 6. Framing Khuyến nghị & Framing Dự phòng

### Framing Khuyến nghị (Primary Framing)
- **Tên đề xuất**: **CRIC-ED: Contamination-Resilient In-Context Likelihood for Cell-Level Error Detection in Tabular Foundation Models**
- **Thông điệp cốt lõi**:
  "Khi sử dụng Tabular Foundation Models để phát hiện lỗi cấp ô mà không cần huấn luyện, chính các giá trị bẩn trong ngữ cảnh (self-contamination) có thể hợp thức hóa lỗi và làm suy giảm độ chính xác của mô hình. Bài báo phân tích hiện tượng này và đề xuất CRIC-ED: một cơ chế tính likelihood có kiểm soát ranh giới thông tin (cross-fitting, target dropping) kết hợp với context intervention và influence-aware pruning để phát hiện lỗi cấp ô chính xác trên dữ liệu bảng dị thể."

### Framing Dự phòng 1 (Fallback Framing A — Nếu context trimming không tạo ra gain rõ rệt)
- **Tên đề xuất**: **CS-ED: Selective In-Context Error Detection: Knowing When to Abstain on Rare-Valid Tabular Cells**
- **Thông điệp cốt lõi**: Chuyển trọng tâm từ việc "tối ưu điểm số tuyệt đối" sang việc "đo lường độ bất định do ngữ cảnh và từ chối phán đoán để triệt tiêu báo động giả trên các mẫu hiếm hợp lệ".

### Framing Dự phòng 2 (Fallback Framing B — Nếu TabPFN backbone gặp sự cố kỹ thuật / phần cứng)
- **Tên đề xuất**: **Dual-ED: Coordinate-Wise Robust Deviance Meets In-Context Semantic Verification for Tabular Error Localization**
- **Thông điệp cốt lõi**: Không dựa vào mô hình TFM cồng kềnh; phát triển hệ thống phát hiện lỗi cấp ô hybrid kết hợp thống kê đa biến robust cho cột số và xác thực ngữ nghĩa zero-shot cho cột văn bản.

---

## 7. Câu hỏi nghiên cứu (RQs), Giả thuyết, Baselines & Protocol

### Research Questions & Hypotheses
- **RQ1 (Hiệu năng tổng thể)**: Conditional TFM Likelihood (CRIC-ED) có đạt AUPRC cấp ô vượt trội hơn các mô hình baseline cổ điển (DDC, Isolation Forest per column) và baseline hiện đại (CDC, uTabPFN) trên các benchmark dữ liệu thực tế (RAHA datasets) ở cùng mức tài nguyên không?
  - *Hypothesis*: Có, nhờ prior phân phối đa biến được học trước từ hàng triệu bảng dữ liệu tổng hợp.
- **RQ2 (Tác động của cấu trúc lỗi context)**: Cùng một tỷ lệ lỗi trong context, lỗi xuất hiện có cấu trúc (theo nhóm, batch) có làm giảm độ nhạy phát hiện ô lỗi của TFM nhiều hơn đáng kể so với lỗi phân tán ngẫu nhiên không?
  - *Hypothesis*: Có, hiện tượng Context Normalization xảy ra mạnh nhất khi lỗi lặp lại có cấu trúc trong context.
- **RQ3 (Cơ chế Context Trimming / Intervention)**: Việc can thiệp và tỉa bớt context (Context Trimming) có thực sự cải thiện khả năng phát hiện lỗi mà không vô tình xóa bỏ các nhóm mẫu hiếm nhưng hợp lệ (rare-valid subgroups) không?
  - *Hypothesis*: Trimming dựa trên negative influence cải thiện AUPRC trên dirty data, nhưng cần có cơ chế kiểm soát phương sai để bảo toàn rare-valid patterns.

### Hệ thống Baselines (Bắt buộc so sánh công bằng)
1. **Classical Numeric Baseline**: DDC (Detecting Deviating Data Cells) trên các cột số.
2. **Standard Machine Learning Baseline**: Column-wise Isolation Forest và MissForest Imputer Residuals.
3. **Task-Specific Modern Baseline**: CDC (From Data Imputation to Data Cleaning, AISTATS 2024).
4. **Foundation Model Baseline**: Unsupervised TabPFN (uTabPFN) nguyên bản với random context selection.
5. **(Nếu đủ compute/API)**: ZeroED hoặc ForestED trên cùng tập dữ liệu con.

### Ablation Studies bắt buộc
- *Ablation 1*: Không trimming vs. Random removal (cùng kích thước context) vs. Influence trimming.
- *Ablation 2*: Context selection: Random vs. kNN vs. Stratified.
- *Ablation 3*: Context size scaling: $k \in \{32, 64, 128, 256, 512\}$.
- *Diagnostic arm*: Leakage check (so sánh trường hợp vô tình đưa row mục tiêu vào context để định lượng mức độ phồng điểm số do rò rỉ dữ liệu).

### Tiêu chí dừng (Stopping / Pivot Criteria)
- Nếu sau thí nghiệm pilot tối thiểu, CRIC-ED không vượt qua được baseline đơn giản uTabPFN hoặc CDC trên tập dữ liệu sạch lỗi rò rỉ: **DỪNG và kích hoạt Framing Dự phòng 1 (Abstention) hoặc Framing Dự phòng 2 (Dual-ED)**.
- Tuyệt đối không tinh chỉnh ngưỡng hay loại bỏ dataset bất lợi một cách có chủ đích để tạo kết quả dương tính giả.

---

## 8. Những claim chưa đủ bằng chứng & Thí nghiệm tối thiểu (Minimum Viable Pilot)

### Danh sách Claim cần bằng chứng thực nghiệm (Claims Ledger)
1. *Claim 1*: "TabFM đạt kết quả SOTA trên bài toán cell error detection." → **TRẠNG THÁI: PENDING**. Chưa có bất kỳ lượt chạy thực nghiệm nào trong repository.
2. *Claim 2*: "Context Trimming cải thiện độ chính xác phát hiện ô lỗi." → **TRẠNG THÁI: HYPOTHESIS**. Chưa được chứng minh.
3. *Claim 3*: "Context bẩn có cấu trúc làm mô hình bình thường hóa lỗi." → **TRẠNG THÁI: HYPOTHESIS**. Cần kiểm chứng qua thí nghiệm can thiệp có đối chứng.

### Kế hoạch Pilot tối thiểu (Minimum Viable Pilot - Stage G0/G1)
- **Tập dữ liệu**: Lấy 1 subset chuẩn của benchmark RAHA (ví dụ: Hospital hoặc Beers, quy mô $\le 500$ dòng, 10-15 cột).
- **Mục tiêu kỹ thuật**:
  1. Kiểm tra interface tính phân phối xác suất đầu ra của TabPFN (thực hiện trên CPU local smoke test, không tốn phí).
  2. Đo lường AUPRC cấp ô của conditional NLL thô (raw uTabPFN) so với DDC trên cột số và frequency-based trên cột phân loại.
  3. Đo runtime thực tế trên mỗi ô để ước tính chi phí cho toàn bộ benchmark.
