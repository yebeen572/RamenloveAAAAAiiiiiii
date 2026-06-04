from __future__ import annotations

import os
from typing import Any

from .base import Agent


class ImageTeam(Agent):
    """3-1. 이미지팀 — 디지털 이미지 광고 기획."""

    agent_id = "image"
    agent_name = "이미지팀"
    emoji = "🖼️"

    @property
    def system_prompt(self) -> str:
        return """당신은 디지털 이미지 광고 전문 크리에이티브 디렉터입니다.
기획서와 카피를 바탕으로 이미지 광고 소재 기획안을 작성합니다.

포함 항목:
1. **콘셉트** — 비주얼 한 줄 컨셉
2. **배너 소재 3종** — 각각 레이아웃, 카피 배치, 컬러, 이미지 묘사
3. **SNS 피드 소재 2종** — Instagram/Facebook용
4. **A/B 테스트 제안** — 2가지 변형
5. **제작 스펙** — 사이즈, 포맷, 파일 가이드

실제 디자이너가 바로 작업할 수 있을 정도로 구체적으로 작성하세요."""

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        feedback = context.get("feedback", {}).get("image", "")
        feedback_block = f"\n\n## 대표 피드백 (재작업)\n{feedback}" if feedback else ""
        return f"""## AE 기획서
{context['ae_plan']}

## 카피
{context['copy']}
{feedback_block}

브랜드: {context['brand']} — 이미지 광고 소재 기획안을 작성해주세요."""


class VideoTeam(Agent):
    """3-2. 영상팀 — 영상 광고 기획."""

    agent_id = "video"
    agent_name = "영상팀"
    emoji = "🎬"

    @property
    def system_prompt(self) -> str:
        return """당신은 영상 광고 PD입니다.
15초/30초/60초 영상 광고 기획안을 작성합니다.

포함 항목:
1. **영상 콘셉트** — 스토리텔링 한 줄
2. **15초 스팟** — 씬별 구성 (초 단위), 나레이션, 자막, BGM
3. **30초 스팟** — 씬별 구성
4. **쇼츠/릴스 15초** — 세로형 숏폼
5. **촬영/제작 가이드** — 장면, 분위기, 모델/소품
6. **CTA 엔딩** — 마지막 3초

영상 제작팀이 바로 촬영할 수 있도록 구체적으로 작성하세요."""

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        feedback = context.get("feedback", {}).get("video", "")
        feedback_block = f"\n\n## 대표 피드백 (재작업)\n{feedback}" if feedback else ""
        return f"""## AE 기획서
{context['ae_plan']}

## 카피
{context['copy']}
{feedback_block}

브랜드: {context['brand']} — 영상 광고 기획안을 작성해주세요."""


class OutdoorTeam(Agent):
    """3-3. 옥외팀 — OOH(옥외) 광고 기획."""

    agent_id = "outdoor"
    agent_name = "옥외팀"
    emoji = "🏙️"

    @property
    def system_prompt(self) -> str:
        return """당신은 OOH(Out-of-Home) 광고 전문 AE입니다.
옥외 광고 매체 기획안을 작성합니다.

포함 항목:
1. **옥외 콘셉트** — 거리에서 3초 안에 전달할 메시지
2. **버스 쉘터** — 디자인, 카피, 비주얼 묘사
3. **지하철 스크린도어/조명광고** — 레이아웃
4. **빌보드/건물 래핑** — 대형 옥외
5. **미디어 믹스 & 집행 제안** — 위치, 기간, 예상 노출
6. **현장 연출 아이디어** — POP-UP, 체험 부스 등

옥외 매체 특성(짧은 시선, 큰 임팩트)을 반영하세요."""

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        feedback = context.get("feedback", {}).get("outdoor", "")
        feedback_block = f"\n\n## 대표 피드백 (재작업)\n{feedback}" if feedback else ""
        return f"""## AE 기획서
{context['ae_plan']}

## 카피
{context['copy']}
{feedback_block}

브랜드: {context['brand']} — 옥외 광고 기획안을 작성해주세요."""


class InnovationTeam(Agent):
    """3-4. 혁신팀 — 신규 미디어·체험형 광고 기획."""

    agent_id = "innovation"
    agent_name = "혁신팀"
    emoji = "💡"

    @property
    def system_prompt(self) -> str:
        return """당신은 마케팅 테크·혁신 미디어 전문가입니다.
기존 채널을 넘어선 혁신적 광고 아이디어를 기획합니다.

포함 항목:
1. **혁신 콘셉트** — "이런 광고는 처음이다" 수준의 아이디어
2. **AI/메타버스 활용** — 챗봇, AR 필터, 가상 체험 등
3. **바이럴/UGC 캠페인** — 참여형 이벤트
4. **브랜디드 콘텐츠** — 웹툰, 팟캐스트, 콜라보
5. **데이터 기반 퍼스널라이제이션** — 1:1 맞춤 접근
6. **실행 로드맵** — MVP → 확장 단계

미래지향적이면서 현실적으로 실행 가능한 아이디어를 제시하세요."""

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        feedback = context.get("feedback", {}).get("innovation", "")
        feedback_block = f"\n\n## 대표 피드백 (재작업)\n{feedback}" if feedback else ""
        return f"""## AE 기획서
{context['ae_plan']}

## 카피
{context['copy']}
{feedback_block}

브랜드: {context['brand']} — 혁신 광고 기획안을 작성해주세요."""


class CEOAgent(Agent):
    """4. 대표 (검수) — 채점 후 통과/재작업 판정."""

    agent_id = "ceo"
    agent_name = "대표 (검수)"
    emoji = "👔"

    @property
    def system_prompt(self) -> str:
        pass_score = int(os.getenv("PASS_SCORE", "70"))
        return f"""당신은 광고 대행사 대표이사입니다. 20년 경력의 까다로운 검수자입니다.
전체 캠페인 결과물을 종합 평가하고, 통과/재작업을 판정합니다.

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
```json
{{
  "overall_score": 0-100,
  "passed": true/false,
  "summary": "전체 총평 2-3문장",
  "team_scores": {{
    "ae": 0-100,
    "copywriter": 0-100,
    "image": 0-100,
    "video": 0-100,
    "outdoor": 0-100,
    "innovation": 0-100
  }},
  "team_feedback": {{
    "ae": "피드백 (재작업 시에만 구체적으로)",
    "copywriter": "피드백",
    "image": "피드백",
    "video": "피드백",
    "outdoor": "피드백",
    "innovation": "피드백"
  }},
  "rework_teams": ["재작업 필요 팀 id 목록, 예: image, video"]
}}
```

판정 기준:
- overall_score >= {pass_score} 이면 passed: true
- passed: false 이면 rework_teams에 70점 미만 팀 id를 넣으세요
- AE와 카피라이터는 재작업 대상에서 제외 (이미 완료된 단계)
- 재작업 대상은 image, video, outdoor, innovation 중에서만 선택"""

    def build_user_prompt(self, context: dict[str, Any]) -> str:
        return f"""다음 캠페인 결과물을 검수해주세요.

## 브리프
- 브랜드: {context['brand']}
- 목표: {context['goal']}
- 타겟: {context['target']}

## AE 기획서
{context['ae_plan']}

## 카피
{context['copy']}

## 이미지팀
{context.get('production', {}).get('image', '없음')}

## 영상팀
{context.get('production', {}).get('video', '없음')}

## 옥외팀
{context.get('production', {}).get('outdoor', '없음')}

## 혁신팀
{context.get('production', {}).get('innovation', '없음')}"""
