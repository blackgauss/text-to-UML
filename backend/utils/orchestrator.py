"""Pipeline runner."""

from __future__ import annotations

import sys

from .data_models import MermaidArtifact
from .llm import LLMProvider
from .pipeline import Pipeline, PipelineContext, default_pipeline


class Orchestrator:
    def __init__(
        self,
        provider: LLMProvider,
        pipeline: Pipeline | None = None,
        *,
        max_retries: int = 3,
        skip_refine: bool = False,
    ):
        self.provider = provider
        self.max_retries = max_retries
        self.pipeline = pipeline or default_pipeline(skip_refine=skip_refine)

    def run(self, raw_text: str, diagram_type: str = "auto") -> MermaidArtifact:
        ctx = PipelineContext(
            raw_text=raw_text,
            diagram_type=diagram_type,
            max_retries=self.max_retries,
        )

        _log(f"Running pipeline: {self.pipeline}")
        for step in self.pipeline:
            step(ctx, self.provider)

        assert ctx.artifact is not None, "Pipeline completed but produced no artifact"
        return ctx.artifact


def _log(msg: str) -> None:
    print(f"[orchestrator] {msg}", file=sys.stderr)