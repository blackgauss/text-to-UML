"""FastAPI server."""

from __future__ import annotations

import os

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.utils import (
    DiagramGenerationError,
    Orchestrator,
    ProviderError,
    build_provider,
)
from backend.utils.data_models import DiagramType
from backend.utils.env import load_dotenv

app = FastAPI(title="text-to-uml")
_provider = None


def _get_provider():
    global _provider
    if _provider is None:
        _provider = build_provider()
    return _provider


class GenerateRequest(BaseModel):
    text: str
    diagram_type: DiagramType = "auto"
    skip_refine: bool = False
    max_retries: int = 3


class GenerateResponse(BaseModel):
    code: str
    explanation: str
    is_valid: bool


@app.post("/generate", response_model=GenerateResponse)
def generate_diagram(req: GenerateRequest):
    try:
        provider = _get_provider()
        orchestrator = Orchestrator(
            provider=provider,
            max_retries=req.max_retries,
            skip_refine=req.skip_refine,
        )
        artifact = orchestrator.run(req.text, diagram_type=req.diagram_type)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except DiagramGenerationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return GenerateResponse(
        code=artifact.code,
        explanation=artifact.explanation,
        is_valid=artifact.is_valid,
    )


def _parse_port(default: int = 8000) -> int:
    raw = os.environ.get("API_PORT")
    if not raw or not raw.strip():
        return default
    try:
        port = int(raw)
    except ValueError:
        return default
    if not (0 < port < 65536):
        return default
    return port


def serve() -> None:
    load_dotenv()
    host = os.environ.get("API_HOST", "127.0.0.1")
    port = _parse_port()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    serve()
