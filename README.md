# Second Brain Core

Shared foundation for Spillwave ContentPack plugins: OKF schemas, typed edges, deterministic write helpers, and progressive-disclosure packing. Dual-host (Claude Code + Grok Build + Codex).

MIT. Dual-host: **Claude Code**, **Grok Build**, and **Codex** (Agent Skill Standard). Writes OKF Markdown + YAML into a shared second-brain bundle so other agents and local jobs can read the same graph.

## Install

```bash
# Claude Code
/plugin marketplace add SpillwaveSolutions/second-brain-core
/plugin install second-brain-core@SpillwaveSolutions

# Skilz CLI
skilz install SpillwaveSolutions/second-brain-core
```

Point the plugin at a shared knowledge root (default `knowledge/`). All sibling ContentPack plugins write into the same tree.

## Skills

| Skill | What it does |
|-------|----------------|
| `/sbc-init` | Scaffold the catalogs this plugin owns |
| `/sbc-capture` | Capture a noun into the shared second brain (deterministic write) |
| `/sbc-pack` | Build a bounded ContextPack from a root concept |
| `/sbc-validate` | Validate frontmatter, types, and links |
| `/sbc-session` | Open or close an isolated write session (worktree + PR) |
| `/sbc-doctor` | Health check of the bundle this plugin owns |

## Nouns this plugin may write

| Type | Meaning |
|------|---------|
| `Concept` | Generic typed knowledge node |
| `ContextPack` | Bounded ranked typed-hop subgraph |
| `TypedEdge` | Directed relationship between concepts |
| `AgentIdentity` | Stable identity string for a writer agent |
| `WriteEvent` | Append-only record of a deterministic write |

## Relationships

| `rel` | Meaning |
|-------|---------|
| `related_to` | Soft association |
| `depends_on` | Hard dependency |
| `owned_by` | Accountability |
| `originates_from` | Provenance |
| `supersedes` | Replaces older concept |
| `documents` | Narrative about target |

## Catalogs

- `concepts/`
- `packs/`

## Deterministic write boundary

The model proposes. Schema-enforced scripts commit:

```bash
python3 scripts/sbc_common.py write \
  --bundle knowledge \
  --type Concept \
  --folder concepts \
  --title "Example" \
  --author "Grok Bot: Second Brain Core"
```

Never invent `rel` values. Never write types owned by another plugin.

This plugin is the shared substrate. Domain plugins (sales-pipeline, content-media, …) depend on these write and pack conventions.

## Related plugins

- [second-brain-core](https://github.com/SpillwaveSolutions/second-brain-core) — shared pack engine and typed-edge conventions
- [project-knowledge-capture](https://github.com/SpillwaveSolutions/project-knowledge-capture) — the “why” second brain
- [system-architecture-capture](https://github.com/SpillwaveSolutions/system-architecture-capture) — the “what is running” second brain
- [wiki_ticket_sdd](https://github.com/SpillwaveSolutions/wiki_ticket_sdd) — visible work log

## Multi-host

Works with Claude Code, Grok Build, Codex, Agent Plugins 1.0 clients, Grok Bot, and LangChain Deep Agents.

| Host | How to load |
|------|-------------|
| Claude Code | marketplace + plugin install |
| Grok Build | zero-config Claude plugin |
| Codex | Agent Skills / `hooks/hooks.json` |
| Agent Plugins clients | root `plugin.json` + `skills/` |
| Grok Bot | [docs/GROK_BOT.md](docs/GROK_BOT.md) |
| LangChain Deep Agents | [docs/LANG_CHAIN_DEEP_AGENTS.md](docs/LANG_CHAIN_DEEP_AGENTS.md) |

Write isolation (worktree + PR) lives in second-brain-core: [docs/ISOLATION.md](https://github.com/SpillwaveSolutions/second-brain-core/blob/main/docs/ISOLATION.md). Point `SECOND_BRAIN_ROOT` at the session bundle. Never hard-code a private remote.

Eight job-function plugins plus core. Knowledge root is always a local path or env the human already owns.

## License

MIT. Copyright 2026 Rick Hightower / contributors.
