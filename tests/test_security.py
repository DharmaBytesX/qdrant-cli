"""Verify no secrets (API keys, tokens) are hardcoded in source files."""

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src"

SECRET_PATTERNS = [
    re.compile(r"sk-or-v[0-9a-f-]+", re.I),
    re.compile(r"sk-[a-zA-Z0-9]{20,}", re.I),
    re.compile(r"api[_-]?key\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]", re.I),
    re.compile(r"api[_-]?secret\s*=\s*['\"][a-zA-Z0-9_\-]{16,}['\"]", re.I),
    re.compile(r"token\s*=\s*['\"][a-zA-Z0-9_\-.]{20,}['\"]", re.I),
    re.compile(r"password\s*=\s*['\"][a-zA-Z0-9_\-!@#$%^&*()+]{8,}['\"]", re.I),
]


def _find_secrets(path: Path) -> list[tuple[Path, int, str]]:
    results: list[tuple[Path, int, str]] = []
    for f in path.rglob("*.py"):
        if ".venv" in str(f):
            continue
        for i, line in enumerate(f.read_text().splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for pattern in SECRET_PATTERNS:
                if pattern.search(stripped):
                    results.append((f, i, stripped[:80]))
                    break
    return results


def test_no_secrets_in_source():
    found = _find_secrets(SRC)
    assert not found, "Potential secrets found:\n" + "\n".join(
        f"  {f}:{n} {line}" for f, n, line in found
    )


def test_no_secrets_in_tests():
    found = _find_secrets(HERE)
    assert not found, "Potential secrets found in tests:\n" + "\n".join(
        f"  {f}:{n} {line}" for f, n, line in found
    )
