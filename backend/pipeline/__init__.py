"""Pipeline engine — context, protocol, runner, and registry."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any, Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.data_models import MermaidArtifact
    from ..utils.llm import LLMProvider


# ── Context & protocol ────────────────────────────────────────────────

@dataclass
class PipelineContext:
    raw_text: str
    diagram_type: str = "auto"
    max_retries: int = 3
    spec: str = ""
    artifact: MermaidArtifact | None = None
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class StepFn(Protocol):
    def __call__(self, ctx: PipelineContext, provider: LLMProvider) -> None: ...


# ── Pipeline runner ───────────────────────────────────────────────────

class Pipeline:

    def __init__(self, steps: list[StepFn] | None = None):
        self._steps: list[StepFn] = steps or []

    def add(self, step: StepFn) -> Pipeline:
        self._steps.append(step)
        return self

    def __iter__(self):
        return iter(self._steps)

    def __len__(self):
        return len(self._steps)

    def __repr__(self) -> str:
        names = [s.__name__ if hasattr(s, "__name__") else str(s) for s in self._steps]
        return " → ".join(names)


# ── Registry ──────────────────────────────────────────────────────────

_REGISTRY: dict[str, Pipeline] = {}


def register(name: str, pipeline: Pipeline) -> None:
    _REGISTRY[name] = pipeline


def get_pipeline(name: str = "default") -> Pipeline:
    if name not in _REGISTRY:
        # lazy-import workflows so they self-register
        from . import workflows as _  # noqa: F811
    if name not in _REGISTRY:
        raise ValueError(f"Unknown pipeline '{name}'. Available: {list(_REGISTRY)}")
    return _REGISTRY[name]


def available_pipelines() -> list[str]:
    from . import workflows as _  # noqa: F811
    return list(_REGISTRY)


# ── Shared logger ─────────────────────────────────────────────────────

def _log(msg: str) -> None:
    print(f"[pipeline] {msg}", file=sys.stderr)
