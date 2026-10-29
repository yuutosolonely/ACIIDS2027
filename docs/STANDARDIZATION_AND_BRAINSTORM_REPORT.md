# Báo cáo chuẩn hóa workspace và brainstorm — ACIIDS 2027

Cập nhật: 2026-10-29. Repository: `F:/competitions/ACIIDS/ACIIDS2027`.

## Thay đổi trong lần cập nhật này
- Đồng bộ tên working title CRIC-ED trong tài liệu vận hành; giữ tên source card ban đầu chỉ trong snapshot provenance; package Python hiện dùng namespace `cric_ed`.
- Gỡ handbook migration không còn thuộc context nghiên cứu; cập nhật source manifest và setup manifest tương ứng.
- Bổ sung bảy Antigravity custom-agent definitions trong `.agents/agents/`, mỗi role chọn chạy trực tiếp; không bật auto-subagent.
- Giữ rules ở `.agents/rules/`, skills ở `.agents/skills/` và project MCP ở `.agents/mcp_config.json`.
- Sửa policy ledger để phản ánh khung AI theo risk, oversight và disclosure của Springer Nature; ACIIDS page không tự quy định chi tiết AI use.
- Sửa báo cáo trạng thái để không tuyên bố hoàn tất tuyệt đối khi chưa xác nhận runtime hoặc chạy nghiên cứu.

## Tình trạng idea
CRIC-ED tiếp tục là working proposal cho Idea 3, chưa được chốt như quyết định cuối và chưa có kết quả thực nghiệm. Các hướng dự phòng, baseline, RQ và điều kiện dừng được ghi trong `docs/BRAINSTORM.md`; novelty còn cần kiểm chứng closest work và chạy pilot có protocol đóng băng.

## Kiểm tra ghi nhận
- Trước lần chỉnh sửa này, static setup check báo PASS và skill mirror báo MATCH.
- Lần pytest gần nhất trong môi trường kiểm tra báo 10 passed, 1 lỗi khởi tạo do `PermissionError` khi tạo thư mục tạm dưới `.cache/pytest`; không đủ căn cứ ghi toàn bộ test PASS.
- Sau các chỉnh sửa hiện tại, `tools/check_setup.py` PASS (9 skills, 9 snapshots) và `tools/sync_skills.py --check` MATCH. Runtime discovery phải được kiểm tra trong Antigravity UI; file tĩnh không chứng minh runtime đã nạp agent.
- Không có benchmark/model run, không tải weights/datasets, không có paid compute authorization và chưa compile manuscript.

## Quy định và điểm còn mở
Nguồn ACIIDS và Springer, trạng thái xác minh, ngày truy cập và unresolved items được quản lý trong `docs/context/conference/POLICIES.md` và `DATES.md`. Hiện cần kiểm tra lại EasyChair track/ẩn danh và disclosure instructions gần lúc nộp.
