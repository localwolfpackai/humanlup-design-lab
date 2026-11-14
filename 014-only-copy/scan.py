#!/usr/bin/env python3
"""Only Copy scanner. Reads a folder of Git repos and prints one JSON document.

    python3 scan.py                      scans ~/Projects, prints to the terminal
    python3 scan.py --root ~/Code        scans another folder
    python3 scan.py --output scan.json   writes a file instead

It only reads. It runs no command that changes a repo, fetches nothing,
opens nothing. Paste the JSON into the Only Copy page ("Load scan").

What it fixes from repo_inventory_dashboard.py:
  - unpushed counts every local commit that is on no remote, on any branch.
    The old script compared the current branch with its upstream and printed 0
    when the branch had no upstream, so a branch that was never pushed read as clean.
  - last commit is a real date, not "5 months ago".
  - --root and --output exist. Nothing opens a browser.
"""
import argparse, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

SKIP = {"node_modules", ".next", ".venv", "venv", "__pycache__", "dist", ".git"}


def git(repo, *args):
    try:
        r = subprocess.run(["git", "-C", str(repo), *args],
                           capture_output=True, text=True, timeout=15)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def find_repos(root):
    """Walk by hand so skipped folders are never entered."""
    stack = [root]
    while stack:
        d = stack.pop()
        try:
            kids = sorted(p for p in d.iterdir() if p.is_dir() and not p.is_symlink())
        except OSError:
            continue
        if (d / ".git").is_dir():
            yield d
        stack.extend(k for k in kids if k.name not in SKIP)


def kind(repo):
    if (repo / "package.json").exists():
        return "Web / Node project"
    if (repo / "pyproject.toml").exists() or (repo / "requirements.txt").exists():
        return "Python project"
    if (repo / "index.html").exists():
        return "Static website"
    if (repo / "README.md").exists():
        return "Docs / mixed"
    return "Unknown"


def read(repo, root):
    has_commits = bool(git(repo, "rev-list", "-n", "1", "--all"))
    dirty = [x for x in git(repo, "status", "--porcelain").splitlines() if x.strip()]
    unpushed = git(repo, "rev-list", "--count", "--branches", "--not", "--remotes")
    last = git(repo, "log", "-1", "--format=%h%x09%cI%x09%s").split("\t", 2)
    rel = repo.relative_to(root).as_posix()
    return {
        "rel": rel if rel else ".",
        "type": kind(repo),
        "branch": git(repo, "branch", "--show-current") or "(detached)",
        "remote": git(repo, "remote", "get-url", "origin"),
        "deploy": (repo / ".vercel" / "project.json").exists(),
        "dirty": len(dirty),
        "unpushed": int(unpushed or 0),
        "commits": has_commits,
        "hash": last[0] if len(last) == 3 else "",
        "date": last[1] if len(last) == 3 else "",
        "subject": last[2] if len(last) == 3 else "",
    }


def main():
    ap = argparse.ArgumentParser(description="Print a JSON inventory of the Git repos in a folder.")
    ap.add_argument("--root", default=str(Path.home() / "Projects"))
    ap.add_argument("--output", default="")
    a = ap.parse_args()
    root = Path(a.root).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"Not a folder: {root}")
    repos = sorted((read(r, root) for r in find_repos(root)), key=lambda r: r["rel"])
    home = str(Path.home())
    shown = str(root)
    if shown.startswith(home):
        shown = "~" + shown[len(home):]
    doc = {"onlyCopy": 2, "root": shown,
           "scanned": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "repos": repos}
    text = json.dumps(doc, indent=1, ensure_ascii=False)
    if a.output:
        Path(a.output).expanduser().write_text(text + "\n")
        print(f"{len(repos)} repos written to {a.output}", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
