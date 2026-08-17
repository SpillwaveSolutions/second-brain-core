# Write isolation

One private second brain. Many agents. Many machines. Many project worktrees.

Type ownership says *what* a pack may write. Isolation says *where concurrent sessions do not collide*. A fleet actor registry (when present) says *who* may open a session. A type allowlist (when present) says *which actor* may write a restricted type.

## Actor registry

If the operator provides `actors.json` (`SECOND_BRAIN_ACTORS`, `$SECOND_BRAIN_HOME/actors.json`, or `actors.json` walking up from the repo) **and** that file lists `actors`, `brain_session.py open` fails closed on an unknown actor.

No registry file (or a restrict-only file) keeps the old behavior: any claimed identity may open.

See `actors.sample.json`. Paths only. Never put a remote in the registry.

## Type allowlist

`restrict` maps a type to the actors who may write it. Pack-shipped `actors.json` and the operator file merge by **intersection**. First required rule (executive-coordination): `DailyDigest` / `WeeklyDigest` are CoS-only (`grok-bot/executive-coordination`). A CTO actor on the same pack is denied.

## Pack roots are not access control

`--root /clients/<slug>.md` and “pack from this client” are **ContextPack scope**. They do not stop a write to another client’s node. Four account-management actors with different default roots can still write each other’s files until a later client-scope check exists. Isolation prevents branch clobber, not same-path overlap. Review still has to catch two sessions writing the same concept.

## Protocol

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
  --project northstar-console

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


## Canonical helper

`scripts/brain_session.py` in this repository is the **canonical** isolation helper.

Foundation packs (okf-plugin, PKC, SAC, DEKC, AGER, WikiTicket) vendor a copy. Job packs already ship the same script. Do not fork the protocol:

- branch: `brain/<actor>/<session-id>`
- read `main`; write only in the session worktree
- close via commit + PR against the checkout's existing remote
- never force-push; never invent a remote URL

If the helper changes, bump this pack and re-vendor.
