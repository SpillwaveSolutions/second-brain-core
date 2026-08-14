---
name: sbc-init
description: Scaffold the Second Brain Core catalogs in a shared second-brain bundle.
---

# sbc-init

Create the catalogs this plugin owns inside a shared knowledge root.

## Process

1. Confirm target (default `knowledge/`).
2. Run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sbc_common.py" init-bundle \
  --bundle knowledge \
  --title "Second Brain Core" \
  --catalogs "concepts,packs"
```

3. Point the user at `sample-knowledge/` for a fictional demo.

## Done when

- `knowledge/index.md` exists
- Each owned catalog has `index.md`
