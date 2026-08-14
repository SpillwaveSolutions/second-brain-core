---
name: sbc-validate
description: Validate Second Brain Core concepts: required fields, types, and in-bundle links.
---

# sbc-validate

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sbc_common.py" validate --bundle knowledge
```

Fail on missing `type`/`title` or broken absolute links.
