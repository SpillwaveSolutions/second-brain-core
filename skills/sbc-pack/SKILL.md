---
name: sbc-pack
description: Build a bounded ContextPack from a Second Brain Core root concept (default 2 hops, 20 nodes).
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
