# Design — Second Brain Core

## Problem

Session memory evaporates. This plugin gives one job function a typed, git-native vocabulary so agents and local jobs share a second brain.

## Rules

1. Git-native Markdown + YAML
2. Deterministic write boundary
3. Progressive disclosure via ContextPacks
4. No hard-coded real-world client names in samples
5. Dual-host plugin packaging

## Nouns

| `Concept` | Generic typed knowledge node |
| `ContextPack` | Bounded ranked typed-hop subgraph |
| `TypedEdge` | Directed relationship between concepts |
| `AgentIdentity` | Stable identity string for a writer agent |
| `WriteEvent` | Append-only record of a deterministic write |
