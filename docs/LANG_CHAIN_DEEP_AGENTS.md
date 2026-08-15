# LangChain Deep Agents / Deep Agents Code

How to use this Spillwave ContentPack (or foundation plugin) with LangChain Deep Agents and Deep Agents Code (`dcode`).

This package already follows the open **Agent Skills** layout (`skills/*/SKILL.md`). Deep Agents loads the same format.

## Privacy and knowledge root

The institutional second brain is a **local or private** OKF tree the human already owns.

- Point Deep Agents at that tree with `SECOND_BRAIN_ROOT` or by running from a working directory that contains `knowledge/`.
- Never hard-code a remote URL or clone command in agent configuration.
- Public samples use only fictional Northstar / Lumenfield data.

## Install / discovery options

### A. Filesystem skills source (recommended for control)

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

# After cloning or installing the pack:
#   git clone https://github.com/SpillwaveSolutions/second-brain-core.git
#   # or: npx skills add SpillwaveSolutions/second-brain-core

agent = create_deep_agent(
    model="...",
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    skills=["./path/to/second-brain-core/skills/"],  # or absolute path
    # system_prompt can reference SECOND_BRAIN_ROOT and identity rules
)
```

Or with SkillsMiddleware:

```python
from deepagents.middleware import SkillsMiddleware

SkillsMiddleware(
    backend=backend,
    sources=["/skills/", "/path/to/pack/skills/"],
)
```

### B. npx skills / marketplace style

```bash
npx skills add SpillwaveSolutions/second-brain-core --skill '*' --yes
# optionally --agent or global flags per your Deep Agents / dcode setup
```

Deep Agents Code (`dcode`) may also accept marketplace or local plugin directories via its `/plugins` manager when the host supports Agent Skills or Agent Plugins packages.

### C. Agent Plugins 1.0 portable package

This repo ships a root `plugin.json` conforming to https://agent-plugins.org. Any Deep Agents host that reads Agent Plugins can load the same directory.

## Deterministic write boundary

Deep Agents must **not** write free-form Markdown into the knowledge tree.

1. Claim identity for the process:

   ```bash
   export SECOND_BRAIN_IDENTITY="deep-agents/<your-role>"
   # or pass --author on every call
   ```

2. Use the pack scripts:

   ```bash
   python3 scripts/sbc_common.py write \
     --bundle "${SECOND_BRAIN_ROOT:-knowledge}" \
     --type Concept \
     --folder concepts \
     --title "..." \
     --author "${SECOND_BRAIN_IDENTITY}"
   ```

3. Prefer a ContextPack (2 hops) before answering or writing:

   ```bash
   python3 scripts/sbc_common.py pack <root-concept.md> --bundle knowledge --hops 2
   # or the pack skill / script shipped with this plugin
   ```

Wrap the scripts as tools or shell commands inside the Deep Agent so the model proposes and the scripts commit.

## Progressive disclosure

- Startup: only skill frontmatter (name + description) is visible.
- On need: load full SKILL.md.
- For institutional knowledge: always pack first; do not dump the entire tree into context.

## Identity and multi-writer safety

- Actor string pattern: `deep-agents/<role>` or host-specific.
- Emit `AgentIdentity` and `WriteEvent` nodes when the pack supports them (this core does).
- Concurrent writers: serialize via the pack's brain-write / flock helper if present. Fail closed on conflict. Never force-push.

## Three memory planes

| Plane | Where it lives |
|-------|----------------|
| Procedural | Skills, harness rules, this file |
| Working | Current Deep Agents turn + packed context |
| Institutional | The OKF Markdown tree under SECOND_BRAIN_ROOT |

Keep identity/preferences out of the institutional tree when they belong in agent profile.

## Related

- Agent Skills spec (SKILL.md)
- Agent Plugins 1.0 (plugin.json + skills/)
- This pack's README and AGENTS.md for type ownership
- Companion foundation: okf-plugin, project-knowledge-capture, wiki_ticket_sdd
- See also `docs/GROK_BOT.md` for the parallel Grok Bot binding
