from __future__ import annotations

import json
import os
from dataclasses import dataclass

import httpx


@dataclass
class GenerationRequest:
    system_prompt: str
    user_prompt: str
    temperature: float = 0.1


class LLMProvider:
    def generate(self, request: GenerationRequest) -> str:
        raise NotImplementedError


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model_name = os.getenv("MODEL_NAME", "gpt-4.1-mini")

    def generate(self, request: GenerationRequest) -> str:
        if not self.api_key:
            return self._mock_response(request)

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "temperature": request.temperature,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"].strip()

    @staticmethod
    def _mock_response(request: GenerationRequest) -> str:
        # Deterministic fallback for local orchestration testing without external model.
        return json.dumps(
            {
                "mode": "mock",
                "system": request.system_prompt[:120],
                "user": request.user_prompt[:400],
            },
            ensure_ascii=True,
        )


def build_provider() -> LLMProvider:
    return OpenAICompatibleProvider()
