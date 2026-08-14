---
name: sbc-capture
description: Capture a Second Brain Core noun into the shared second brain via the deterministic write helper.
---

# sbc-capture

## Process

1. Identify the noun type from the allowed list (see README).
2. Collect title, status, author identity, and optional typed links.
3. Write with the helper — do not hand-author frontmatter unless the user insists:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sbc_common.py" write \
  --bundle knowledge \
  --type Concept \
  --folder concepts \
  --title "Example Concept" \
  --author "Grok Bot: Second Brain Core" \
  --tags "sbc"
```

4. Add typed links in a follow-up edit if needed (`rel` values from `docs/typed-edges.md`).
5. Validate.

Allowed types: Concept, ContextPack, TypedEdge, AgentIdentity, WriteEvent.
