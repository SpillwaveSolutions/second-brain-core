# Changelog

## 0.3.2 — 2026-08-16

- Codex / Claude PostToolUse hook is **fail-closed**: `sbc-hook-validate.sh` runs `sbc_common.py validate` after `apply_patch` / Write / Edit and exits non-zero on a broken bundle.
- Removed the SessionStart print reminder (a reminder is not a harness).
- Writes outside a knowledge bundle stay a silent no-op.

## 0.3.1 — 2026-08-16

- Privacy: isolation tests and docs use only fictional **lumenfield-detector** / **northstar-console** actors.
- `scripts/brain_session.py` marked as the canonical isolation helper; foundation packs vendor this copy.


## 0.3.0 — 2026-08-15

- Grok Bot onboarding: `docs/ONBOARDING.md` (LLM-wiki history, destination state, public repo list)
- Full type ownership in `docs/GROK_BOT.md` (every registry noun, not a subset)
- Registry folders filled so writes land in the right catalog
- Linked Northstar sample graph (typed edges, packable in 2 hops)
- Version stamps aligned across plugin.json, marketplace, and package.json
- README related-plugins list now covers the whole suite plus foundations

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
