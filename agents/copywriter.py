from __future__ import annotations

from typing import Any

from .base import Agent


class CopywriterAgent(Agent):
    """2. 카피라이터 — 핵심 카피·슬로건 작성."""

    agent_id = "copywriter"
    agent_name = "카피라이터"
    emoji = "✍️"

    @property
    def system_prompt(self) -> str:
        return """당신은 수상 경력이 있는 광고 카피라이터입니다.
AE 기획서의 방향에 맞춰 임팩트 있는 카피를 작성합니다.

다음을 반드시 포함하세요:
1. **메인 슬로건** — 3개 후보 (각 15자 이내 권장)
2. **서브 카피** — 슬로건을 보완하는 2~3줄
3. **헤드라인** — 디지털 배너용 5개
4. **CTA (Call to Action)** — 3개
5. **해시태그** — SNS용 5개
6. **카피 톤 가이드** — 제작팀이 따를 언어 스타일

기획서의 핵심 메시지와 크리에이티브 방향을 정확히 반영하세요."""

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        return f"""AE 기획서를 바탕으로 카피를 작성해주세요.

## AE 기획서
{context['ae_plan']}

---
브랜드: {context['brand']} | 목표: {context['goal']} | 타겟: {context['target']}"""
