#!/usr/bin/env python3
"""Pre-push secret scan for Agency CEO OS.

Fails (exit 1) if a file looks like it contains a real credential.
Placeholders are allowed: values containing your/example/test/placeholder,
and .env.example itself. Test files use fake keys (test-key) and are allowed.

Usage: python3 scripts/scan_secrets.py [root_dir]
Default root: the boss-ceo directory (parent of scripts/).
"""
import re
import sys
from pathlib import Path

PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(api[_-]?key|token|password)\s*=\s*['\"][^'\"]{16,}['\"]"),
]
ALLOW = re.compile(r"your|example|test|placeholder|change-?me|xxx", re.I)
SKIP_DIRS = {"__pycache__", ".git"}
SKIP_SUFFIXES = (".db", ".pyc")


def scan(root: Path) -> list[str]:
    hits = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix in SKIP_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for pat in PATTERNS:
                m = pat.search(line)
                if m and not ALLOW.search(m.group(0)):
                    hits.append(f"{path.relative_to(root)}:{lineno}: {pat.pattern}")
    return hits


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    hits = scan(root)
    if hits:
        print("SECRET SCAN FAILED — suspected credentials:")
        for h in hits:
            print("  " + h)
        return 1
    print(f"secret scan OK ({root}) — no suspected credentials")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
