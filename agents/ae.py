from __future__ import annotations

from typing import Any

from .base import Agent


class AEAgent(Agent):
    """1. AE (기획자) — 캠페인 전략 기획서 작성."""

    agent_id = "ae"
    agent_name = "AE (기획자)"
    emoji = "📋"

    @property
    def system_prompt(self) -> str:
        return """당신은 15년 경력의 광고 대행사 AE(Account Executive)입니다.
브랜드·목표·타겟을 분석해 캠페인 전략 기획서를 작성합니다.

기획서에는 반드시 아래 섹션을 포함하세요:
1. **캠페인 개요** — 한 줄 캠페인 방향
2. **브랜드 분석** — 강점, 포지셔닝
3. **타겟 인사이트** — 누구에게, 왜, 어떤 니즈
4. **캠페인 목표 & KPI** — 측정 가능한 목표
5. **핵심 메시지** — 전달할 하나의 메시지
6. **크리에이티브 방향** — 톤앤매너, 비주얼 가이드
7. **미디어 전략** — 채널별 접근
8. **제작팀 가이드** — 이미지/영상/옥외/혁신팀이 참고할 구체적 지침

전문적이면서 실행 가능한 기획서를 한국어로 작성하세요."""

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        return f"""다음 정보를 바탕으로 캠페인 전략 기획서를 작성해주세요.

- 브랜드: {context['brand']}
- 캠페인 목표: {context['goal']}
- 타겟: {context['target']}

추가 요청사항: {context.get('user_message', '없음')}"""
