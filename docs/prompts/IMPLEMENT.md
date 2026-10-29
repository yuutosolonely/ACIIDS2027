# implement — CRIC-ED / ACIIDS 2027

Bạn nhận nhiệm vụ triển khai code và thực nghiệm CRIC-ED. Tuân thủ AGENTS.md, docs/AUTHORIZATION.md và docs/WORKFLOW.md.
Đọc: docs/IDEA.md, docs/experiment-plan.md, docs/HARNESS.md, data/DATA_CARD.md, prereg and open findings.
Skill liên quan: tabfm-protocol, experiment-design; tải chỉ khi cần, không giả định tool được mô tả là đang khả dụng.

Own assigned source/tests/config/scripts. Build CPU scorer/data checks before model runs. No clean-label leakage, default-checkpoint drift or unsupported claims. Report commit, artifacts and failed runs.

Before work: confirm cwd, source revision/snapshot, dirty status, exact task, owned output paths and acceptance checks. If not yet a Git snapshot, state that and use an artifact manifest; never invent a hash.
Keep measured/source-reported/hypothesis/proposal/pending separate. Report source files, checks really run, results, remaining decisions and next action. Use docs/templates/HANDOFF.md when saving a handoff.
No additional agents/worktrees/messages, paid runs or publication without applicable user authorization. Continue authorized independent work when evidence is missing.
