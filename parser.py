from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class BriefInput:
    brand: str
    goal: str
    target: str
    user_message: str


def parse_user_message(message: str) -> BriefInput:
    """사용자 한 마디에서 브랜드·목표·타겟을 추출합니다.

    지원 형식:
    - "브랜드: X | 목표: Y | 타겟: Z"
    - "X 브랜드, Y 목표, Z 타겟"
    - 자유 형식 (전체를 브리프로 사용, 기본값 적용)
    """
    message = message.strip()
    if not message:
        raise ValueError("메시지를 입력해주세요.")

    pipe_match = re.match(
        r"브랜드\s*[:：]\s*(.+?)\s*[|｜]\s*목표\s*[:：]\s*(.+?)\s*[|｜]\s*타겟\s*[:：]\s*(.+)",
        message,
        re.DOTALL,
    )
    if pipe_match:
        return BriefInput(
            brand=pipe_match.group(1).strip(),
            goal=pipe_match.group(2).strip(),
            target=pipe_match.group(3).strip(),
            user_message=message,
        )

    simple_pipe = re.match(r"^(.+?)\s*[|｜]\s*(.+?)\s*[|｜]\s*(.+)$", message, re.DOTALL)
    if simple_pipe:
        return BriefInput(
            brand=simple_pipe.group(1).strip(),
            goal=simple_pipe.group(2).strip(),
            target=simple_pipe.group(3).strip(),
            user_message=message,
        )

    for_match = re.match(
        r"(.+?)\s*브랜드\s*[,，]\s*(.+?)\s*목표\s*[,，]\s*(.+?)\s*타겟",
        message,
    )
    if for_match:
        return BriefInput(
            brand=for_match.group(1).strip(),
            goal=for_match.group(2).strip(),
            target=for_match.group(3).strip(),
            user_message=message,
        )

    # 자유 형식: 문장에서 키워드 추출 시도
    brand = _extract_after(message, ["브랜드", "brand"]) or message.split(",")[0].strip()
    goal = _extract_after(message, ["목표", "goal", "캠페인"]) or "브랜드 인지도 및 전환율 향상"
    target = _extract_after(message, ["타겟", "target", "대상"]) or "20~30대 디지털 네이티브"

    return BriefInput(brand=brand, goal=goal, target=target, user_message=message)


def _extract_after(text: str, keywords: list[str]) -> str | None:
    for kw in keywords:
        pattern = rf"{kw}\s*[:：은는]?\s*([^,，|｜]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None
