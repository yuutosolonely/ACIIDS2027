# Workflow Idea 3

Đầu phiên: xác minh repo/worktree/source snapshot, đọc AGENTS, STATE, AUTHORIZATION và prompt vai trò; đọc IDEA/plan/prereg/evidence liên quan. Không nạp toàn bộ raw data hoặc lịch sử chat vào context.

Vòng làm việc: question → public-source check → proposed experiment → prereg/freeze → CPU validation → authorized model run → log → analysis → independent review → paper. Hiện mới setup/literature, chưa có model run.

Một task card ghi role, source commit/snapshot, read/write scope, concrete output và acceptance checks. Chủ file tích hợp báo cáo; agent khác không sửa đồng thời cùng file. Brainstorm là proposal tới khi tác giả chọn.

Handoff theo `docs/templates/HANDOFF.md`. Reviewer cần base/head commit đích và artifact manifest thật; không coi HEAD của nhánh review là code mới nhất. Untracked/ignored artifacts phải có đường dẫn snapshot được phép; không tự xuất hiện ở worktree khác.

CP0 scope/novelty; CP1 data/scorer/G0; CP2 prereg/freeze; CP3 evidence/ablation; CP4 paper/format/policy. Mỗi finding ghi evidence, consequence, reproduction và closure criterion. Không dùng số phiếu/điểm “accept” để bỏ qua lỗi soundness.

Cuối phiên: cập nhật STATE và handoff trong phạm vi được giao; báo source revision, checks thật, pending items, bước tiếp theo. Không tự tạo agent/nhắn leader/nộp bài.
