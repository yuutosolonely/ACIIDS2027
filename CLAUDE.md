# Claude Code adapter
Read and follow `AGENTS.md`. Shared rules live in `.agents/rules/`; canonical skills in `.agents/skills/` are mirrored to `.claude/skills/` by `tools/sync_skills.py`.
For a long session read the assigned file in `docs/prompts/` and `docs/STATE.md`.
`.claude/agents/` defines optional focused roles; launch only when authorized. A read-only tool allowlist may prevent saving reports: return the report to the caller rather than requesting broader tools unnecessarily.
Check `/mcp` for `aciids-lab`. No paid compute tools are exposed by this server.
