"""Concrete LLM providers."""

from __future__ import annotations

import json
import os

import openai

from .data_models import DiagramRequest, MermaidArtifact, ProviderError
from .llm import LLMProvider
from ..prompts import (
    DOMAINS,
    GENERATE_BASE,
    REFINER_BASE,
    REPAIR_SYSTEM,
    ROUTER_SYSTEM,
    get_style_guide,
)

_DEFAULT_TIMEOUT = 120.0
_CLIENT_TIMEOUT = 60.0


class _OpenAICompatibleProvider(LLMProvider):

    def __init__(self, *, api_key: str, model: str, base_url: str | None = None):
        self.client = openai.Client(
            api_key=api_key,
            base_url=base_url,
            timeout=_CLIENT_TIMEOUT,
        )
        self.model = model

    def _chat(self, system: str, user: str, json_mode: bool = False) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"} if json_mode else openai.NOT_GIVEN,
                timeout=_DEFAULT_TIMEOUT,
            )
            return resp.choices[0].message.content or ""
        except openai.APIError as exc:
            raise ProviderError(f"API error: {exc}") from exc

    def route_domain(self, text: str) -> str:
        raw = self._chat(ROUTER_SYSTEM, text, json_mode=True)
        try:
            domain = json.loads(raw).get("domain", "general")
        except (json.JSONDecodeError, AttributeError):
            return "general"
        return domain if domain in DOMAINS else "general"

    def refine_input(self, text: str, domain: str = "general") -> str:
        system = REFINER_BASE + "\n\n" + get_style_guide(domain)
        return self._chat(system, text)

    def generate_diagram(self, request: DiagramRequest, domain: str = "general") -> MermaidArtifact:
        system = GENERATE_BASE.format(diagram_type=request.diagram_type) + "\n\n" + get_style_guide(domain)
        raw = self._chat(system, request.raw_text, json_mode=True)
        return MermaidArtifact.model_validate_json(raw)

    def repair_code(self, broken_code: str, error_msg: str) -> MermaidArtifact:
        system = REPAIR_SYSTEM.format(broken_code=broken_code, error_msg=error_msg)
        raw = self._chat(system, "Fix the code above.", json_mode=True)
        return MermaidArtifact.model_validate_json(raw)


class OpenAIProvider(_OpenAICompatibleProvider):
    def __init__(self, api_key: str, model: str):
        super().__init__(api_key=api_key, model=model)


class OllamaProvider(_OpenAICompatibleProvider):
    def __init__(self, model: str, base_url: str):
        super().__init__(api_key="ollama", model=model, base_url=base_url)


_PROVIDER_DEFAULTS: dict[str, dict[str, str]] = {
    "openai": {"model": "gpt-4o"},
    "ollama": {"model": "llama3", "base_url": "http://localhost:11434/v1"},
}


def build_provider() -> LLMProvider:
    name = os.environ.get("LLM_PROVIDER", "openai").lower()

    if name == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise ProviderError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        model = os.environ.get("LLM_MODEL", _PROVIDER_DEFAULTS["openai"]["model"])
        return OpenAIProvider(api_key=api_key, model=model)

    if name == "ollama":
        defaults = _PROVIDER_DEFAULTS["ollama"]
        model = os.environ.get("LLM_MODEL", defaults["model"])
        base_url = os.environ.get("OLLAMA_BASE_URL", defaults["base_url"])
        return OllamaProvider(model=model, base_url=base_url)

    raise ProviderError(f"Unknown LLM_PROVIDER '{name}'. Supported: {list(_PROVIDER_DEFAULTS)}")