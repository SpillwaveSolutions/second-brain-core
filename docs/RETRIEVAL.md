# Query-time retrieval

Write isolation lives in [ISOLATION.md](ISOLATION.md). This file is the
read contract. It stops a Q&A turn from pulling search hits and pack
bodies into the parent working context.

## Why progressive disclosure is not enough

A ContextPack clips the graph. Default is 2 hops, about 20 nodes, and a
fail-closed token budget. Neighbor bodies stay off.

That clip still lands in the parent. Search hit lists land there too.
The parent then carries that working set for the rest of the turn.

Isolation is a child agent. The child runs search and pack. The parent
keeps a Retrieval card only.

## Rule

For Q&A, or any "what does the brain say" question, the parent MUST
spawn the pack's `*-retriever` agent (Claude Code Task / Agent, or the
host equivalent).

The parent does not run search or pack inline for retrieval.

Deepen stays in the child. If the card says `deepen` or `try-alt-seed`,
the parent may spawn again with that instruction. The parent still does
not unpack the graph.

Writes still pack first when the author needs a bounded subgraph to
edit. That is authoring, not Q&A retrieval.

## Scripts are the engine

Pack and search scripts stay deterministic.

| Pack | Engine |
|------|--------|
| second-brain-core | `sbc_common.py pack` |
| PKC | `pkc_pack` / `pkc_search` |
| SAC | `sac_pack` / `sac_search` |
| DEKC | `dekc_pack` / `dekc_search` |
| RKC | `rkc_pack` / thin `rkc_search` |

No LLM inside those scripts. The child scores fit and writes the card.

## Retrieval card

The child returns this shape and then stops.

```markdown
## Retrieval card
- Query: ...
- Seed: `/path` (`Type`) - why chosen
- Fit: high|medium|low - one sentence
- Engine: index|rg|scan (optional)
- Pack: hops=N nodes=N tokens=N/budget
- Lead nodes: (5-8 bullets: title · type · path · one-line why)
- Open gaps: missing edges / thin pack / none
- Next: stay|deepen|try-alt-seed `/other`
```

Minimum fields: Query, Seed, Fit, Pack hops/nodes/tokens, Lead nodes
(5-8, or fewer if the pack is smaller), Open gaps, Next.

Engine is optional. Omit it when the child only ran `sbc_common.py pack`.

Next is an instruction for the parent.

| Next | Meaning |
|------|---------|
| `stay` | Card is enough. Answer from it. |
| `deepen` | Spawn again. Child may walk 2 hops. |
| `deepen-2hop` | Same as `deepen`. Pack alias. |
| `try-alt-seed /path` | Spawn again with a different seed. |

Do not invent `rel` values when you read or write nodes.

Public samples stay Northstar / Lumenfield fiction. Never name or
clone-instruct a private remote.

## Pack-specific extensions

Foundation packs may add fields. They do not drop the shared minimum.

| Pack | Extra fields | Extra Next values |
|------|--------------|-------------------|
| SAC | Critical edges (up to 5). Blast hops when blast-radius ran. | `blast-radius` |
| DEKC | Lineage note (upstream / downstream one-liner, or none). | `lineage` |
| RKC | Spine counts (Finding, Claim, Evidence, or n/a). | `need-layer1-search` |
| PKC | Engine is required (`index` / `rg` / `scan`). | (shared set) |

Do not move those pack agents into core.

## Orthogonal fan-out

Each plane has its own retriever. Spawn in parallel when the question
crosses planes. Each child returns its own card. Do not merge packs
into the parent.

| Plane | Pack | Spawn | When |
|-------|------|-------|------|
| Project memory | [project-knowledge-capture](https://github.com/SpillwaveSolutions/project-knowledge-capture) | `knowledge-retriever` (`/pkc-retrieve`) | Feature, DecisionRecord, Meeting, Experiment, Question, TicketLink |
| Architecture | [system-architecture-capture](https://github.com/SpillwaveSolutions/system-architecture-capture) | `architecture-retriever` (`/sac-retrieve`) | Service, ApiContract, Package, Runtime, Pipeline, IdentityProvider, blast radius |
| Data platform | [data-engineering-knowledge-capture](https://github.com/SpillwaveSolutions/data-engineering-knowledge-capture) | `data-retriever` (`/dekc-retrieve`) | Table, Metric, LineagePath, IngestionJob, Transformation, Dashboard, DataProduct, GlossaryTerm, BusinessObject |
| Research | [research-knowledge-capture](https://github.com/SpillwaveSolutions/research-knowledge-capture) | `research-retriever` (`/research-retrieve`) | ResearchQuestion, Finding, Claim, Evidence, Subject, SourceDocument |

Core does not ship those agents. Enable the pack that owns the nouns.

## Child CLI

Preferred child flags:

```bash
python3 scripts/sbc_common.py pack --bundle "${SECOND_BRAIN_ROOT:-knowledge}" \
  --root "/concepts/northstar-concept.md" --tiny --summary
```

`--tiny` is 1 hop and 8 nodes. `--summary` prints compact markdown.
Bodies stay off for every node, including the seed. The token budget
is fail-closed. Node clip is not a token budget.

Foundation packs already have the same flags on `pkc_pack`, `sac_pack`,
`dekc_pack`, and `rkc_pack`. Prefer `--tiny --summary` in the child.
Use `--hops 2 --summary` only on a deepen step.

## Job-function packs without a retriever

Job-function ContentPacks (executive-coordination, account-management,
sales-pipeline, and siblings) may not ship a retriever yet.

Two paths:

1. Add a pack-local `*-retriever` later. Reuse this card.
2. Until then, spawn a short-lived child Task. The child runs
   `sbc_common.py pack --tiny --summary` (or the pack's own pack
   script if it already has `--summary`). The child returns this
   same card.

Do not run that pack inline in the parent "just this once."

## Core-owned concepts

This pack owns Concept, ContextPack, TypedEdge, AgentIdentity, and
WriteEvent. There is no core retriever agent. For Q&A over those
types only, spawn a short-lived child Task.

The child:

1. Resolves a seed (title or in-bundle path).
2. Runs `sbc_common.py pack --tiny --summary`.
3. Returns a Retrieval card.
4. Stops.

Parent skill: `skills/sbc-retrieve/SKILL.md`.
