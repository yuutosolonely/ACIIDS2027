# Claim → Evidence Ledger — ACIIDS 2027

Cập nhật: 2026-10-29.
Nguyên tắc: Mọi khẳng định nghiên cứu khoa học phải truy nguyên trực tiếp về Run ID, artifact thực nghiệm, source revision và config cụ thể. Phân định rạch ròi giữa Đã đo lường (Measured), Nguồn công bố báo cáo (Source-reported), Giả thuyết (Hypothesis), Đề xuất (Proposal) và Đang chờ thực hiện (Pending).

---

## 1. Trạng thái các Claim của Đề tài (Idea 3 / CRIC-ED)

| Claim ID | Nội dung khẳng định | Trạng thái hiện tại | Loại bằng chứng / Nguồn chứng minh | Ghi chú & Rào cản |
| :--- | :--- | :--- | :--- | :--- |
| **CLM-01** | CRIC-ED đạt hiệu năng AUPRC cấp ô vượt trội CDC và classical baselines trên bảng dữ liệu dị thể. | **PENDING** (Chưa đo) | Chưa có run nào được thực hiện trong repository. | Tuyệt đối không đưa số liệu giả định vào abstract hay kết luận bài báo. |
| **CLM-02** | Context Trimming cải thiện độ chính xác phát hiện ô lỗi so với việc giữ nguyên context bị bẩn. | **HYPOTHESIS** (Giả thuyết) | Cần kiểm chứng qua pilot có đối chứng matched-random-removal. | Nguy cơ vô tình loại bỏ các mẫu hiếm hợp lệ (rare-valid) cần được kiểm tra cụ thể. |
| **CLM-03** | Lỗi có cấu trúc (clustered/batch corruption) trong context làm suy giảm conditional TFM score mạnh hơn lỗi ngẫu nhiên (hiện tượng Context Normalization). | **HYPOTHESIS** (Giả thuyết) | Cần kiểm chứng qua thí nghiệm can thiệp ghép cặp (paired context intervention). | TACTIC đã quan sát hiện tượng ở cấp hàng (row); ta cần chứng minh độc lập ở cấp ô (cell). |
| **CLM-04** | "Conditional TFM scoring" hoặc "Cross-fitting" là đóng góp hoàn toàn mới. | **NOT ESTABLISHED** (Bác bỏ / Trùng lặp) | Prior work đã sử dụng: uTabPFN (code), ZEN (arXiv 2026-10), TACTIC (arXiv 2026-03). | Đóng góp nghiên cứu phải tập trung vào: **Cell-level error localization under heterogeneous self-contamination**, không tuyên bố mới về cross-fitting. |
| **CLM-05** | TFM đào tạo sẵn cung cấp prior phân phối liên tục và phân loại vượt trội imputer thông thường. | **HYPOTHESIS** (Giả thuyết) | Cần đo lường log-likelihood calibration trên các tập dữ liệu chuẩn. | Phụ thuộc vào chất lượng checkpoint TabPFN v2 trên dữ liệu thực. |

---

## 2. Bằng chứng Tài liệu & Nguồn gốc (Literature Evidence)
- Toàn bộ metadata và quan sát bài báo liên quan lưu tại `docs/literature/papers.json` và `docs/related-work.md`.
- Các trích dẫn đã được kiểm tra nguồn gốc chính (arXiv metadata, proceedings AISTATS, Nature, Technometrics, ICDE, JASA).
- Ghi nhận trạng thái chưa reproduce mã nguồn của các paper đối thủ; chỉ dẫn số liệu từ bài báo của họ ở chế độ "Source-reported", không coi là số liệu đã tự kiểm chứng.

---

## 3. Quy tắc cập nhật khi có kết quả thực nghiệm
Khi thực hiện confirmatory runs trong tương lai:
1. Ghi rõ Run ID, timestamp, hardware/VRAM sử dụng, git commit SHA.
2. Lưu trữ đầy đủ artifact kết quả (file JSON/CSV kết quả raw) trong `experiments/runs/<run_id>/`.
3. Báo cáo macro-average và per-dataset metric, confidence intervals (cluster bootstrap theo entity), và tỷ lệ ô không dự đoán được (unsupported coverage denominator).
