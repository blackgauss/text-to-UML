"""Data contracts and validation."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from typing import Literal

from pydantic import BaseModel, Field

DiagramType = Literal["sequence", "flowchart", "class", "erd", "auto"]

_DIRECTIVES = {
    "graph", "flowchart", "sequenceDiagram", "classDiagram",
    "erDiagram", "stateDiagram", "stateDiagram-v2",
    "gantt", "pie", "gitGraph",
}

_DANGEROUS = re.compile(r"<script|<iframe|javascript:", re.IGNORECASE)


class DiagramGenerationError(Exception):
    pass


class ProviderError(Exception):
    pass


class DiagramRequest(BaseModel):
    raw_text: str
    diagram_type: DiagramType = "auto"


class MermaidArtifact(BaseModel):
    code: str = Field(description="Raw Mermaid syntax")
    explanation: str = ""
    is_valid: bool = False

    def validate_syntax(self) -> tuple[bool, str]:
        code = self.code.strip()

        if not code:
            return False, "Empty code"

        if code.startswith("```"):
            lines = code.splitlines()
            code = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            self.code = code.strip()

        first_word = code.split()[0] if code.split() else ""
        if first_word not in _DIRECTIVES:
            return False, f"Unknown directive '{first_word}'. Expected one of: {_DIRECTIVES}"

        if _DANGEROUS.search(code):
            return False, "Code contains potentially dangerous content"

        for open_ch, close_ch in [("{", "}"), ("[", "]"), ("(", ")")]:
            if code.count(open_ch) != code.count(close_ch):
                return False, f"Unbalanced '{open_ch}' / '{close_ch}'"

        if len(code.strip().splitlines()) < 2:
            return False, "Diagram body is empty (only directive line found)"

        return True, ""

    def compile_check(self) -> tuple[bool, str]:
        ok, err = self.validate_syntax()
        if not ok:
            return ok, err

        mmdc = shutil.which("mmdc")
        if not mmdc:
            return True, ""

        with tempfile.TemporaryDirectory() as tmp:
            in_path = f"{tmp}/input.mmd"
            out_path = f"{tmp}/output.svg"
            with open(in_path, "w") as f:
                f.write(self.code)
            result = subprocess.run(
                [mmdc, "-i", in_path, "-o", out_path, "--quiet"],
                capture_output=True, text=True, timeout=30,
            )

        if result.returncode == 0:
            return True, ""

        stderr = result.stderr.strip()
        for line in stderr.splitlines():
            if "Error:" in line or "Expecting" in line:
                return False, line.strip()
        return False, stderr[:300] if stderr else "mmdc exited with non-zero status"