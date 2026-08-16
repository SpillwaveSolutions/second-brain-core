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


if __name__ == "__main__":
    test_sample_validates()
    test_write_requires_author()
    test_init_and_write()
    test_isolation_two_sessions_do_not_clobber()
    test_sample_pack_walks()
    test_hooks_json_is_fail_closed_post_tool_use()
    test_hook_valid_bundle_exits_zero()
    test_hook_invalid_bundle_exits_nonzero()
    test_hook_not_a_bundle_is_silent_ok()
    test_hook_apply_patch_payload()
    print("ok")
