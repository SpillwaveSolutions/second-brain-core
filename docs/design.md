# Design — Second Brain Core

## Problem

Session memory evaporates. This plugin gives one job function a typed, git-native vocabulary so agents and local jobs share a second brain.

## Rules

1. Git-native Markdown + YAML
2. Deterministic write boundary
3. Progressive disclosure via ContextPacks
4. No hard-coded real-world client names in samples
5. Multi-host plugin packaging (Claude Code, Grok Build, Codex, Agent Plugins 1.0, Grok Bot, LangChain Deep Agents)
6. Write isolation: read main, write in a session worktree, close as a PR. Type ownership says *what*. Isolation says *where*.

## Nouns

| `Concept` | Generic typed knowledge node |
| `ContextPack` | Bounded ranked typed-hop subgraph |
| `TypedEdge` | Directed relationship between concepts |
| `AgentIdentity` | Stable identity string for a writer agent |
| `WriteEvent` | Append-only record of a deterministic write |
