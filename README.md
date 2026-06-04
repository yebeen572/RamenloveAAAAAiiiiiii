# 🏢 AI 광고 대행사 — 7인조 멀티 에이전트

채팅창에 한 마디만 입력하면, **7명의 AI 팀원**이 협업하여 **캠페인 바이블**을 자동으로 완성합니다.

```
사용자 입력
    ↓
STEP 1  AE (기획자) ──── 순차
    ↓
STEP 2  카피라이터 ──── 순차
    ↓
STEP 3  이미지팀 / 영상팀 / 옥외팀 / 혁신팀 ──── 병렬 (동시)
    ↓
STEP 4  대표 (검수) ──── 채점 → 통과 or 재작업
    ↓
STEP 5  캠페인 바이블 완성
```

## 팀 구성 (7명)

| 팀 | 역할 | 실행 방식 |
|---|---|---|
| 📋 AE | 캠페인 전략 기획서 | 순차 (1번) |
| ✍️ 카피라이터 | 슬로건·헤드라인·CTA | 순차 (2번) |
| 🖼️ 이미지팀 | 디지털 이미지 광고 | **병렬** |
| 🎬 영상팀 | 15/30초 영상 광고 | **병렬** |
| 🏙️ 옥외팀 | OOH 옥외 광고 | **병렬** |
| 💡 혁신팀 | AI/바이럴/신규 미디어 | **병렬** |
| 👔 대표 | 검수·채점·재작업 지시 | 순차 (마지막) |

## 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. API 키 설정

```bash
copy .env.example .env
```

`.env` 파일에 OpenAI API 키를 입력하세요:

```
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. 서버 실행

```bash
uvicorn main:app --reload --port 8000
```

브라우저에서 **http://localhost:8000** 을 열어주세요.

## 사용법

채팅창에 아래 형식으로 입력하세요:

```
브랜드 | 목표 | 타겟
```

**예시:**
```
네이버 클로바X | AI 교육 서비스 런칭 홍보 | 20~30대 직장인
```

입력하면 AE → 카피 → 4개 제작팀(동시) → 대표 검수 → 캠페인 바이블 순으로 자동 진행됩니다.

## 핵심 설계

### 순차 vs 병렬

- **순차**: AE → 카피라이터 (방향이 정해져야 다음 작업 가능)
- **병렬**: 4개 제작팀 (`asyncio.gather`로 동시 실행 → 4배 빠름)
- **재작업 루프**: 대표가 점수 미달 팀에만 재작업 지시 (최대 2회)

### 파일 구조

```
appagency/
├── main.py           # FastAPI 서버 + SSE 스트리밍
├── orchestrator.py   # 워크플로우 엔진 (순차/병렬/재작업)
├── parser.py         # 사용자 입력 파싱
├── agents/
│   ├── base.py       # LLM 에이전트 베이스
│   ├── ae.py         # AE 기획자
│   ├── copywriter.py # 카피라이터
│   └── production.py # 4개 제작팀 + 대표
└── static/
    └── index.html    # 채팅 UI + 워크플로우 시각화
```

## API

| 엔드포인트 | 설명 |
|---|---|
| `GET /` | 웹 UI |
| `GET /api/health` | 서버 상태 확인 |
| `POST /api/campaign` | 캠페인 생성 (일괄 응답) |
| `POST /api/campaign/stream` | 캠페인 생성 (SSE 실시간) |

## 환경 변수

| 변수 | 기본값 | 설명 |
|---|---|---|
| `OPENAI_API_KEY` | (필수) | OpenAI API 키 |
| `OPENAI_MODEL` | `gpt-4o-mini` | 사용할 모델 |
| `PASS_SCORE` | `70` | 대표 검수 통과 점수 |
| `MAX_REWORK_ROUNDS` | `2` | 최대 재작업 횟수 |
