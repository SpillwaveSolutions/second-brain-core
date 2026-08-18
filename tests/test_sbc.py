#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "sbc_common.py"
SESSION = ROOT / "scripts" / "brain_session.py"
HOOK = ROOT / "scripts" / "sbc-hook-validate.sh"
HOOKS_JSON = ROOT / "hooks" / "hooks.json"
SAMPLE = ROOT / "sample-knowledge"


def run(*args, env=None):
    e = os.environ.copy()
    if env:
        e.update(env)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=e,
    )


def run_session(*args, cwd=None):
    return subprocess.run(
        [sys.executable, str(SESSION), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def run_hook(*args, stdin=None, env=None):
    e = os.environ.copy()
    e.pop("SECOND_BRAIN_ROOT", None)
    if env:
        e.update(env)
    return subprocess.run(
        ["bash", str(HOOK), *args],
        input=stdin,
        capture_output=True,
        text=True,
        env=e,
    )


def git(cwd, *args):
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def test_sample_validates():
    r = run("validate", "--bundle", str(SAMPLE))
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(r.stdout)
    assert data["ok"] is True
    assert data["concepts"] >= 1


def test_write_requires_author():
    with tempfile.TemporaryDirectory() as td:
        bundle = Path(td) / "knowledge"
        run("init-bundle", "--bundle", str(bundle), "--title", "Test", "--catalogs", "concepts")
        r = run(
            "write",
            "--bundle",
            str(bundle),
            "--type",
            "Concept",
            "--folder",
            "concepts",
            "--title",
            "No Author",
        )
        assert r.returncode != 0
        assert "identity" in r.stdout.lower() or "identity" in r.stderr.lower()


def test_init_and_write():
    with tempfile.TemporaryDirectory() as td:
        bundle = Path(td) / "knowledge"
        r = run("init-bundle", "--bundle", str(bundle), "--title", "Test", "--catalogs", "concepts")
        assert r.returncode == 0, r.stdout + r.stderr
        r = run(
            "write",
            "--bundle",
            str(bundle),
            "--type",
            "Concept",
            "--folder",
            "concepts",
            "--title",
            "Hello World",
            "--author",
            "grok-bot/second-brain-core",
        )
        assert r.returncode == 0, r.stdout + r.stderr
        data = json.loads(r.stdout)
        assert data["author"] == "grok-bot/second-brain-core"
        assert data["event"]
        r = run("validate", "--bundle", str(bundle))
        assert r.returncode == 0, r.stdout + r.stderr


def test_isolation_two_sessions_do_not_clobber():
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "brain"
        repo.mkdir()
        git(repo, "init", "-b", "main")
        git(repo, "config", "user.email", "test@example.com")
        git(repo, "config", "user.name", "tester")
        knowledge = repo / "knowledge"
        r = run("init-bundle", "--bundle", str(knowledge), "--title", "Shared", "--catalogs", "concepts")
        assert r.returncode == 0, r.stdout + r.stderr
        git(repo, "add", ".")
        git(repo, "commit", "-m", "seed")

        a = run_session(
            "open",
            "--repo",
            str(repo),
            "--bundle",
            "knowledge",
            "--actor",
            "claude-code/lumenfield-detector",
            "--host",
            "claude-code",
            "--project",
            "lumenfield-detector",
        )
        assert a.returncode == 0, a.stdout + a.stderr
        sa = json.loads(a.stdout)
        b = run_session(
            "open",
            "--repo",
            str(repo),
            "--bundle",
            "knowledge",
            "--actor",
            "grok-bot/northstar-console",
            "--host",
            "grok-bot",
            "--project",
            "northstar-console",
        )
        assert b.returncode == 0, b.stdout + b.stderr
        sb = json.loads(b.stdout)
        assert sa["branch"] != sb["branch"]
        assert sa["worktree"] != sb["worktree"]

        r = run(
            "write",
            "--bundle",
            sa["bundle"],
            "--type",
            "Concept",
            "--title",
            "Lumenfield Detector Note",
            "--author",
            "claude-code/lumenfield-detector",
        )
        assert r.returncode == 0, r.stdout + r.stderr
        r = run(
            "write",
            "--bundle",
            sb["bundle"],
            "--type",
            "Concept",
            "--title",
            "Northstar Console Layout",
            "--author",
            "grok-bot/northstar-console",
        )
        assert r.returncode == 0, r.stdout + r.stderr

        # Isolation: each session only has its own new file
        assert (Path(sa["bundle"]) / "concepts" / "lumenfield-detector-note.md").exists()
        assert not (Path(sa["bundle"]) / "concepts" / "northstar-console-layout.md").exists()
        assert (Path(sb["bundle"]) / "concepts" / "northstar-console-layout.md").exists()
        assert not (Path(sb["bundle"]) / "concepts" / "lumenfield-detector-note.md").exists()

        ca = run_session("close", "--repo", str(repo), "--session", sa["session_id"], "--no-push", "--allow-local")
        assert ca.returncode == 0, ca.stdout + ca.stderr
        cb = run_session("close", "--repo", str(repo), "--session", sb["session_id"], "--no-push", "--allow-local")
        assert cb.returncode == 0, cb.stdout + cb.stderr

        # Merge both branches into main
        git(repo, "merge", "--no-ff", sa["branch"], "-m", "merge lumenfield-detector")
        git(repo, "merge", "--no-ff", sb["branch"], "-m", "merge northstar-console")
        assert (knowledge / "concepts" / "lumenfield-detector-note.md").exists()
        assert (knowledge / "concepts" / "northstar-console-layout.md").exists()


def test_sample_pack_walks():
    root = "Northstar Concept"
    r = run("pack", "--bundle", str(SAMPLE), "--root", root, "--hops", "2")
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(r.stdout)
    assert data.get("ok") is True
    assert len(data.get("nodes") or []) >= 3, data
    assert data.get("tokens", 0) > 0
    assert data.get("budget") == 32000
    assert data.get("window") == 128000
    text = Path(data["path"]).read_text(encoding="utf-8")
    assert "Tokens:" in text
    # Neighbor bodies stay off. Sample identity/contextpack notes must not leak.
    assert "Fictional generic typed knowledge node" in text  # root body
    assert "Fictional writer identity" not in text
    assert "Fictional bounded ranked typed-hop subgraph" not in text


def test_pack_default_budget_is_quarter_window():
    with tempfile.TemporaryDirectory() as td:
        bundle = Path(td) / "knowledge"
        run("init-bundle", "--bundle", str(bundle), "--title", "Budget", "--catalogs", "concepts")
        run(
            "write",
            "--bundle",
            str(bundle),
            "--type",
            "Concept",
            "--title",
            "Northstar Root",
            "--author",
            "grok-bot/northstar-console",
            "--body",
            "# Northstar Root\n\nShort root body.\n",
        )
        r = run(
            "pack",
            "--bundle",
            str(bundle),
            "--root",
            "Northstar Root",
            env={"SECOND_BRAIN_WINDOW_TOKENS": "400"},
        )
        assert r.returncode == 0, r.stdout + r.stderr
        data = json.loads(r.stdout)
        assert data["window"] == 400
        assert data["budget"] == 100
        assert data["tokens"] <= 100


def test_pack_exceeds_token_budget_fails_closed():
    with tempfile.TemporaryDirectory() as td:
        bundle = Path(td) / "knowledge"
        run("init-bundle", "--bundle", str(bundle), "--title", "Over", "--catalogs", "concepts")
        fat = "# Fat Root\n\n" + ("word " * 400)
        run(
            "write",
            "--bundle",
            str(bundle),
            "--type",
            "Concept",
            "--title",
            "Fat Root",
            "--author",
            "claude-code/lumenfield-detector",
            "--body",
            fat,
        )
        out = bundle / "packs" / "should-not-exist.md"
        r = run(
            "pack",
            "--bundle",
            str(bundle),
            "--root",
            "Fat Root",
            "--max-nodes",
            "1",
            "--max-tokens",
            "20",
            "--out",
            str(out),
        )
        assert r.returncode != 0, r.stdout + r.stderr
        data = json.loads(r.stdout)
        assert data["error"] == "pack exceeds token budget"
        assert data["tokens"] > data["budget"]
        assert data["budget"] == 20
        assert not out.exists()


def test_pack_bodies_off_unless_root():
    with tempfile.TemporaryDirectory() as td:
        bundle = Path(td) / "knowledge"
        run("init-bundle", "--bundle", str(bundle), "--title", "Bodies", "--catalogs", "concepts")
        run(
            "write",
            "--bundle",
            str(bundle),
            "--type",
            "Concept",
            "--title",
            "Lumenfield Root",
            "--author",
            "claude-code/lumenfield-detector",
            "--body",
            "# Lumenfield Root\n\nROOT_BODY_MARKER secret-of-root\n",
        )
        neighbor = bundle / "concepts" / "neighbor.md"
        neighbor.write_text(
            "---\n"
            "type: Concept\n"
            "title: Neighbor Note\n"
            "description: neighbor-frontmatter-only\n"
            "links:\n"
            "  - target: /concepts/lumenfield-root.md\n"
            "    rel: related_to\n"
            "---\n\n# Neighbor\n\nNEIGHBOR_BODY_MARKER must-not-pack\n",
            encoding="utf-8",
        )
        # Link root -> neighbor so hops=1 includes it
        root = bundle / "concepts" / "lumenfield-root.md"
        text = root.read_text(encoding="utf-8")
        text = text.replace(
            "---\n\n",
            "links:\n  - target: /concepts/neighbor.md\n    rel: related_to\n---\n\n",
            1,
        )
        root.write_text(text, encoding="utf-8")
        r = run("pack", "--bundle", str(bundle), "--root", "Lumenfield Root", "--hops", "1")
        assert r.returncode == 0, r.stdout + r.stderr
        data = json.loads(r.stdout)
        packed = Path(data["path"]).read_text(encoding="utf-8")
        assert "ROOT_BODY_MARKER" in packed
        assert "NEIGHBOR_BODY_MARKER" not in packed
        assert "neighbor-frontmatter-only" in packed
        assert "Neighbor Note" in packed



def test_hooks_json_is_fail_closed_post_tool_use():
    data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    assert "SessionStart" not in data.get("hooks", {}), data
    post = data["hooks"]["PostToolUse"]
    matchers = " ".join(entry.get("matcher", "") for entry in post)
    assert "apply_patch" in matchers
    assert "Write" in matchers
    assert "Edit" in matchers
    commands = []
    for entry in post:
        for hook in entry.get("hooks", []):
            commands.append(hook.get("command", ""))
    assert any("sbc-hook-validate.sh" in c for c in commands), commands


def test_hook_valid_bundle_exits_zero():
    r = run_hook(str(SAMPLE / "concepts" / "northstar-concept.md"))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "validating bundle at" in r.stdout


def test_hook_invalid_bundle_exits_nonzero():
    with tempfile.TemporaryDirectory() as td:
        bundle = Path(td) / "knowledge"
        run("init-bundle", "--bundle", str(bundle), "--title", "Broken", "--catalogs", "concepts")
        dest = bundle / "concepts" / "broken.md"
        dest.write_text(
            "---\n"
            "type: Concept\n"
            "title: Broken\n"
            "links:\n"
            "  - target: /concepts/does-not-exist.md\n"
            "    rel: related_to\n"
            "---\n\n# Broken\n",
            encoding="utf-8",
        )
        r = run_hook(str(dest))
        assert r.returncode != 0, r.stdout + r.stderr
        assert "validating bundle at" in r.stdout


def test_hook_not_a_bundle_is_silent_ok():
    with tempfile.TemporaryDirectory() as td:
        notes = Path(td) / "notes.md"
        notes.write_text("# just notes\n", encoding="utf-8")
        r = run_hook(str(notes))
        assert r.returncode == 0, r.stdout + r.stderr
        assert r.stdout == ""
        assert r.stderr == ""


def test_hook_apply_patch_payload():
    payload = json.dumps(
        {
            "tool_name": "apply_patch",
            "tool_input": {
                "input": (
                    "*** Begin Patch\n"
                    f"*** Update File: {SAMPLE / 'concepts' / 'northstar-concept.md'}\n"
                    "*** End Patch\n"
                )
            },
        }
    )
    r = run_hook(stdin=payload)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "validating bundle at" in r.stdout


def test_host_manifest_versions_match():
    root_ver = json.loads((ROOT / "plugin.json").read_text())["version"]
    found = {"plugin.json": root_ver}
    for rel, path in (
        (".cursor-plugin/plugin.json", ("version",)),
        (".claude-plugin/plugin.json", ("version",)),
        (".claude-plugin/marketplace.json", ("plugins", 0, "version")),
        (".grok-plugin/marketplace.json", ("plugins", 0, "version")),
        ("marketplace.json", ("plugins", 0, "version")),
        ("package.json", ("version",)),
    ):
        f = ROOT / rel
        if not f.exists():
            continue
        node = json.loads(f.read_text())
        for key in path:
            node = node[key]
        found[rel] = node
    assert len(set(found.values())) == 1, f"version drift: {found}"


def _write_registry(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_session_open_without_registry_still_works():
    tmp = Path(tempfile.mkdtemp())
    repo = tmp / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True, capture_output=True)
    (repo / "knowledge").mkdir()
    (repo / "knowledge" / "index.md").write_text("# k\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)
    env = os.environ.copy()
    env.pop("SECOND_BRAIN_ACTORS", None)
    env["SECOND_BRAIN_HOME"] = str(tmp / "empty-home")
    r = subprocess.run(
        [
            sys.executable,
            str(SESSION),
            "open",
            "--repo",
            str(repo),
            "--bundle",
            "knowledge",
            "--actor",
            "grok-bot/northstar-console",
            "--plugin",
            "second-brain-core",
            "--host",
            "test",
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert json.loads(r.stdout)["ok"] is True


def test_session_open_unknown_actor_fails_closed():
    tmp = Path(tempfile.mkdtemp())
    repo = tmp / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True, capture_output=True)
    (repo / "knowledge").mkdir()
    (repo / "knowledge" / "index.md").write_text("# k\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True, capture_output=True)
    registry = _write_registry(
        tmp / "actors.json",
        {"version": 1, "actors": [{"actor": "grok-bot/executive-coordination"}]},
    )
    env = os.environ.copy()
    env["SECOND_BRAIN_ACTORS"] = str(registry)
    env["SECOND_BRAIN_HOME"] = str(tmp / "empty-home")
    r = subprocess.run(
        [
            sys.executable,
            str(SESSION),
            "open",
            "--repo",
            str(repo),
            "--bundle",
            "knowledge",
            "--actor",
            "grok-bot/imposter",
            "--plugin",
            "executive-coordination",
        ],
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode != 0, r.stdout
    err = json.loads(r.stdout or r.stderr)
    assert err["error"] == "actor not in registry"


def test_dailydigest_is_cos_only():
    sys.path.insert(0, str(ROOT / "scripts"))
    import sbc_actors

    tmp = Path(tempfile.mkdtemp())
    registry = _write_registry(
        tmp / "actors.json",
        {
            "version": 1,
            "actors": [
                {"actor": "grok-bot/executive-coordination"},
                {"actor": "grok-bot/spillwave-cto"},
            ],
            "restrict": {
                "DailyDigest": ["grok-bot/executive-coordination"],
                "WeeklyDigest": ["grok-bot/executive-coordination"],
            },
        },
    )
    os.environ["SECOND_BRAIN_ACTORS"] = str(registry)
    os.environ["SECOND_BRAIN_HOME"] = str(tmp / "empty-home")
    try:
        sbc_actors.require_type_allowed(
            "grok-bot/executive-coordination", "DailyDigest", start=tmp
        )
        sbc_actors.require_type_allowed("grok-bot/spillwave-cto", "Decision", start=tmp)
        try:
            sbc_actors.require_type_allowed(
                "grok-bot/spillwave-cto", "DailyDigest", start=tmp
            )
            raise AssertionError("CTO DailyDigest must fail closed")
        except SystemExit as exc:
            assert exc.code == 1
    finally:
        os.environ.pop("SECOND_BRAIN_ACTORS", None)
        os.environ.pop("SECOND_BRAIN_HOME", None)


if __name__ == "__main__":
    test_sample_validates()
    test_write_requires_author()
    test_init_and_write()
    test_isolation_two_sessions_do_not_clobber()
    test_sample_pack_walks()
    test_pack_default_budget_is_quarter_window()
    test_pack_exceeds_token_budget_fails_closed()
    test_pack_bodies_off_unless_root()
    test_hooks_json_is_fail_closed_post_tool_use()
    test_hook_valid_bundle_exits_zero()
    test_hook_invalid_bundle_exits_nonzero()
    test_hook_not_a_bundle_is_silent_ok()
    test_hook_apply_patch_payload()
    test_host_manifest_versions_match()
    test_session_open_without_registry_still_works()
    test_session_open_unknown_actor_fails_closed()
    test_dailydigest_is_cos_only()
    print("ok")
