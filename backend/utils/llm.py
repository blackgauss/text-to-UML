"""Abstract LLM provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .data_models import DiagramRequest, MermaidArtifact


class LLMProvider(ABC):

    @abstractmethod
    def route_domain(self, text: str) -> str: ...

    @abstractmethod
    def refine_input(self, text: str, domain: str = "general") -> str: ...

    @abstractmethod
    def generate_diagram(self, request: DiagramRequest, domain: str = "general") -> MermaidArtifact: ...

    @abstractmethod
    def repair_code(self, broken_code: str, error_msg: str) -> MermaidArtifact: ...

