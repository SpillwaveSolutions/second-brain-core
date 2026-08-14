---
name: sbc-doctor
description: Health-check the Second Brain Core catalogs and report empty indexes or missing schemas.
---

# sbc-doctor

1. Run validate.
2. List catalogs that have only `index.md` (empty).
3. Confirm every written `type` exists in `schemas/okf-concepts/`.
4. Report counts by type.
