---
name: sbc-retrieve
description: Spawn a retrieval sub-agent for second-brain Q&A so search and pack stay off the parent context.
---

# sbc-retrieve

Parent-facing. Read [docs/RETRIEVAL.md](../../docs/RETRIEVAL.md) first.

For Q&A, or "what does the brain say", spawn a child. Do not run
`sbc_common.py pack`, `pkc_pack`, `sac_pack`, `dekc_pack`, or
`rkc_pack` in this parent turn. Progressive disclosure still lands
the pack in the parent if you run it here.

Do not invent `rel` values. See `docs/typed-edges.md`.

## Foundation retrievers

Spawn the pack that owns the nouns. Each child returns a Retrieval
card only. Fan out in parallel when the question crosses planes.

| Plane | Spawn |
|-------|-------|
| Project memory (Feature, DecisionRecord, Meeting, Experiment) | PKC `knowledge-retriever` (`/pkc-retrieve`) |
| Architecture (Service, ApiContract, Runtime, blast radius) | SAC `architecture-retriever` (`/sac-retrieve`) |
| Data platform (Table, Metric, LineagePath, DataProduct) | DEKC `data-retriever` (`/dekc-retrieve`) |
| Research (ResearchQuestion, Finding, Claim, Evidence) | RKC `research-retriever` (`/research-retrieve`) |

Do not move those agents into core.

## Core-owned concepts

For Concept, ContextPack, TypedEdge, AgentIdentity, or WriteEvent
only, spawn a short-lived child Task (host equivalent). The child
runs:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sbc_common.py" pack \
  --bundle "${SECOND_BRAIN_ROOT:-knowledge}" \
  --root "/concepts/example.md" \
  --tiny --summary
```

`--tiny` is 1 hop / 8 nodes. `--summary` is compact markdown, bodies
off, fail-closed budget. The child fills the Retrieval card from
that stdout and stops.

## Job-function packs without a retriever

Same temporary path: short-lived child Task, `sbc_common.py pack --tiny --summary`,
same card. Add a pack-local retriever later if the pack needs its own
scoring.

## Consume

Keep only the card. Answer from it. If Next is `deepen` or
`try-alt-seed`, spawn again. Do not paste hit lists or pack bodies
into this context.
