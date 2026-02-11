"""Pipeline runner."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from .data_models import MermaidArtifact
from .llm import LLMProvider

if TYPE_CHECKING:
    from ..pipeline import Pipeline, PipelineContext


@dataclass
class PipelineResult:
    artifact: MermaidArtifact
    metadata: dict[str, Any]


class Orchestrator:
    def __init__(
        self,
        provider: LLMProvider,
        pipeline: Pipeline | str | None = None,
        *,
        max_retries: int = 3,
        skip_refine: bool = False,
    ):
        from ..pipeline import Pipeline as _Pipeline, get_pipeline

        self.provider = provider
        self.max_retries = max_retries

        if isinstance(pipeline, _Pipeline):
            self.pipeline = pipeline
        elif isinstance(pipeline, str):
            self.pipeline = get_pipeline(pipeline)
        else:
            self.pipeline = get_pipeline("fast" if skip_refine else "default")

    def run(self, raw_text: str, diagram_type: str = "auto") -> PipelineResult:
        from ..pipeline import PipelineContext

        ctx = PipelineContext(
            raw_text=raw_text,
            diagram_type=diagram_type,
            max_retries=self.max_retries,
        )

        _log(f"Running pipeline: {self.pipeline}")
        for step in self.pipeline:
            step(ctx, self.provider)

        assert ctx.artifact is not None, "Pipeline completed but produced no artifact"
        return PipelineResult(artifact=ctx.artifact, metadata=ctx.metadata)


def _log(msg: str) -> None:
    print(f"[orchestrator] {msg}", file=sys.stderr)