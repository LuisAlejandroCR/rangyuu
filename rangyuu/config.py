# config.py: reads configuration from the process environment, falling back to .env.local.
# A real environment variable always wins, so a container or Cloud Run secret is never
# shadowed by a stale file. The file is gitignored and only meant for local development.

import os
from pathlib import Path

ENV_FILE = ".env.local"
_cache: dict | None = None


def _load(path: Path) -> dict:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip("'\"")
        if value:
            values[key.strip()] = value
    return values


def get(name: str, default: str = "") -> str:
    """Environment first, then .env.local, then the default."""
    global _cache
    found = os.environ.get(name)
    if found:
        return found
    if _cache is None:
        _cache = _load(Path.cwd() / ENV_FILE)
    return _cache.get(name, default)


def reset() -> None:
    """Drop the cached file so a test or a long-lived process can re-read it."""
    global _cache
    _cache = None
