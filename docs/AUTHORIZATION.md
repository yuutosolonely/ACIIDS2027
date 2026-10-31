# Phạm vi ủy quyền nghiên cứu — ACIIDS 2027

Workspace nghiên cứu chuyên biệt cho bài báo tham dự hội nghị **ACIIDS 2027** (Idea 3 / CRIC-ED), đặt tại `F:/competitions/ACIIDS/ACIIDS2027`.

## Phạm vi được phép thực hiện
- Cập nhật và chuẩn hóa cấu trúc repository cục bộ, tài liệu, cấu hình agent/rules/skills/MCP.
- Kiểm tra mã nguồn, chạy test suite, kiểm tra tính toàn vẹn tĩnh (CPU local validation).
- Tìm kiếm, đọc và trích xuất tài liệu khoa học công khai (Semantic Scholar / arXiv / OpenAlex).
- Đề xuất thiết kế thực nghiệm, protocol kiểm chuẩn, brainstorm và lập kế hoạch nghiên cứu.

## Giới hạn và các hành động CHƯA được ủy quyền
- Ngân sách hiện tại: **$0.00**. Nghiêm cấm chạy các job trả phí (Modal / Cloud GPU / Paid APIs).
- Chưa được ủy quyền tải các checkpoint mô hình hoặc bộ dữ liệu có dung lượng lớn / điều khoản cấp phép mới chưa kiểm chứng.
- Tuyệt đối không tự ý nộp bài (submit EasyChair), xuất bản (publish), tạo release công khai hoặc gửi dữ liệu nghiên cứu nội bộ ra ngoài.
- Các role files và agent definitions trong `.agents/`, `.claude/`, `.codex/` là cấu hình tĩnh; không tự động khởi chạy môi trường đa tác tử song song ngoài tầm kiểm soát.
- Mọi thay đổi về phạm vi, ngân sách hoặc pivot đề tài đều phải có phê duyệt rõ ràng từ người dùng.

## Chỉ thị nghiên cứu tiếp nối — 2026-10-30

**Đối soát bàn giao mới nhất:** quyết định Path A và bốn sửa đổi v2 đã được tác giả chấp thuận, được ghi trong các phần bổ sung của `docs/DECISION_BRIEF_20261030.md` và checkpoint Claude `0aff63e`. Cho phép thực hiện T1–T8 của `docs/handoffs/TASKS_CODEX_V2_1_20261030.md` trên CPU local với dữ liệu/weights đã pin. Người dùng xác nhận chỉ Codex đang chạy; Codex tiếp quản cả điều phối và thực thi. Yêu cầu mới: cố gắng hoàn thành trong 8 giờ, đồng thời thực nghiệm phải được kiểm chứng đầy đủ. Các giới hạn $0, không submission/publication/upload vẫn giữ nguyên. Không tự thay các quyết định phương pháp đã duyệt bằng phương án v3.

Người dùng giao tiếp quản điều phối của Claude, thực hiện nghiên cứu và viết bài đến khi hoàn thiện; goal đang active: “thực hiện đến khi hoàn thiện bài paper nghiên cứu có thực nghiệm chi tiết và có cơ sở khoa học hoàn chỉnh đạt chuẩn nộp cho hội nghị ít nhất là rank B”.

Áp dụng cho công việc tiếp theo: tiếp tục nghiên cứu Idea 3/CRIC-ED, thiết kế protocol, triển khai và chạy thực nghiệm CPU local với dữ liệu/checkpoint đã có sau khi kiểm provenance/license, rà primary literature và viết/biên tập manuscript theo evidence. Coordinator xử lý các lựa chọn kỹ thuật trong phạm vi này và ghi lại trước evaluation; không gán chúng thành quyết định chi tiết mà tác giả đã nói trong lịch sử. Những tải/run trước chỉ thị vẫn giữ hồ sơ deviation, không được hồi tố phê duyệt.

Ngân sách vẫn $0; không phát sinh quyền tải checkpoint/accept điều khoản mới, compute/API trả phí, launch agent/worktree, upload manuscript vào dịch vụ kiểm tra, publication hoặc submission. NO-GO cho hạn ACIIDS hiện tại vẫn hiệu lực. “Xóa dấu vết AI” được thực thi như biên tập văn phong tự nhiên, bỏ diễn đạt khuôn mẫu và kiểm tính nguyên bản; không xóa disclosure bắt buộc hoặc khai sai nguồn gốc. Bản thảo cần tác giả xác minh trước sử dụng bên ngoài.


## Đối soát trạng thái nộp bài — 2026-10-31 (Claude)

Câu “NO-GO cho hạn ACIIDS hiện tại vẫn hiệu lực” ở trên được giữ làm lịch sử. Theo `docs/DECISION_BRIEF_20261030.md` (mục “Chỉ thị mới của tác giả … 2026-10-30 ~11:45 ICT”), tác giả đã đổi mục tiêu kế hoạch sang hoàn thiện bài để **tác giả tự nộp** ACIIDS 2027. Trạng thái chính xác hiện hành:
- Được phép: chuẩn bị, kiểm chứng và build bản thảo trong phạm vi $0 / CPU local.
- Không được phép với agent: nộp bài, đăng nhập EasyChair, upload manuscript, push, xuất bản, liên hệ bên ngoài.
- Chưa quyết định: việc **có nộp hay không** là quyết định riêng của tác giả sau khi đọc toàn văn; không suy ra từ chỉ thị chuẩn bị bài.
