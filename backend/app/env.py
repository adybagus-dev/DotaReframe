from __future__ import annotations

import os
from pathlib import Path


def _parse_env_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None
    key, value = stripped.split("=", 1)
    key = key.strip()
    value = value.strip()
    if not key or key in os.environ:
        return None
    if value and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    return key, value


def load_environment(base_dir: Path | None = None) -> None:
    root = base_dir or Path(__file__).resolve().parents[2]
    candidates = [
        root / ".env",
        root / ".env.local",
        root / "backend" / ".env",
        root / "backend" / ".env.local",
    ]
    for path in candidates:
        if not path.exists():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            parsed = _parse_env_line(raw_line)
            if parsed:
                key, value = parsed
                os.environ.setdefault(key, value)
