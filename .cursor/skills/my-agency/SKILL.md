---
name: my-agency
description: 학교 새 학기 홍보 캠페인을 my-ae → my-copywriter → my-reviewer 3단계로 순차 실행한다. /myagency 또는 "내 캠페인 만들어줘"라고 하면 이 스킬을 사용한다.
disable-model-invocation: true
---

# My Agency — 3단계 캠페인 워크플로우

학교 새 학기 홍보 캠페인을 **my-ae → my-copywriter → my-reviewer** 순서로 실행한다.
각 단계는 **반드시 순차**로 진행한다. 다음 단계는 이전 단계 결과물이 저장된 뒤에만 시작한다.

## 트리거

다음 중 하나가 입력되면 이 스킬을 즉시 실행한다:

- `/myagency`
- "내 캠페인 만들어줘"

## 사전 확인

사용자 메시지에서 아래를 파악한다. 없으면 **한 번만** 물어본다:

- **학교명** (또는 브랜드)
- **홍보 목표**
- **타겟** (신입생 / 재학생 / 학부모 등)

형식 예: `○○고등학교 | 새 학기 신입생 모집 | 예비 중3·학부모`

`output/` 폴더가 없으면 생성한다.

---

## 진행 대본

아래 체크리스트를 복사해 진행 상황을 추적한다:

```
My Agency 진행:
- [ ] 1단계: my-ae 실행 → output/my_ae_plan.md 저장
- [ ] 2단계: my-copywriter 실행 → output/my_copy.md 저장
- [ ] 3단계: my-reviewer 실행 → output/my_review.md 저장
```

---

### 1단계: my-ae 실행 → 결과물 저장

**실행:** `my-ae` 서브에이전트를 호출한다.

**전달할 내용:**
- 학교명, 홍보 목표, 타겟
- 캠페인 주제: 「우리 학교 새 학기 홍보」
- `.cursor/agents/my-ae.md`의 역할·규칙·금지 사항을 따를 것

**완료 조건:**
- AE 기획서 작성 완료
- `output/my_ae_plan.md`에 저장

**사용자에게 알림:**
> 📋 1단계 — AE 기획서 작성 중…

완료 시:
> ✅ 1단계 완료 — `output/my_ae_plan.md` 저장됨

---

### 2단계: my-copywriter 실행 (1단계 결과물 전달) → 결과물 저장

**선행 조건:** `output/my_ae_plan.md`가 존재할 것

**실행:** `my-copywriter` 서브에이전트를 호출한다.

**전달할 내용:**
- `output/my_ae_plan.md` **전문** (반드시 첨부)
- `.cursor/agents/my-copywriter.md`의 역할·규칙·금지 사항을 따를 것

**완료 조건:**
- 핵심 카피·슬로건 작성 완료
- `output/my_copy.md`에 저장

**사용자에게 알림:**
> ✍️ 2단계 — 카피 작성 중… (AE 기획서 반영)

완료 시:
> ✅ 2단계 완료 — `output/my_copy.md` 저장됨

---

### 3단계: my-reviewer 실행 (1·2단계 결과물 전달) → 검수 결과 저장

**선행 조건:**
- `output/my_ae_plan.md` 존재
- `output/my_copy.md` 존재

**실행:** `my-reviewer` 서브에이전트를 호출한다.

**전달할 내용:**
- `output/my_ae_plan.md` **전문**
- `output/my_copy.md` **전문**
- `.cursor/agents/my-reviewer.md`의 역할·규칙·금지 사항을 따를 것
- **readonly: true** — 산출물을 수정하지 말고 검수·채점만 할 것

**완료 조건:**
- 5개 항목 채점 (각 10점, 총 50점)
- 총점 40점 이상 → 통과 / 미만 → 재작업 지시
- `output/my_review.md`에 검수 결과 저장

**사용자에게 알림:**
> 👔 3단계 — 검수자 채점 중…

완료 시:
> ✅ 3단계 완료 — `output/my_review.md` 저장됨

---

## 최종 마무리

3단계가 모두 끝나면 사용자에게 요약을 전달한다:

1. **총점 및 통과/재작업 판정**
2. **산출물 위치**
   - `output/my_ae_plan.md` — AE 기획서
   - `output/my_copy.md` — 카피
   - `output/my_review.md` — 검수 결과
3. **재작업 필요 시** — my-reviewer가 지시한 담당(AE 또는 카피라이터)과 구체적 보완 사항

---

## 원칙 (위반 금지)

| 규칙 | 이유 |
|------|------|
| AE 없이 카피부터 쓰지 않는다 | 방향이 엇나감 |
| 1단계 결과 없이 2단계 시작 금지 | 카피가 기획과 어긋남 |
| 1·2단계 결과 없이 3단계 시작 금지 | 검수 근거 없음 |
| my-reviewer는 **읽기만** (readonly) | 검수자가 산출물을 직접 고치면 안 됨 |
| 3단계를 건너뛰고 완료 선언 금지 | 검수 없이 배포 불가 |

## 재작업 루프

3단계에서 **40점 미만**이면:

1. `output/my_review.md`의 재작업 지시 확인
2. **AE 보완** → 1단계부터 재실행
3. **카피 보완** → 2단계부터 재실행 (1단계 결과 유지)
4. 보완 후 **3단계 재검수** (최대 1회)

---

## 산출물 경로 요약

| 단계 | 에이전트 | 저장 파일 |
|------|----------|-----------|
| 1 | my-ae | `output/my_ae_plan.md` |
| 2 | my-copywriter | `output/my_copy.md` |
| 3 | my-reviewer | `output/my_review.md` |
