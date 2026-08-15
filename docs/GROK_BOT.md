# Grok Bot — binding this ContentPack

You are operating as a **Grok Bot** agent that reads and writes the same shared institutional second brain used by local agents (Claude Code, Grok Build, Codex).

This file is the binding contract. It does **not** install a Claude-style plugin. Grok Bot skills are workflows; enable the skill that matches your role and follow the rules below.

## Privacy (non-negotiable)

- The working second brain is private. This public pack never documents its remote URL, org/repo slug, or clone command.
- Knowledge root is always a path the human already has, or the environment variable `SECOND_BRAIN_ROOT`.
- Never copy live nodes, real client names, contacts, or production facts into public repos, samples, or chat that might be logged publicly.
- Public samples remain Northstar / Lumenfield fiction only.
- If a task would require leaking the private location, stop and ask the human.

## Identity

- Actor string pattern: `grok-bot/<plugin-id>`  
  Examples: `grok-bot/second-brain-core`, `grok-bot/content-media`, `grok-bot/news-digest`, `grok-bot/account-management/<client-slug>`
- Claim identity **per process**:
  - Preferred: pass `--author grok-bot/<plugin-id>` on every write, **or**
  - Set `SECOND_BRAIN_IDENTITY=grok-bot/<plugin-id>` in this agent's environment only.
- Do **not** use a single shared `knowledge/.identity.json` for a multi-agent fleet.
- On first use, write an `AgentIdentity` node. On every successful write, emit a `WriteEvent` (actor, plugin, host=`grok-bot`, timestamp, type, path).
- Git author may remain the human; the actor field is the durable claim for folds and audits.
- Chat prefix (optional): `Grok Bot: <Role>`.

## Knowledge root

```bash
export SECOND_BRAIN_ROOT="${SECOND_BRAIN_ROOT:-knowledge}"
# Human points this at their existing private checkout. Never invent a remote.
```

All pack scripts accept `--bundle` / knowledge root relative to cwd or via the env var.

## Deterministic write boundary

The model proposes structured content. Scripts validate and write.

```bash
python3 scripts/sbc_common.py write \
  --bundle "${SECOND_BRAIN_ROOT}" \
  --type Concept \
  --folder concepts \
  --title "Example title" \
  --author "${SECOND_BRAIN_IDENTITY:?claim an identity first}"
```

Job packs use their own `*_common.py` with the same contract.

**Forbidden:** `cat`, `echo`, or direct file writes of Markdown into the knowledge tree.

**Required:** type ownership. Refuse types owned by another ContentPack.

## Concurrent writers (serialize)

When multiple Grok Bots (or local agents) share the same private remote:

1. Acquire a lock (`brain-write` helper or flock).
2. `git pull --rebase` on the existing checkout.
3. Run the pack write script with `--author`.
4. Commit if needed; push to **whatever remote the checkout already has**.
5. Drop lock.
6. Fail closed on conflict. Never force-push. Never push to a public remote.

Report the path and commit SHA, not a dumped graph.

## Progressive disclosure

Default ContextPack: **2 hops** (budget ~20 nodes is a soft hint, not a schema).

- News packs news; media packs content; account managers pack only their `owned_by` client root.
- Pack before answering or writing. Do not load the entire tree.

## Skill binding (how Grok Bot "installs")

1. Enable **only** the skill(s) for this agent's role / ContentPack.
2. Set `SECOND_BRAIN_IDENTITY` and `SECOND_BRAIN_ROOT` (or equivalent).
3. GitHub access to the already-private remote is sufficient until the human requests a clone on the shared box.
4. A clone on a shared box is an ownership problem; do not solve it by making the repo public.

Grok Bot does not run `/plugin marketplace add`. That is a Claude Code / Grok Build verb. Grok Bot UI "plugins" are MCP connectors and private skills; this ContentPack is bound via the skill workflow in this file.

## Three memory planes

| Plane | Location |
|-------|----------|
| Procedural | Skills, this file, harness rules |
| Working | Current turn + packed context |
| Institutional | The private OKF Markdown tree |

Agent profile / personal long-term prefs stay outside the institutional tree.

## Allowed actions summary

- Pack (2 hops) → answer or propose write
- Write only owned types via scripts + `--author`
- Emit AgentIdentity / WriteEvent
- Report path + SHA

## Forbidden actions summary

- Raw Markdown writes
- Types owned by other packs
- Documenting or hard-coding the private remote
- Copying live records into public artifacts
- Force-push or public-remote push

## Related public packages

- second-brain-core (this foundation)
- Job ContentPacks: executive-coordination, account-management, sales-pipeline, executive-job-search, consulting-leads, content-media, news-digest, gtm-positioning
- Foundations: okf-plugin, project-knowledge-capture, system-architecture-capture, data-engineering-knowledge-capture, wiki_ticket_sdd, okf-agent-graph

Point every host at the same human-owned knowledge root so Grok Bots and laptop agents compound one institutional memory.
