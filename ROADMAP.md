# Kế Hoạch Nghiên Cứu (Roadmap) — ACIIDS 2027

Cập nhật từ trạng thái thực tế: **29/10/2026**.
Thời hạn nộp bài chính thức ACIIDS 2027: **31/10/2026, 23:59 AoE** (tương đương **01/11/2026, 18:59 ICT / Giờ Việt Nam**).

---

## Các Giai đoạn Thực hiện (Checkpoints)

1. **Giai đoạn Hiện tại (Hoàn tất Chuẩn hóa & Rà soát Đề xuất)**:
   - Chuẩn hóa 100% workspace độc lập cho ACIIDS 2027; dọn sạch toàn bộ ngữ cảnh cũ.
   - Xác minh chính sách ACIIDS 2027 (Springer LNCS/LNAI, quy định AI, độ dài 12–15 trang).
   - Đánh giá lại Idea 3 dưới dạng **Đề xuất nghiên cứu (Proposal)**; mở rộng 3 hướng khả thi:
     - *Hướng 1 (Khuyến nghị)*: CRIC-ED (Cell-level error detection chống self-contamination).
     - *Hướng 2 (Dự phòng 1)*: CS-ED (Context sensitivity & selective abstention trên rare-valid cells).
     - *Hướng 3 (Dự phòng 2)*: Dual-ED (Coordinate-wise robust deviance + zero-shot semantic, không phụ thuộc TFM).

2. **Checkpoint CP0 (Giải quyết Trùng lặp & Ranh giới Khoa học)**:
   - Rà soát ranh giới nhiệm vụ: Cell-ED khác biệt với Row Anomaly Detection (TACTIC, ZEN, TaskBridge), Label Error Detection (TICDA) và Data Imputation (CDC).
   - Xác lập hệ thống Research Questions (RQ1–RQ3) có thể bác bỏ và protocol chống rò rỉ (cross-fitting).

3. **Checkpoint CP1 / Cổng G0 (Kiểm thử Kỹ thuật Cục bộ — Zero-Cost CPU Smoke)**:
   - Kiểm tra API phân phối đầu ra của TabPFN trên môi trường CPU cục bộ với dữ liệu mẫu nhỏ.
   - Kiểm tra khả năng xử lý cột số và cột phân loại mà không cần GPU trả phí hay tải weights cồng kềnh.

4. **Checkpoint CP2 / Cổng G1 (Chạy Thí nghiệm Pilot & Quyết định Chốt Đề tài)**:
   - Chạy pilot trên subset nhỏ (200 hàng) của benchmark RAHA (Hospital/Beers).
   - So sánh trực tiếp giữa conditional TFM likelihood với DDC (thống kê robust) và frequency baseline.
   - **Quyết định chốt**: Nếu pilot cho thấy hiệu quả rõ ràng và khả thi về mặt tài nguyên $\to$ chính thức chốt Hướng 1; nếu gặp vấn đề về minority false alarm $\to$ chuyển Hướng 2; nếu gặp rào cản tài nguyên/checkpoint $\to$ chuyển Hướng 3.

5. **Checkpoint CP3 / Cổng G2 (Thực nghiệm Xác nhận & Ablation có Đối chứng)**:
   - Chạy confirmatory runs có đối chứng (No trimming vs Random removal vs Influence trimming).
   - Đo lường và ghi lại đầy đủ artifacts trong `experiments/runs/`, chi phí tính toán, CI và tỷ lệ coverage.

6. **Checkpoint CP4 (Soạn thảo Bản thảo Springer LNAI & Đảm bảo Liêm chính)**:
   - Soạn thảo manuscript 12–15 trang theo mẫu Springer LaTeX llncs.
   - Kiểm tra tính nhất quán giữa số liệu trong bài với `docs/CLAIM_EVIDENCE.md`.
   - Bổ sung tuyên bố minh bạch về AI (AI Disclosure) theo chuẩn Springer Nature.
