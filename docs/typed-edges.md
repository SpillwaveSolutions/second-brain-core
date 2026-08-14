# Typed edges — Second Brain Core

Direction matters. Packs follow outbound edges by default.

| `rel` | Meaning |
|-------|---------|
| `related_to` | Soft association |
| `depends_on` | Hard dependency |
| `owned_by` | Accountability |
| `originates_from` | Provenance |
| `supersedes` | Replaces older concept |
| `documents` | Narrative about target |

Unknown `rel` values are treated as `info` by validation. Do not invent new names in this plugin.
