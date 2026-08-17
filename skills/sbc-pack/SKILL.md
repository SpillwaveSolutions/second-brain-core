---
name: sbc-pack
description: Build a bounded ContextPack from a Second Brain Core root concept (default 2 hops, 20 nodes, 1/4 window token budget).
---

# sbc-pack

## Process

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sbc_common.py" pack \
  --bundle knowledge \
  --root "/concepts/example.md" \
  --hops 2 \
  --max-nodes 20
```

Use `--hops 1` for a tiny pack. Outbound edges only. Do not dump the whole tree.

**Token budget.** Default is 1/4 of `SECOND_BRAIN_WINDOW_TOKENS` (128000 → 32000).
Override with `--max-tokens` or `SECOND_BRAIN_PACK_MAX_TOKENS`. If the rendered
pack exceeds the budget, the script exits 1 and writes nothing. `--max-nodes`
clips the walk; it is not a token budget.

**Bodies off** unless that node is the pack root. Neighbors are title + type +
path + frontmatter description only.
