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
            "claude-code/threatiq",
            "--host",
            "claude-code",
            "--project",
            "threatiq",
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
            "grok-build/ui-app",
            "--host",
            "grok-build",
            "--project",
            "ui-app",
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
            "Threat Detector Note",
            "--author",
            "claude-code/threatiq",
        )
        assert r.returncode == 0, r.stdout + r.stderr
        r = run(
            "write",
            "--bundle",
            sb["bundle"],
            "--type",
            "Concept",
            "--title",
            "UI Layout Decision",
            "--author",
            "grok-build/ui-app",
        )
        assert r.returncode == 0, r.stdout + r.stderr

        # Isolation: each session only has its own new file
        assert (Path(sa["bundle"]) / "concepts" / "threat-detector-note.md").exists()
        assert not (Path(sa["bundle"]) / "concepts" / "ui-layout-decision.md").exists()
        assert (Path(sb["bundle"]) / "concepts" / "ui-layout-decision.md").exists()
        assert not (Path(sb["bundle"]) / "concepts" / "threat-detector-note.md").exists()

        ca = run_session("close", "--repo", str(repo), "--session", sa["session_id"], "--no-push", "--allow-local")
        assert ca.returncode == 0, ca.stdout + ca.stderr
        cb = run_session("close", "--repo", str(repo), "--session", sb["session_id"], "--no-push", "--allow-local")
        assert cb.returncode == 0, cb.stdout + cb.stderr

        # Merge both branches into main
        git(repo, "merge", "--no-ff", sa["branch"], "-m", "merge threatiq")
        git(repo, "merge", "--no-ff", sb["branch"], "-m", "merge ui")
        assert (knowledge / "concepts" / "threat-detector-note.md").exists()
        assert (knowledge / "concepts" / "ui-layout-decision.md").exists()


def test_sample_pack_walks():
    root = "Northstar Concept"
    r = run("pack", "--bundle", str(SAMPLE), "--root", root, "--hops", "2")
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(r.stdout)
    assert data.get("ok") is True
    assert len(data.get("nodes") or []) >= 3, data


if __name__ == "__main__":
    test_sample_validates()
    test_write_requires_author()
    test_init_and_write()
    test_isolation_two_sessions_do_not_clobber()
    test_sample_pack_walks()
    print("ok")
