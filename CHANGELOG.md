# Changelog

## 0.2.0 — 2026-08-15

- Write isolation: `scripts/brain_session.py` (worktree + branch + PR)
- Required `--author` / `SECOND_BRAIN_IDENTITY`; emit `WriteEvent` on write
- Agent Plugins 1.0 root `plugin.json`
- `docs/GROK_BOT.md`, `docs/LANG_CHAIN_DEEP_AGENTS.md`, `docs/ISOLATION.md`
- Codex hooks (`.codex-plugin` + `hooks/hooks.json`)
- Skill `sbc-session`

## 0.1.0 — 2026-08-14

- Initial public release
- Nouns: Concept, ContextPack, TypedEdge, AgentIdentity, WriteEvent
- Skills: sbc-init, sbc-capture, sbc-pack, sbc-validate, sbc-doctor
- Dual-host plugin manifests (Claude Code + Grok Build)
