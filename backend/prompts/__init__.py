"""Prompt template loader."""

from pathlib import Path

_DIR = Path(__file__).parent
_STYLE_DIR = _DIR / "style_guides"

# Known domains — add new .txt files to style_guides/ and register here.
DOMAINS: set[str] = {p.stem for p in _STYLE_DIR.glob("*.txt")}

def _read(name: str) -> str:
    return (_DIR / name).read_text().strip()

def get_style_guide(domain: str = "general") -> str:
    path = _STYLE_DIR / f"{domain}.txt"
    if not path.exists():
        path = _STYLE_DIR / "general.txt"
    return path.read_text().strip()

REFINER_BASE = _read("refiner.txt")
GENERATE_BASE = _read("generate.txt")
REPAIR_SYSTEM = _read("repair.txt")
ROUTER_SYSTEM = _read("router.txt")

# Backwards-compatible defaults (general style guide baked in).
STYLE_GUIDE = get_style_guide("general")
REFINER_SYSTEM = REFINER_BASE + "\n\n" + STYLE_GUIDE
GENERATE_SYSTEM = GENERATE_BASE + "\n\n" + STYLE_GUIDE
