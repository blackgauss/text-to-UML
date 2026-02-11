"""Constrain: inject domain grammar rules into the spec before generation."""

from __future__ import annotations

from ...prompts import get_grammar, format_grammar_prompt
from ...utils.llm import LLMProvider
from .. import PipelineContext, _log


def constrain(ctx: PipelineContext, _provider: LLMProvider) -> None:
    domain = ctx.metadata.get("domain", "general")
    grammar = get_grammar(domain)

    if grammar is None:
        _log(f"No grammar for domain '{domain}', skipping constraints")
        return

    constraint_block = format_grammar_prompt(grammar)
    ctx.metadata["grammar"] = grammar
    ctx.spec = ctx.spec + "\n\n" + constraint_block
    _log(f"Injected {domain} grammar ({len(grammar['node_types'])} types, {len(grammar['valid_connections'])} connections)")
