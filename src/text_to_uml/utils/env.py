"""Environment helpers."""

import os
from pathlib import Path


def load_dotenv() -> None:
    for candidate in [Path.cwd() / ".env", Path(__file__).resolve().parents[3] / ".env"]:
        if candidate.exists():
            _parse(candidate)
            return


def _parse(path: Path) -> None:
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())
