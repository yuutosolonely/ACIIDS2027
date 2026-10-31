# Decision brief cho tác giả — 2026-10-30

Bối cảnh đã xác minh: pilot trên fixture tổng hợp cho kết quả âm (proxy stop: Rule 1 không đánh giá được theo nguyên văn (uTabPFN/CDC chưa chạy, không có benchmark); proxy untrimmed ≥ influence trimming; MAD 1.000 > scorer 0.365); code không có TFM; chưa có kết quả benchmark. Hạn ACIIDS 2027: **31/10/2026 23:59 AoE = 01/11/2026 18:59 ICT** (nguồn chính thức, kiểm 2026-10-30). Yêu cầu: LNCS/LNAI, 12–15 trang gồm references, EasyChair. Double-blind và vị trí AI disclosure: UNVERIFIED.

Coordinator **không** tự chọn đường nào dưới đây; mỗi đường cần một quyết định thuộc thẩm quyền tác giả.

## Đường A — Giữ CRIC-ED với TFM thật

- Cần phê duyệt: tạo/đăng nhập tài khoản PriorLabs và chấp nhận điều khoản weights; cài `tabpfn` (PyPI); pin checkpoint **TabPFN-2** (Prior Labs License = Apache-2.0 + attribution). Không dùng 2.5 (non-commercial) hoặc mặc định mới nhất (3.5, điều khoản chưa kiểm). Nguồn: github.com/PriorLabs/TabPFN, huggingface.co/Prior-Labs/TabPFN-v2-reg (đọc 2026-10-30).
- Phần cứng: README nêu CPU hỗ trợ tới ~1.000 mẫu cho checkpoint cũ; GPU khuyến nghị. Máy hiện có 12 luồng CPU, không xác nhận GPU. Flights/beers (~2.400 dòng) cần giới hạn context ≤1.000 (là một quyết định protocol phải đăng ký trước).
- Việc phải làm trước confirmatory: kiểm API phân phối (numerical/categorical), protocol mới đóng băng cho dữ liệu thật (prereg hiện tại vẫn hiệu lực cho estimand, baselines, 5 seed, 1.000 bootstrap), triển khai baselines DDC, IF, CDC, uTabPFN (mỗi cái có license/phụ thuộc riêng chưa kiểm), paired context logging, chạy 4 dataset × 5 seed × các arm, rồi viết 12–15 trang.
- Ước lượng thô: tích hợp + baselines 1–2 ngày, chạy CPU nhiều giờ đến vài ngày, viết 1–2 ngày. **Không khả thi một cách trung thực trước 01/11 18:59 ICT.**

## Đường B — Fallback theo preregistration

- Prereg Rule 1 (điều kiện nguyên văn chưa đánh giá được, chỉ có proxy âm) quy định: "STOP CRIC-ED and activate Fallback Framing 1 (CS-ED)" (selective abstention qua multi-context resampling). CS-ED chỉ được mô tả định tính trong `docs/BRAINSTORM.md`; chưa có estimand, metric abstention, ngưỡng hay baseline đóng băng → cần tác giả chấp thuận và một protocol mới đăng ký trước confirmatory.
- Nếu không có TFM, CS-ED sẽ dựa trên scorer heuristic đang thua MAD trên pilot; giá trị khoa học thấp nếu không đổi scorer.
- Lựa chọn ngoài prereg (thăm dò `src/cced/`, purification cấp ô): **không** được prereg định nghĩa → là pivot mới, cần phê duyệt scope. Kết quả thăm dò trên dev `movies_1` là âm (không hơn matched-random; dưới baseline đơn giản trên lỗi thật). Không khuyến nghị.
- Lưu ý dữ liệu: thống kê mô tả lỗi của cả 5 bảng RAHA đã bị xem ngày 2026-10-30; protocol mới phải công khai điều này hoặc dùng bảng chưa xem.

## Đường C — NO-GO cho hạn này, tiếp tục nghiên cứu

- Giữ kết quả âm có tài liệu, hoàn thiện hạ tầng (đã làm: archive, paired RNG, tests, bib), chọn A hoặc B với thời gian đủ, nhắm hội nghị/tạp chí sau (CFP cần kiểm từ nguồn chính thức; chưa kiểm).
- Có thể viết preprint/internal report về kết quả âm và bài học protocol; kiểm chính sách trước khi công khai.

## Khuyến nghị của coordinator

**NO-GO FOR THIS DEADLINE** (Đường C), sau đó chọn A (nếu chấp nhận điều khoản PriorLabs và có GPU/thời gian) hoặc B với protocol mới. Lý do: mọi đường đều cần protocol mới đóng băng + confirmatory runs + baselines chưa có + 12–15 trang, trong khoảng < 40 giờ; rút gọn sẽ vi phạm chuẩn đã cam kết.

## Các việc đã làm không phụ thuộc quyết định

Xem `docs/review/AUDIT_20261030.md` (archive pilot hash-identical, tái lập chính xác, sửa RNG + paired streams + context logging, 6 test mới, bib sửa theo nguồn chính, manuscript hiệu chỉnh thành internal draft kết quả âm, STATE/CLAIM_EVIDENCE/EXPERIMENT_LOG/readiness/README cập nhật).

## Quyết định của tác giả — 2026-10-30

- **Quyết định:** NO-GO cho hạn ACIIDS 2027 (31/10/2026 23:59 AoE). Không nộp bản nào trong đợt này.
- **Người quyết định:** tác giả/người dùng, trả lời câu hỏi quyết định của coordinator ngày 2026-10-30.
- **Lý do (theo brief):** chưa có bằng chứng benchmark, chưa có TFM, proxy stop âm trên fixture; mọi đường tiếp cần protocol mới đóng băng + confirmatory runs + 12–15 trang trong < 40 giờ.
- **Hệ quả:** `paper/main.tex` giữ trạng thái INTERNAL DRAFT; không chuẩn bị gói nộp; prereg giữ nguyên. Đường A (TFM) hay B (fallback/pivot) cho giai đoạn sau **chưa được chọn**; không chạy thực nghiệm phụ thuộc vào lựa chọn đó.

## Quyết định của tác giả — Đường A (ghi bổ sung, 2026-10-30 ~05:05 ICT)

- **Nguồn:** câu trả lời trực tiếp của tác giả cho câu hỏi quyết định thứ hai của coordinator Claude trong phiên 2026-10-30 (ngay sau quyết định NO-GO). Lựa chọn được chọn, nguyên văn: "Đường A: TFM thật — Giữ câu hỏi CRIC-ED gốc với TabPFN-2. Bạn tự tạo tài khoản PriorLabs và chấp nhận điều khoản weights; tôi cài tabpfn (PyPI), pin checkpoint, chạy CPU (≤1.000 mẫu context)."
- **Phạm vi được duyệt theo lựa chọn đó:** cài `tabpfn` từ PyPI vào môi trường cục bộ; tải và pin checkpoint TabPFN-2; chạy CPU cục bộ; tiếp tục câu hỏi CRIC-ED với TFM thật. Không bao gồm: chi phí, GPU/cloud trả phí, nộp bài, công bố.
- **Xác minh sau quyết định (coordinator, 2026-10-30):** weights TabPFN-v2 trên Hugging Face không bị gate; `tabpfn==9.2.0` chỉ yêu cầu đăng nhập PriorLabs cho v2.5 trở lên, nên **không cần tài khoản PriorLabs** cho v2. Điều khoản áp dụng: Prior Labs License v1.1 (Apache-2.0 + điều 10 attribution; dùng nội bộ để benchmark không cần attribution; phân phối thì kèm license và ghi "Built with PriorLabs-TabPFN"). Checkpoint pin: `data/manifests/tabpfn_v2_checkpoints_20261030.json`.
- **Chưa được quyết định:** các điểm trong `docs/proposals/V2_AMENDMENT_20261030.md` (biên thông tin group/row, control khớp compute, phạm vi thống kê). Chưa có freeze.

## Quyết định của tác giả về đề xuất sửa đổi v2 (2026-10-30 ~05:10 ICT)

Nguồn: câu trả lời trực tiếp của tác giả cho 4 câu hỏi của coordinator Claude.
1. **Ownership:** Claude tiếp quản vai coordinator; Codex đã dừng. Giữ nguyên code/test Codex đã viết, không ghi đè công việc của Codex.
2. **Biên thông tin:** row-level là phân tích chính (chỉ loại hàng của ô đích; bản ghi khác cùng thực thể là bằng chứng hợp lệ); leave-entity-out là phân tích phụ trên các bảng có khóa thực thể công khai.
3. **Phạm vi thống kê:** mô tả theo từng bảng (đơn vị = bảng nguồn), hiệu paired + khoảng bất định theo từng bảng, macro mô tả; không có phán quyết thắng/thua nhị phân xuyên dataset.
4. **Control khớp compute:** có. Nested pass-1 chung trong pool huấn luyện ngoài, dùng cho purify và cho một random control khớp compute; báo cáo chi phí từng phần.

Các quyết định này được đưa vào `prereg/PREREGISTRATION_V2_1.md` (bản sửa đổi; v1 và v2 giữ nguyên).

## Chỉ thị mới của tác giả — Hoàn thiện bài để tác giả nộp ACIIDS 2027 (2026-10-30 ~11:45 ICT)

- **Nguồn & thời điểm:** Chỉ thị trực tiếp từ tác giả do coordinator Claude chuyển tiếp vào khoảng 11:45 ICT ngày 2026-10-30.
- **Nội dung chỉ thị:** Hoàn thiện bài báo càng nhanh càng tốt để TÁC GIẢ tự nộp vào ACIIDS 2027 (hạn chót: 31/10/2026 23:59 AoE = 01/11/2026 18:59 ICT; định dạng PDF LNCS/LNAI, 12–15 trang gồm tài liệu tham khảo; nộp qua EasyChair).
- **Ý nghĩa kế hoạch:** Chỉ thị này thay thế quyết định NO-GO trước đó về mặt mục tiêu kế hoạch; chuyển mục tiêu sang hoàn thiện đầy đủ bài báo khoa học có kiểm chứng thực nghiệm chặt chẽ để tác giả kịp nộp.
- **Quy tắc bất biến:** Tác giả là người duy nhất nộp bài, tải bài lên hệ thống hay công bố. Các agent (Codex, Claude, Antigravity) tuyệt đối không tự ý nộp bài, upload file ra ngoài, push branch hay liên hệ với bất kỳ ai.
- **Phân công điều phối:** Claude giữ vai trò coordinator (review, không trực tiếp sửa file); Antigravity là worker duy nhất triển khai hoàn thiện code/bài báo trên worktree `agy/finish`.

