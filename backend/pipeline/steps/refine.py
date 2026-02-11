"""Refine: rewrite user input into a structured spec."""

from __future__ import annotations

from ...utils.llm import LLMProvider
from .. import PipelineContext, _log


def refine(ctx: PipelineContext, provider: LLMProvider) -> None:
    _log("Refining input...")
    domain = ctx.metadata.get("domain", "general")
    ctx.spec = provider.refine_input(ctx.raw_text, domain=domain)
    if len(ctx.spec) > 2000:
        ctx.spec = ctx.spec[:2000] + "\n[truncated]"
    _log(f"Refined spec ({len(ctx.spec)} chars)")


def passthrough(ctx: PipelineContext, _provider: LLMProvider) -> None:
    _log("Passthrough (no refine)")
    ctx.spec = ctx.raw_text
