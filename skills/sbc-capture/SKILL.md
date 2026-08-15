---
name: sbc-capture
description: Capture a Second Brain Core noun into the shared second brain via the deterministic write helper.
---

# sbc-capture

## Process

0. If more than one agent writes the shared brain, open an isolation session (`sbc-session`) and export `SECOND_BRAIN_ROOT`.
   Claim identity `grok-bot/second-brain-core` (or `deep-agents/second-brain-core` on Deep Agents).
1. Identify the noun type from the allowed list (see README).
2. Collect title, status, author identity, and optional typed links.
3. Write with the helper — do not hand-author frontmatter unless the user insists:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sbc_common.py" write \
  --bundle "${SECOND_BRAIN_ROOT:-knowledge}" \
  --type Concept \
  --folder concepts \
  --title "Example Concept" \
  --author "${SECOND_BRAIN_IDENTITY:?claim an identity first}" \
  --tags "sbc"
```

4. Add typed links in a follow-up edit if needed (`rel` values from `docs/typed-edges.md`).
5. Validate.

Allowed types: Concept, ContextPack, TypedEdge, AgentIdentity, WriteEvent.
