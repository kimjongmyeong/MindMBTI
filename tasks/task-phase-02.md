# Phase 2: MBTI 설문 및 결과 산출

## 전제: Phase 1 완료

## 구현 항목

### FR-010 MBTI 설문 제공
- `GET /api/mbti/questions` - 48문항 반환 (4지표 x 12문항)
- 각 문항: id, dimension (E/I, S/N, T/F, J/P), text, (1~5 Likert)

### FR-011 검사 진행
- `POST /api/mbti/submit` - 문항별 답변 배열 전송
- 중간 저장 (session_id로)

### FR-012 MBTI 결과 산출
- 점수 기반 유형 계산 (각 지표별 E vs I, S vs N 등)
- `GET /api/mbti/result/{session_id}` - 유형 + 퍼센트
- 예: ENFP (E 63%, N 71%, F 55%, P 60%)
