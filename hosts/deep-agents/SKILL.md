---
name: deep-agents-second-brain-core
description: Bind LangChain Deep Agents to second-brain-core. Isolation, identity, deterministic writes.
---

# Deep Agents / Second Brain Core

Follow `docs/LANG_CHAIN_DEEP_AGENTS.md`.

1. Identity: `deep-agents/second-brain-core`
2. Load with `skills=["./path/to/second-brain-core/skills/"]` or SkillsMiddleware.
3. Open an isolation session (`scripts/brain_session.py open --host deep-agents`) unless `SECOND_BRAIN_ROOT` already points at a session worktree.
4. Pack 2 hops, then write owned types only via `scripts/sbc_common.py write --author`.
5. Close the session to PR. Report path + SHA.
6. Never document a private remote. Never write raw Markdown into the tree.
