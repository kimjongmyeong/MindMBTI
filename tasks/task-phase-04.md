# Phase 4: 궁합 분석 & 직무 적합도

## 전제: Phase 3 완료

## 구현 항목

### FR-030 MBTI 궁합 분석
- `POST /api/compatibility` - type_a, type_b
- 관계 유형 분류 (이상적/보완적/갈등 가능성)
- 갈등 포인트, 의사소통 전략

### FR-040 직무 매칭
- `GET /api/career/match/{mbti_type}` - 직무군 추천
- 개발, 기획, 마케팅, 연구, 상담, 예술 등
