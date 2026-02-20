# Phase 3: 심리 분석 리포트

## 전제: Phase 2 완료

## 구현 항목

### FR-020 기본 리포트
- MBTI 유형별 고정 템플릿
- 성격 키워드 5개, 강점, 약점, 스트레스 반응, 의사결정 스타일
- `GET /api/report/basic/{mbti_type}`

### FR-021 AI 확장 해석
- OpenAI/Claude API 호출
- 사용자 입력: 직업, 현재 고민, 관계 고민
- `POST /api/report/ai` - 맞춤 해석 생성
