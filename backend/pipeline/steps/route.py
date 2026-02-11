"""Route: classify the domain of the input."""

from __future__ import annotations

from ...utils.llm import LLMProvider
from .. import PipelineContext, _log


def route(ctx: PipelineContext, provider: LLMProvider) -> None:
    _log("Routing domain...")
    domain = provider.route_domain(ctx.raw_text)
    ctx.metadata["domain"] = domain
    _log(f"Domain: {domain}")
