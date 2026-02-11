"""Composable pipeline steps."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any, Protocol

from .data_models import DiagramGenerationError, DiagramRequest, MermaidArtifact
from .llm import LLMProvider


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


def refine(ctx: PipelineContext, provider: LLMProvider) -> None:
    _log("Refining input...")
    ctx.spec = provider.refine_input(ctx.raw_text)
    if len(ctx.spec) > 2000:
        ctx.spec = ctx.spec[:2000] + "\n[truncated]"
    _log(f"Refined spec ({len(ctx.spec)} chars)")


def passthrough(ctx: PipelineContext, _provider: LLMProvider) -> None:
    _log("Passthrough (no refine)")
    ctx.spec = ctx.raw_text


def generate(ctx: PipelineContext, provider: LLMProvider) -> None:
    _log("Generating diagram...")
    request = DiagramRequest(raw_text=ctx.spec, diagram_type=ctx.diagram_type)  # type: ignore[arg-type]
    ctx.artifact = provider.generate_diagram(request)
    _log("Initial diagram generated")


def validate_and_repair(ctx: PipelineContext, provider: LLMProvider) -> None:
    assert ctx.artifact is not None, "No artifact to validate — 'generate' step must run first"

    last_error = ""
    for attempt in range(ctx.max_retries):
        ok, error_msg = ctx.artifact.compile_check()
        if ok:
            ctx.artifact.is_valid = True
            _log("Validation passed ✓")
            return

        _log(f"Validation failed (attempt {attempt + 1}/{ctx.max_retries}): {error_msg}")
        last_error = error_msg
        _log("Requesting repair...")
        ctx.artifact = provider.repair_code(ctx.artifact.code, error_msg)

    ok, error_msg = ctx.artifact.compile_check()
    if ok:
        ctx.artifact.is_valid = True
        return

    ctx.error = last_error
    raise DiagramGenerationError(
        f"Failed after {ctx.max_retries} repair attempts. Last error: {last_error}"
    )


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


def default_pipeline(skip_refine: bool = False) -> Pipeline:
    return Pipeline([
        passthrough if skip_refine else refine,
        generate,
        validate_and_repair,
    ])


def _log(msg: str) -> None:
    print(f"[pipeline] {msg}", file=sys.stderr)
