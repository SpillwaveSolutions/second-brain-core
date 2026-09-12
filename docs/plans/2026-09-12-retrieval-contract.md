---
date: 2026-09-12
slug: retrieval-contract
title: Query-time retrieval contract
epic: 01M2BB3AEDASWTR7CKAXZ6D431
items: [01M2BB3AEMPXGZG2S1CVG8FA23, 01M2BB3AEMGVPV58P854CMFF36, 01M2BB3AEMY2XA7HJFZKZ5E2X6, 01M2BB3AEMH3MGG9M08WWXP71B, 01M2BB3AEMMWQXGCVBBH4PXJ38]
git_hash: "f81f36ddfe647968943d87985ab914b7d6e04f65"
---

# Query-time retrieval contract (0.3.8)

Generalize the retrieval isolation story that PKC, SAC, DEKC, and RKC
already ship. Core documents the parent spawn rule and the shared
Retrieval card. Pack-specific retriever agents stay in those packs.

Scripts remain the deterministic engine. No LLM inside pack or search.
`--summary` and `--tiny` land on `sbc_common.py pack` so a short-lived
child Task can pack core-owned concepts without dumping bodies into
the parent.

## Tasks

- [ ] (P1) Write docs/RETRIEVAL.md
  Shared query-time contract: why pack-in-parent is not isolation, spawn
  rule, card fields, fan-out table, child CLI, job-pack fallback.
- [ ] (P1) Add sbc-retrieve skill and command shim
  Parent-facing skill points at RETRIEVAL.md, lists the four foundation
  retrievers, and tells the parent to spawn a child Task for core types.
- [ ] (P1) Add --summary and --tiny on sbc pack
  Compact card-friendly stdout, bodies off, fail-closed token budget,
  tiny clip of 1 hop / 8 nodes. Tests cover the new flags.
- [ ] (P2) Wire docs and bump 0.3.8
  AGENTS, ONBOARDING, GROK_BOT, CHANGELOG, README, host skills, version
  stamps. Fiction samples only. No private remotes.
- [ ] (P2) Run tests and open the PR
  Tests must pass. Branch and draft PR against main.
