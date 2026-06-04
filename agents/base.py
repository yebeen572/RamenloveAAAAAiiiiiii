from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from openai import AsyncOpenAI


@dataclass
class AgentResult:
    agent_id: str
    agent_name: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Agent:
    """LLM 기반 에이전트 베이스 클래스."""

    agent_id: str = "base"
    agent_name: str = "에이전트"
    emoji: str = "🤖"

    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def system_prompt(self) -> str:
        raise NotImplementedError

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        raise NotImplementedError

    async def run(self, context: dict[str, Any]) -> AgentResult:
        user_prompt = self.build_user_prompt(context)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.8,
        )
        content = response.choices[0].message.content or ""
        return AgentResult(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            content=content.strip(),
        )
