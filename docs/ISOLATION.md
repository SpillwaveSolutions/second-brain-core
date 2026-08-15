# Write isolation

One private second brain. Many agents. Many machines. Many project worktrees.

Type ownership says *what* you may write. Isolation says *where concurrent sessions do not collide*.

## Protocol

```
read  → origin/main (shared truth) + optional session overlay
write → brain/<actor>/<session-id> worktree only
close → commit, push to the checkout's existing remote, open PR
merge → human or green auto-merge on non-overlapping paths
```

```bash
python3 scripts/brain_session.py open \
  --repo . \
  --bundle knowledge \
  --actor grok-bot/content-media \
  --plugin content-media \
  --host grok-bot \
  --project ui-app

# JSON includes SECOND_BRAIN_ROOT for this session.
# All writes go there via *_common.py write --author ...

python3 scripts/brain_session.py close --repo . --session <id>
```

Branch name: `brain/<sanitized-actor>/<session-id>`

## Why not only flock-on-main

Flock serializes writers on one machine. It fails across machines, long thinking sessions, and cloud Grok Bots. Worktree + PR is the multi-agent protocol. Flock remains optional *inside* one worktree.

## Read freshness

- Shared truth: pack `main` after a fast-forward pull.
- Session overlay: also see your own unmerged writes (`--overlay` on pack).
- Do not pack other agents' open branches by default.

## Conflicts

OKF concepts are one file per path. Two agents editing the same concept will conflict. That is useful. Prefer creating new nodes. Catalog indexes are regenerated-friendly; treat them as derived when possible.

## Grok Bot (cloud)

No local worktree required. Same branch naming via GitHub. Or mount a box and give each bot session its own worktree. Do not solve isolation by making the knowledge repo public.

## Public pack surface

This document never names a private remote. `SECOND_BRAIN_ROOT` is a local path the human already has.
