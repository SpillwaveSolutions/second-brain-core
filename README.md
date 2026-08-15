# Second Brain Core

Shared foundation for Spillwave ContentPack plugins: OKF schemas, typed edges, deterministic write helpers, and progressive-disclosure packing.

MIT. Works with **Claude Code**, **Grok Build**, **Codex**, **Agent Plugins 1.0** clients, **Grok Bot**, and **LangChain Deep Agents**. Writes OKF Markdown + YAML into a shared second-brain bundle so other agents and local jobs can read the same graph.

## Install

### Claude Code

```bash
/plugin marketplace add SpillwaveSolutions/second-brain-core
/plugin install second-brain-core@SpillwaveSolutions
```

### Grok Build

Grok Build loads Claude-compatible plugins with zero extra config. Optional native metadata lives under `.grok-plugin/`.

### Codex (Agent Skill Standard)

Skills live under `skills/*/SKILL.md`. Install via your Codex skill installer, clone, or any Agent Skills-compatible path.

### Agent Plugins 1.0 (universal portable format)

This repo includes a root [`plugin.json`](plugin.json) conforming to [Agent Plugins 1.0](https://agent-plugins.org). Compatible clients (Codex, Cursor, VS Code, ChatGPT, Kiro, and others) discover `skills/` and optional MCP from the fixed layout.

### Skilz CLI

```bash
skilz install SpillwaveSolutions/second-brain-core
```

### LangChain Deep Agents / Deep Agents Code

See [docs/LANG_CHAIN_DEEP_AGENTS.md](docs/LANG_CHAIN_DEEP_AGENTS.md). Point `skills=` or SkillsMiddleware sources at this package's `skills/` directory after clone or `npx skills add`.

### Grok Bot

Grok Bot does not use `/plugin install`. Bind via the skill workflow in [docs/GROK_BOT.md](docs/GROK_BOT.md) (actor string, `SECOND_BRAIN_ROOT`, deterministic write helpers). No private remote is documented in public files.

### Knowledge root

Point every host at a shared knowledge root the human already owns (default `knowledge/` relative to cwd, or `SECOND_BRAIN_ROOT`). All sibling ContentPack plugins write into the same tree. Public samples use Northstar fiction only.

## Multi-host matrix

| Host | How to load | Identity | Knowledge root |
|------|-------------|----------|----------------|
| Claude Code | marketplace + plugin install | `SECOND_BRAIN_IDENTITY` / whoami | local path or env |
| Grok Build | zero-config Claude plugin | same | same |
| Codex | Agent Skills / plugin install | `--author` | same |
| Agent Plugins clients | root `plugin.json` + `skills/` | env / `--author` | same |
| Grok Bot | skill binding (see GROK_BOT.md) | `grok-bot/<plugin-id>` | `SECOND_BRAIN_ROOT` |
| LangChain Deep Agents | `skills=` path / SkillsMiddleware | `deep-agents/<role>` | `SECOND_BRAIN_ROOT` |

## Skills

| Skill | What it does |
|-------|----------------|
| `/sbc-init` | Scaffold the catalogs this plugin owns |
| `/sbc-capture` | Capture a noun into the shared second brain (deterministic write) |
| `/sbc-pack` | Build a bounded ContextPack from a root concept |
| `/sbc-validate` | Validate frontmatter, types, and links |
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
  --author "${SECOND_BRAIN_IDENTITY:?claim an identity first: brain.py whoami --claim}"
```

Never invent `rel` values. Never write types owned by another plugin.

This plugin is the shared substrate. Domain plugins (sales-pipeline, content-media, …) depend on these write and pack conventions.

## Related plugins

- [second-brain-core](https://github.com/SpillwaveSolutions/second-brain-core) — shared pack engine and typed-edge conventions
- [project-knowledge-capture](https://github.com/SpillwaveSolutions/project-knowledge-capture) — the “why” second brain
- [system-architecture-capture](https://github.com/SpillwaveSolutions/system-architecture-capture) — the “what is running” second brain
- [wiki_ticket_sdd](https://github.com/SpillwaveSolutions/wiki_ticket_sdd) — visible work log
- Job ContentPacks: executive-coordination, account-management, sales-pipeline, executive-job-search, consulting-leads, content-media, news-digest, gtm-positioning

## License

MIT. Copyright 2026 Rick Hightower / contributors.
