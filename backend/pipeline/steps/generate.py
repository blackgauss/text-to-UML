"""Generate: produce a Mermaid diagram from the refined spec."""

from __future__ import annotations

from ...utils.data_models import DiagramRequest
from ...utils.llm import LLMProvider
from .. import PipelineContext, _log


def generate(ctx: PipelineContext, provider: LLMProvider) -> None:
    _log("Generating diagram...")
    domain = ctx.metadata.get("domain", "general")
    request = DiagramRequest(raw_text=ctx.spec, diagram_type=ctx.diagram_type)  # type: ignore[arg-type]
    ctx.artifact = provider.generate_diagram(request, domain=domain)
    _log("Initial diagram generated")
