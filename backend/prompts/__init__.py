"""Prompt template loader."""

import json
from pathlib import Path

_DIR = Path(__file__).parent
_STYLE_DIR = _DIR / "style_guides"
_GRAMMAR_DIR = _DIR / "grammars"

# Known domains — add new .txt files to style_guides/ and register here.
DOMAINS: set[str] = {p.stem for p in _STYLE_DIR.glob("*.txt")}

def _read(name: str) -> str:
    return (_DIR / name).read_text().strip()

def get_style_guide(domain: str = "general") -> str:
    path = _STYLE_DIR / f"{domain}.txt"
    if not path.exists():
        path = _STYLE_DIR / "general.txt"
    return path.read_text().strip()


def get_grammar(domain: str) -> dict | None:
    path = _GRAMMAR_DIR / f"{domain}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def format_grammar_prompt(grammar: dict) -> str:
    """Turn a grammar dict into a prompt-friendly constraint block."""
    lines = [
        "## Domain Grammar Constraints",
        "",
        f"Domain: {grammar['description']}",
        "",
        "You MUST only use the node types and connections listed below.",
        "Do NOT invent node types outside this list.",
        "Do NOT create connections between types unless they appear in the valid connections list.",
        "You may omit types that are not relevant to the user's description.",
        "",
        "### Allowed Node Types",
        "",
    ]
    for nt in grammar["node_types"]:
        lines.append(f"- **{nt['id']}** ({nt['label']}): {nt['desc']}  [shape: {nt['shape']}]")

    lines += ["", "### Valid Connections", ""]
    for c in grammar["valid_connections"]:
        lines.append(f"- {c['from']} → {c['to']}  (edge label: \"{c['label']}\")")

    lines += [
        "",
        "If the user mentions a concept that doesn't map to any type above,",
        "pick the closest match and note the mapping in the explanation field.",
    ]
    return "\n".join(lines)

REFINER_BASE = _read("refiner.txt")
GENERATE_BASE = _read("generate.txt")
REPAIR_SYSTEM = _read("repair.txt")
ROUTER_SYSTEM = _read("router.txt")

# Backwards-compatible defaults (general style guide baked in).
STYLE_GUIDE = get_style_guide("general")
REFINER_SYSTEM = REFINER_BASE + "\n\n" + STYLE_GUIDE
GENERATE_SYSTEM = GENERATE_BASE + "\n\n" + STYLE_GUIDE
