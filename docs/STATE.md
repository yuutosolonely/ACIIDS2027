# Trạng thái nghiên cứu CRIC-ED — ACIIDS 2027

Cập nhật: 2026-10-29.

## Ý tưởng và bằng chứng
- Idea 3 đang được nghiên cứu dưới working title **CRIC-ED**. Đây vẫn là proposal; chưa có quyết định pivot cuối cùng hoặc kết quả benchmark.
- Giả thuyết trung tâm: lỗi có cấu trúc trong in-context table có thể làm giảm khả năng định vị lỗi cấp ô; context intervention cần được đánh giá cùng rare-valid controls.
- Các hướng dự phòng và tiêu chí falsification nằm trong `docs/BRAINSTORM.md`. Novelty chưa được xác lập.
- Chưa có model/benchmark runs trong repository. Mọi claim hiệu năng là PENDING; xem `docs/CLAIM_EVIDENCE.md`.

## Workspace
- ACIIDS workspace files are installed locally. Static configuration check last observed PASS and skill mirror last observed MATCH on 2026-10-29; current run details are recorded in `docs/SETUP_VALIDATION.md`.
- Rules and skills use Antigravity-supported workspace paths. Seven project custom agents now have static definitions in `.agents/agents/`; runtime discovery still needs confirmation in the Antigravity UI.
- `docs/context/team_package/` retains selected idea-source snapshots. Current venue requirements are only in `docs/context/conference/`; old planning material is not current policy or authorization.

## Conference and authorization
- ACIIDS extended deadline listed on the official page: 31 October 2026, 23:59 AoE (1 November 2026, 18:59 Asia/Bangkok). Recheck EasyChair and the official call before any submission.
- Anonymization and exact proceedings AI-disclosure instructions remain unresolved.
- Current budget is $0; paid compute and paid APIs are unauthorized. No model weights or benchmark data have been downloaded by this setup.

## Next gates
1. Confirm all workspace custom agents, skills and MCP server appear in the actual Antigravity session.
2. Resolve dataset access/license, hardware, pinned model/checkpoint capability and inference protocol.
3. Freeze a pilot protocol and run only within the user's authorization.
4. Reassess feasibility against the conference deadline before drafting claims of completed results.
