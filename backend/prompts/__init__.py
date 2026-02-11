"""Prompt template loader."""

from pathlib import Path

_DIR = Path(__file__).parent

def _read(name: str) -> str:
    return (_DIR / name).read_text().strip()

STYLE_GUIDE = _read("style_guide.txt")
REFINER_SYSTEM = _read("refiner.txt") + "\n\n" + STYLE_GUIDE
GENERATE_SYSTEM = _read("generate.txt") + "\n\n" + STYLE_GUIDE
REPAIR_SYSTEM = _read("repair.txt")
