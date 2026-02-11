"""FastAPI server."""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from text_to_uml.utils import (
    DiagramGenerationError,
    Orchestrator,
    ProviderError,
    build_provider,
)
from text_to_uml.utils.data_models import DiagramType

_ROOT = Path(__file__).resolve().parents[2]

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


def _load_dotenv() -> None:
    env_path = _ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def serve() -> None:
    _load_dotenv()
    host = os.environ.get("API_HOST", "127.0.0.1")
    port = int(os.environ.get("API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    serve()
