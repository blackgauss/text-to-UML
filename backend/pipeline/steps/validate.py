"""Validate and repair: compiler check with retry loop."""

from __future__ import annotations

from ...utils.data_models import DiagramGenerationError
from ...utils.llm import LLMProvider
from .. import PipelineContext, _log


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
