# Setup và kiểm tra trên Windows

Repo được chọn: `F:/competitions/ACIIDS/ACIIDS2027`. Nguồn team card nằm ở thư mục sibling team_package và snapshot trong docs/context. Chạy lệnh ở đúng root này.

```powershell
uv sync --locked
uv run python tools/check_setup.py
uv run pytest -q
uv run python tools/check_mcp.py
uv run python tools/lit.py --help
uv run python tools/verify_refs.py --help
```

`uv.lock` khóa dependencies nhẹ cho nghiên cứu/setup. Chưa cài backbone hoặc compute framework. Trước G0, tạo environment riêng/pinned dependencies cho model sau khi kiểm phần cứng và license. Không tự dùng default checkpoint mới thay bản card.

## Nạp vào agent
- Codex: mở đúng repo, trust theo UI/CLI của bạn; kiểm AGENTS/skill inventory/MCP. Project config chỉ có hiệu lực theo trust và managed policy. Custom role TOML ở `.codex/agents/`; role prompt dài trong docs/prompts. Không tự launch role.
- Claude Code: đọc CLAUDE.md; kiểm `/mcp` và `/agents`/skill list trong phiên đang dùng. Toàn bộ các vai nghiên cứu (Literature, Methods, Implement, Critic, Review, Writer, Coordinator) được tổ chức thống nhất; mirror từ `.agents/skills/`. Khi cập nhật file, refresh/start session và xác minh inventory thực.
- Antigravity: root `AGENTS.md`, `.agents/rules/*.md` (YAML trigger), `.agents/skills/*/SKILL.md`, `.agents/agents/*.md` (custom agents) và `.agents/mcp_config.json`. Các agent được cấu hình làm main-agent chọn thủ công; không bật auto-subagent. Mở Customizations/Agent Manager để xác minh inventory runtime. Nguồn: https://antigravity.google/docs/rules, https://antigravity.google/docs/skills, https://antigravity.google/docs/mcp, https://antigravity.google/blog/introducing-custom-agents (đã kiểm 2026-10-29).

MCP này chỉ có literature metadata + local research_status, không có modal_run. CLI và MCP dùng cùng litlib/cache. Network lookup có thể lỗi/429; ghi ERROR/UNVERIFIED, không tự đánh VERIFIED. `research_status` không dò secrets/hardware hoặc gọi external API.

Custom-agent “read-only” là chỉ dẫn, không sandbox riêng trong Codex. Claude role tool list đọc giới hạn khả năng hơn; nếu cần test/ghi report thì giao tác vụ phù hợp và scope rõ. Không dùng permission bypass.

## Sources checked 2026-10-28
Codex: https://learn.chatgpt.com/docs/agent-configuration/agents-md ; https://learn.chatgpt.com/docs/build-skills ; https://learn.chatgpt.com/docs/agent-configuration/subagents ; https://learn.chatgpt.com/docs/extend/mcp?surface=cli
Claude: https://code.claude.com/docs/en/sub-agents ; https://code.claude.com/docs/en/skills
Antigravity: https://www.antigravity.google/docs/rules/ ; https://www.antigravity.google/docs/mcp
Python MCP SDK: https://github.com/modelcontextprotocol/python-sdk

Nếu phiên bản/runtime khác schema đã kiểm, giữ prompt vai trò và sửa adapter theo docs thực có; không giả báo đã tự discover.
