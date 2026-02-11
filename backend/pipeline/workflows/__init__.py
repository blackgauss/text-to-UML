"""Workflow auto-discovery — import all modules in this package to trigger registration."""

from pathlib import Path
import importlib

_dir = Path(__file__).parent
for _f in _dir.glob("*.py"):
    if _f.name.startswith("_"):
        continue
    importlib.import_module(f"{__package__}.{_f.stem}")
