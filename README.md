# ACIIDS2027 — Idea 3 / CRIC-ED

Workspace nghiên cứu cho Idea 3 do người dùng chọn ngày **28/10/2026**.
Working title gốc (đề xuất TFM, chưa được thực hiện): *Masked In-Context Likelihood: Tabular Foundation Models as Training-Free Cell-Level Error Detectors under Self-Contamination*.

**Trạng thái (2026-10-30): NO-GO cho hạn ACIIDS 31/10/2026 (quyết định tác giả) / NOT READY.** Chưa có kết quả benchmark và chưa chạy TFM. Pilot trên fixture tổng hợp cho kết quả âm (proxy stop: Rule 1 không đánh giá được theo nguyên văn (uTabPFN/CDC chưa chạy, không có benchmark); proxy untrimmed ≥ influence trimming; xem `docs/STATE.md`, `docs/review/AUDIT_20261030.md`). Đang chờ quyết định tác giả trong `docs/DECISION_BRIEF_20261030.md`. Dữ liệu RAHA tải local trong `data/raw/` (gitignored; manifest `data/manifests/raha_download_20261030.json`).

Đọc theo thứ tự: `AGENTS.md` → `docs/STATE.md` → `docs/IDEA.md` → `docs/related-work.md` → `docs/BRAINSTORM.md` → `docs/experiment-plan.md`.

## Thiết lập
```powershell
uv sync --locked
uv run python tools/check_setup.py
uv run pytest -q
uv run python tools/check_mcp.py
```
Chỉ cài dependency cho setup, literature và MCP; chưa cài PyTorch, TabPFN, TabICL, Modal hay tải weights/datasets. Compiler paper chưa được xác nhận.

## Làm việc cùng agent
- Codex: `AGENTS.md`, `.codex/config.toml`, `.agents/skills/`, `.codex/agents/`.
- Claude Code: `CLAUDE.md`, `.claude/skills/`, `.claude/agents/`, `.mcp.json`.
- Antigravity: `AGENTS.md`, `.agents/rules/`, `.agents/skills/`, `.agents/mcp_config.json`.
- Prompt bắt đầu: `docs/prompts/IMPLEMENT.md`, `REVIEW.md`, `LITERATURE.md`, `METHODS.md`, `CRITIC.md`, `WRITER.md`, `COORDINATOR.md`.

Quyền chi tiêu và phạm vi hiện hành: `docs/AUTHORIZATION.md`. Checklist trước bài nộp: `docs/PAPER_GUIDE.md`. Hướng dẫn máy/phiên: `docs/SETUP.md`.

Các idea card gốc từ team package được giữ nguyên trong `docs/context/team_package/`; thiết kế đang làm nằm trong `docs/IDEA.md`. Giữ LICENSE sẵn có của repo; third-party resources có license riêng trong `THIRD_PARTY_NOTICES.md`.
