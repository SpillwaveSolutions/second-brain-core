# Changelog

## 0.3.7

- WikiTicket SDD (worklog) is the tracking system for this plugin.


## 0.3.6

- Three-host hooks: Codex + Cursor-native when Claude hooks exist.


## 0.3.5 — 2026-08-17

- **Cursor host.** `.cursor-plugin/plugin.json` (Cursor Plugins) plus `.cursor/rules/second-brain.mdc`. Docs: `docs/CURSOR.md`. `docs/GROK_BOT.md` now covers Grok Bot spawning Cursor cloud agents.

## 0.3.4 — 2026-08-17

- **Fleet actor registry.** If the operator `actors.json` lists `actors`,
  `brain_session.py open` fails closed on an unknown actor. No registry
  keeps the old behavior.
- **Type allowlist.** `restrict` maps a type to allowed actors. Pack +
  operator lists intersect. DailyDigest / WeeklyDigest are CoS-only.
- Pack roots are packing hints, not access control (`docs/ISOLATION.md`).
- Sample: `actors.sample.json`. Paths only.

## 0.3.3 — 2026-08-16

- ContextPack has a **token budget**: default 1/4 of the model window
  (`SECOND_BRAIN_WINDOW_TOKENS`, default 128000 → 32000 tokens). Override with
  `--max-tokens` or `SECOND_BRAIN_PACK_MAX_TOKENS`.
- Pack is **fail-closed** when the rendered subgraph exceeds the budget. Node
  clip (`--max-nodes`) is not a token budget and does not write a truncated pack.
- **Bodies off** unless that node is the pack root. Neighbors keep title, type,
  path, and frontmatter `description` only.
- Token estimate is chars/4. Success JSON reports `tokens`, `budget`, `window`.

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
