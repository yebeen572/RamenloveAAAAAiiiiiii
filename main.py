"""AI 광고 대행사 — 7인조 멀티 에이전트 서버."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from orchestrator import CampaignOrchestrator
from parser import parse_user_message

load_dotenv()

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.getenv("OPENAI_API_KEY"):
        print("[WARN] OPENAI_API_KEY is not set. Check your .env file.")
    yield


app = FastAPI(
    title="AI 광고 대행사",
    description="7명의 AI 팀원이 캠페인 바이블을 자동 생성합니다.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = CampaignOrchestrator()


class CampaignRequest(BaseModel):
    message: str = Field(..., min_length=1, description="캠페인 브리프 (한 마디)")
    brand: str | None = None
    goal: str | None = None
    target: str | None = None


class CampaignResponse(BaseModel):
    brand: str
    goal: str
    target: str
    ae_plan: str
    copywriting: str
    production: dict[str, str]
    ceo_review: dict
    rework_rounds: int
    campaign_bible: str


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    }


@app.post("/api/campaign", response_model=CampaignResponse)
async def create_campaign(req: CampaignRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY가 설정되지 않았습니다.")

    if req.brand and req.goal and req.target:
        brand, goal, target = req.brand, req.goal, req.target
    else:
        try:
            brief = parse_user_message(req.message)
            brand, goal, target = brief.brand, brief.goal, brief.target
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    try:
        result = await orchestrator.run(
            brand=brand,
            goal=goal,
            target=target,
            user_message=req.message,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"캠페인 생성 실패: {e}")

    return CampaignResponse(
        brand=result["brand"],
        goal=result["goal"],
        target=result["target"],
        ae_plan=result["ae_plan"],
        copywriting=result["copy"],
        production=result["production"],
        ceo_review=result["ceo_review"],
        rework_rounds=result["rework_rounds"],
        campaign_bible=result["campaign_bible"],
    )


@app.post("/api/campaign/stream")
async def create_campaign_stream(req: CampaignRequest):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY가 설정되지 않았습니다.")

    if req.brand and req.goal and req.target:
        brand, goal, target = req.brand, req.goal, req.target
    else:
        try:
            brief = parse_user_message(req.message)
            brand, goal, target = brief.brand, brief.goal, brief.target
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return StreamingResponse(
        orchestrator.run_stream(brand, goal, target, req.message),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
