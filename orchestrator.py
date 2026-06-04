from __future__ import annotations

import asyncio
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable

from agents.ae import AEAgent
from agents.copywriter import CopywriterAgent
from agents.production import (
    CEOAgent,
    ImageTeam,
    InnovationTeam,
    OutdoorTeam,
    VideoTeam,
)

PRODUCTION_TEAMS: dict[str, type] = {
    "image": ImageTeam,
    "video": VideoTeam,
    "outdoor": OutdoorTeam,
    "innovation": InnovationTeam,
}


@dataclass
class CampaignState:
    brand: str
    goal: str
    target: str
    user_message: str = ""
    ae_plan: str = ""
    copy: str = ""
    production: dict[str, str] = field(default_factory=dict)
    ceo_review: dict[str, Any] = field(default_factory=dict)
    rework_round: int = 0
    feedback: dict[str, str] = field(default_factory=dict)


EventCallback = Callable[[str, dict[str, Any]], None]


class CampaignOrchestrator:
    """7명 AI 팀원 워크플로우 오케스트레이터.

    STEP 1: AE (순차)
    STEP 2: 카피라이터 (순차)
    STEP 3: 4개 제작팀 (병렬)
    STEP 4: 대표 검수 → 재작업 루프
    STEP 5: 캠페인 바이블 통합
    """

    def __init__(self) -> None:
        self.max_rework = int(os.getenv("MAX_REWORK_ROUNDS", "2"))

    async def run(
        self,
        brand: str,
        goal: str,
        target: str,
        user_message: str = "",
        on_event: EventCallback | None = None,
    ) -> dict[str, Any]:
        state = CampaignState(
            brand=brand,
            goal=goal,
            target=target,
            user_message=user_message,
        )

        def emit(event_type: str, data: dict[str, Any]) -> None:
            if on_event:
                on_event(event_type, data)

        # STEP 1: AE 기획
        emit("step_start", {"step": 1, "label": "AE 기획서 작성"})
        ae = AEAgent()
        emit("agent_start", {"agent_id": "ae", "name": ae.agent_name, "emoji": ae.emoji})
        ae_result = await ae.run(self._context(state))
        state.ae_plan = ae_result.content
        emit("agent_done", {"agent_id": "ae", "name": ae.agent_name, "content": ae_result.content})

        # STEP 2: 카피라이터
        emit("step_start", {"step": 2, "label": "카피 작성"})
        copywriter = CopywriterAgent()
        emit("agent_start", {"agent_id": "copywriter", "name": copywriter.agent_name, "emoji": copywriter.emoji})
        copy_result = await copywriter.run(self._context(state))
        state.copy = copy_result.content
        emit("agent_done", {"agent_id": "copywriter", "name": copywriter.agent_name, "content": copy_result.content})

        # STEP 3 + 4: 제작팀 병렬 → 대표 검수 (재작업 루프)
        while True:
            emit("step_start", {"step": 3, "label": "4개 제작팀 동시 작업", "rework_round": state.rework_round})

            teams_to_run = list(PRODUCTION_TEAMS.keys())
            if state.rework_round > 0 and state.ceo_review.get("rework_teams"):
                teams_to_run = state.ceo_review["rework_teams"]

            await self._run_production_parallel(state, teams_to_run, emit)

            emit("step_start", {"step": 4, "label": "대표 검수"})
            ceo = CEOAgent()
            emit("agent_start", {"agent_id": "ceo", "name": ceo.agent_name, "emoji": ceo.emoji})
            ceo_result = await ceo.run(self._context(state))
            review = self._parse_ceo_review(ceo_result.content)
            state.ceo_review = review
            emit("agent_done", {
                "agent_id": "ceo",
                "name": ceo.agent_name,
                "content": ceo_result.content,
                "review": review,
            })

            if review.get("passed") or state.rework_round >= self.max_rework:
                break

            rework_teams = review.get("rework_teams", [])
            if not rework_teams:
                break

            state.rework_round += 1
            state.feedback = review.get("team_feedback", {})
            emit("rework", {"round": state.rework_round, "teams": rework_teams, "feedback": state.feedback})

        # STEP 5: 캠페인 바이블
        emit("step_start", {"step": 5, "label": "캠페인 바이블 완성"})
        bible = self._compile_bible(state)
        emit("complete", {"bible": bible, "review": state.ceo_review})

        return {
            "brand": state.brand,
            "goal": state.goal,
            "target": state.target,
            "ae_plan": state.ae_plan,
            "copy": state.copy,
            "production": state.production,
            "ceo_review": state.ceo_review,
            "rework_rounds": state.rework_round,
            "campaign_bible": bible,
        }

    async def run_stream(
        self,
        brand: str,
        goal: str,
        target: str,
        user_message: str = "",
    ) -> AsyncIterator[str]:
        """SSE 스트리밍용 이벤트 생성."""
        queue: asyncio.Queue[tuple[str, dict[str, Any]] | None] = asyncio.Queue()

        def on_event(event_type: str, data: dict[str, Any]) -> None:
            queue.put_nowait((event_type, data))

        async def _run() -> None:
            try:
                await self.run(brand, goal, target, user_message, on_event=on_event)
            finally:
                queue.put_nowait(None)

        task = asyncio.create_task(_run())

        while True:
            item = await queue.get()
            if item is None:
                break
            event_type, data = item
            yield f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

        await task

    async def _run_production_parallel(
        self,
        state: CampaignState,
        team_ids: list[str],
        emit: EventCallback,
    ) -> None:
        context = self._context(state)

        async def run_team(team_id: str) -> tuple[str, str]:
            team_cls = PRODUCTION_TEAMS[team_id]
            agent = team_cls()
            emit("agent_start", {"agent_id": team_id, "name": agent.agent_name, "emoji": agent.emoji})
            result = await agent.run(context)
            emit("agent_done", {"agent_id": team_id, "name": agent.agent_name, "content": result.content})
            return team_id, result.content

        results = await asyncio.gather(*[run_team(tid) for tid in team_ids])
        for team_id, content in results:
            state.production[team_id] = content

    def _context(self, state: CampaignState) -> dict[str, Any]:
        return {
            "brand": state.brand,
            "goal": state.goal,
            "target": state.target,
            "user_message": state.user_message,
            "ae_plan": state.ae_plan,
            "copy": state.copy,
            "production": state.production,
            "feedback": state.feedback,
        }

    def _parse_ceo_review(self, content: str) -> dict[str, Any]:
        match = re.search(r"\{[\s\S]*\}", content)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {
            "overall_score": 75,
            "passed": True,
            "summary": content[:200],
            "team_scores": {},
            "team_feedback": {},
            "rework_teams": [],
        }

    def _compile_bible(self, state: CampaignState) -> str:
        review = state.ceo_review
        scores = review.get("team_scores", {})
        score_lines = "\n".join(f"  - {k}: {v}점" for k, v in scores.items()) if scores else "  (점수 없음)"

        return f"""# 📗 캠페인 바이블

> **{state.brand}** | 목표: {state.goal} | 타겟: {state.target}

---

## 🏆 대표 검수 결과

- **종합 점수**: {review.get('overall_score', '-')}점
- **판정**: {'✅ 통과' if review.get('passed') else '⚠️ 조건부 통과'}
- **총평**: {review.get('summary', '')}
- **재작업 횟수**: {state.rework_round}회

### 팀별 점수
{score_lines}

---

## 📋 STEP 1 — AE 기획서

{state.ae_plan}

---

## ✍️ STEP 2 — 카피

{state.copy}

---

## 🖼️ STEP 3-1 — 이미지팀

{state.production.get('image', '(없음)')}

---

## 🎬 STEP 3-2 — 영상팀

{state.production.get('video', '(없음)')}

---

## 🏙️ STEP 3-3 — 옥외팀

{state.production.get('outdoor', '(없음)')}

---

## 💡 STEP 3-4 — 혁신팀

{state.production.get('innovation', '(없음)')}

---

*AI 광고 대행사 7인조가 자동 생성한 캠페인 바이블입니다.*
"""
