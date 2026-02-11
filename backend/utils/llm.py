"""Abstract LLM provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .data_models import DiagramRequest, MermaidArtifact


class LLMProvider(ABC):

    @abstractmethod
    def refine_input(self, text: str) -> str: ...

    @abstractmethod
    def generate_diagram(self, request: DiagramRequest) -> MermaidArtifact: ...

    @abstractmethod
    def repair_code(self, broken_code: str, error_msg: str) -> MermaidArtifact: ...

