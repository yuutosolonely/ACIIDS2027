# Kiểm định setup — 2026-10-29

> **Lượt reliability 2026-10-30:** suite scientific **49 passed**; suite tối thiểu **37 passed, 1 skipped**; runtime check **33 declared pins MATCH** sau khi lưu bản cũ và thêm torch. `.venv-tfm` kế thừa system site packages, không phải môi trường cô lập. Không tải/cài package hoặc chạy TFM/RAHA. Current snapshot/check record: `docs/handoffs/PREFLIGHT_RELIABILITY_20261030.json`; các bản ghi bên dưới là lịch sử.

> **Lượt CPU remediation 2026-10-30:** toàn suite trong `.venv-tfm` đạt **40 passed** bằng fixture tổng hợp/fake predictor; static setup PASS và skill mirror MATCH. Không tải/nạp checkpoint, không chạy benchmark. Danh tính source và kết quả: `docs/handoffs/CPU_REMEDIATION_20261030.json`. Kết quả tiếp nhận/hồ sơ cũ phía dưới giữ để truy vết; không suy từ test PASS ra scientific gate PASS.

> **Cập nhật đối soát 2026-10-30 (Codex):** source `06ded051a382bee8e6db47c582e46145fe544515` + working tree chưa commit. Chạy qua `uv run --locked --offline`: pytest **24 passed** (một warning không ghi được pytest cache), static setup **PASS**, skill mirror **MATCH**, MCP handshake/list/status **PASS**. Nội dung 2026-10-29 phía dưới và JSON cùng tên là lịch sử, không phải trạng thái hiện hành. Đã phát hiện weights và artifact smoke/dev v2 ở local; quyền hạn/provenance chưa đối soát xong. Không tải file hoặc chạy model trong lượt này. Setup PASS không xác lập research gate PASS. Xem `docs/STATE.md`.

Đích: `F:/competitions/ACIIDS/ACIIDS2027`. Đây là kiểm định cấu hình workspace; không phải xác nhận kết quả nghiên cứu.

## Trạng thái gần nhất
- Sau lần cập nhật hiện tại: `tools/check_setup.py` báo PASS với 9 skills và 9 source snapshots; `tools/sync_skills.py --check` báo MATCH.
- Lần pytest gần nhất trong lượt audit trước khi sửa: **10 passed, 1 lỗi khởi tạo**. Python bị `PermissionError` khi fixture tạo temp directory trong `.cache/pytest`; lỗi xảy ra trước khi test đó chạy. Không ghi nhận đây là PASS toàn suite; pytest chưa chạy lại sau chỉnh sửa.
- MCP handshake trước đó đã PASS với bốn công cụ literature/status; chưa chạy lại sau lần cập nhật này.
- Package Python dùng namespace `cric_ed`, đồng bộ giữa `pyproject.toml` và `uv.lock`.
- Bảy Antigravity custom-agent files đã được tạo trong `.agents/agents/`; cấu hình tĩnh đã được static checker đọc, nhưng chưa xác nhận inventory trong Antigravity UI.

## Chưa thực hiện
Không có model weights/dataset lớn được tải, không benchmark/model run, không paid compute, không compile manuscript và không submission. Ý tưởng vẫn là proposal; novelty và hiệu năng chưa được xác lập.

## Cách hoàn tất kiểm tra runtime
Mở đúng root repo trong Antigravity, mở Customizations/Agents, Rules, Skills và MCP Servers; xác nhận bảy agent, workspace rules/skills và `aciids-lab` hiện diện. Ghi lại trạng thái thực tế, không suy ra từ JSON/YAML parse.
