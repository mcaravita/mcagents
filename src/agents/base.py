from __future__ import annotations

from dataclasses import dataclass

from src.llm.provider import LLMProvider


@dataclass
class AgentContext:
    provider: LLMProvider


class BaseAgent:
    def __init__(self, name: str, context: AgentContext) -> None:
        self.name = name
        self.context = context
