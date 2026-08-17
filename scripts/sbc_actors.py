#!/usr/bin/env python3
"""Fleet actor registry and per-type write allowlist.

No operator registry → current behavior (any claimed identity).
If the operator file lists `actors`, session open fails closed on unknown.
`restrict` maps a type name to the actors who may write it. Pack-shipped
and operator files merge by intersection.

Paths only. A `remote` / `url` / `clone` field is a hard error.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

FORBIDDEN = ("remote", "url", "clone", "git_url", "ssh_url", "html_url")
COS_ACTOR = "grok-bot/executive-coordination"


def _home() -> Path:
    raw = (os.environ.get("SECOND_BRAIN_HOME") or "").strip()
    if raw:
        return Path(raw).expanduser()
    return Path.home() / ".second-brain"


def _reject_remotes(data: dict[str, Any], source: Path) -> None:
    bad = [k for k in FORBIDDEN if data.get(k)]
    if bad:
        raise SystemExit(
            json.dumps(
                {
                    "error": "actor registry must be paths only",
                    "forbidden": bad,
                    "registry": str(source),
                }
            )
        )
    for rec in data.get("actors") or []:
        if isinstance(rec, dict):
            rec_bad = [k for k in FORBIDDEN if rec.get(k)]
            if rec_bad:
                raise SystemExit(
                    json.dumps(
                        {
                            "error": "actor registry must be paths only",
                            "forbidden": rec_bad,
                            "actor": rec.get("actor"),
                            "registry": str(source),
                        }
                    )
                )


def _load(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(json.dumps({"error": "actor registry is not JSON", "registry": str(path), "detail": str(exc)}))
    if not isinstance(data, dict):
        raise SystemExit(json.dumps({"error": "actor registry root must be an object", "registry": str(path)}))
    _reject_remotes(data, path)
    return data


def operator_registry_candidates(start: Path | None = None) -> list[Path]:
    out: list[Path] = []
    env = (os.environ.get("SECOND_BRAIN_ACTORS") or "").strip()
    if env:
        out.append(Path(env).expanduser())
    out.append(_home() / "actors.json")
    here = (start or Path.cwd()).resolve()
    if here.is_file():
        here = here.parent
    for _ in range(8):
        out.append(here / "actors.json")
        out.append(here / ".second-brain" / "actors.json")
        if here.parent == here:
            break
        here = here.parent
    seen: set[str] = set()
    uniq: list[Path] = []
    for p in out:
        key = str(p)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(p)
    return uniq


def load_operator_registry(start: Path | None = None) -> tuple[dict[str, Any] | None, Path | None]:
    for path in operator_registry_candidates(start):
        data = _load(path)
        if data is not None:
            return data, path
    return None, None


def load_pack_registry(pack_root: Path | None = None) -> tuple[dict[str, Any] | None, Path | None]:
    if pack_root is None:
        pack_root = Path(__file__).resolve().parents[1]
    path = pack_root / "actors.json"
    data = _load(path)
    if data is None:
        return None, None
    return data, path


def registered_actors(start: Path | None = None) -> tuple[set[str] | None, Path | None]:
    """Return the membership set if the operator file lists actors, else None."""
    data, src = load_operator_registry(start)
    if data is None or src is None:
        return None, None
    rows = data.get("actors")
    if not isinstance(rows, list) or not rows:
        return None, src
    names = {str(r.get("actor") or "").strip() for r in rows if isinstance(r, dict)}
    names.discard("")
    if not names:
        return None, src
    return names, src


def require_registered_actor(actor: str, start: Path | None = None) -> None:
    names, src = registered_actors(start)
    if names is None:
        return
    if actor not in names:
        print(
            json.dumps(
                {
                    "error": "actor not in registry",
                    "actor": actor,
                    "registry": str(src),
                    "hint": "claim a registered actor or add it to the operator actors.json",
                }
            )
        )
        raise SystemExit(1)



def _restrict_map(data: dict[str, Any] | None) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    if not data:
        return out
    raw = data.get("restrict") or {}
    if not isinstance(raw, dict):
        return out
    for typ, actors in raw.items():
        if not isinstance(actors, list):
            continue
        allowed = {str(a).strip() for a in actors if str(a).strip()}
        if allowed:
            out[str(typ)] = allowed
    return out


def allowed_actors_for_type(
    typ: str,
    start: Path | None = None,
    pack_root: Path | None = None,
) -> set[str] | None:
    """Intersection of pack + operator restrict lists. None = unrestricted."""
    pack_data, _ = load_pack_registry(pack_root)
    op_data, _ = load_operator_registry(start)
    maps = [_restrict_map(pack_data), _restrict_map(op_data)]
    sets = [m[typ] for m in maps if typ in m]
    if not sets:
        return None
    allowed = sets[0]
    for extra in sets[1:]:
        allowed = allowed & extra
    return allowed


def require_type_allowed(
    actor: str,
    typ: str,
    start: Path | None = None,
    pack_root: Path | None = None,
) -> None:
    allowed = allowed_actors_for_type(typ, start=start, pack_root=pack_root)
    if allowed is None:
        return
    if actor not in allowed:
        print(
            json.dumps(
                {
                    "error": "actor may not write this type",
                    "actor": actor,
                    "type": typ,
                    "allowed": sorted(allowed),
                }
            )
        )
        raise SystemExit(1)



def cmd_check(args: argparse.Namespace) -> int:
    start = Path(args.start) if args.start else Path.cwd()
    if args.actor:
        require_registered_actor(args.actor, start=start)
    if args.actor and args.type:
        pack = Path(args.pack) if args.pack else None
        require_type_allowed(args.actor, args.type, start=start, pack_root=pack)
    names, src = registered_actors(start)
    print(
        json.dumps(
            {
                "ok": True,
                "actor": args.actor or "",
                "type": args.type or "",
                "registry": str(src) if src else "",
                "registered": sorted(names) if names is not None else None,
            }
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Fleet actor registry (fail-closed when present)")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Fail closed if actor/type is not allowed")
    c.add_argument("--actor", default="")
    c.add_argument("--type", default="")
    c.add_argument("--start", default="")
    c.add_argument("--pack", default="", help="Pack root that may ship actors.json restrict rules")
    args = p.parse_args(argv)
    return {"check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
