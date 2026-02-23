# MindMBTI - MBTI 기반 심리 분석 서비스

48문항 MBTI 검사와 AI 맞춤 해석, 궁합 분석, 직무 매칭을 제공하는 웹 애플리케이션입니다.

---

## 목차
- [기능 개요](#기능-개요)
- [시스템 구조 (동작 방식)](#시스템-구조-동작-방식)
- [사용 방법](#사용-방법)
- [설치 및 실행](#설치-및-실행)
- [기술 스택](#기술-스택)

---

## 기능 개요

| 메뉴 | 설명 |
|------|------|
| **MBTI 검사** | 48문항 리커트 척도(1~5) 설문 → E/I, S/N, T/F, J/P 4지표 점수 산출 → 16가지 유형 중 결과 도출 |
| **기본 리포트** | 유형별 성격 키워드, 강점, 약점, 스트레스 반응, 의사결정 스타일 |
| **AI 맞춤 해석** | 직업·현재 고민·관계 고민 입력 시 OpenAI로 맞춤 심리 해석 생성 (OPENAI_API_KEY 필요) |
| **궁합 분석** | 두 MBTI 유형 선택 → 관계 유형, 갈등 포인트, 의사소통 전략 제안 |
| **직무 매칭** | MBTI 유형별 추천 직무군 (개발, 기획, 마케팅, 연구, 상담, 예술 등) |
| **AI 커리어 조언** | 현재 직무 + MBTI 기반 강점 활용 전략 AI 생성 |
| **대시보드** | 내 검사 이력 저장, 재검사 비교(레이더 차트) |
| **공유** | 결과 페이지에서 공유 링크 생성·복사, PDF 다운로드 |

---

## 시스템 구조 (동작 방식)

```
[사용자] → [React 프론트엔드 :5174] → [FastAPI 백엔드 :8001] → [SQLite/PostgreSQL]
                    ↓
              /api/* 프록시
```

### 데이터 흐름

1. **회원가입/로그인**  
   이메일·비밀번호로 가입 후 JWT 토큰 발급. 토큰은 브라우저 `localStorage`에 저장되며 이후 인증이 필요한 API 호출 시 `Authorization: Bearer <token>` 헤더로 전달됩니다.

2. **MBTI 검사**  
   - 48문항을 1(전혀 아님)~5(매우 그렇다)로 응답  
   - 각 문항은 E/I, S/N, T/F, J/P 4개 차원 중 하나에 속함  
   - 응답 제출 시 세션 ID 생성, 답변은 DB에 저장  
   - 48문항 완료 시 각 차원별 점수 합산 → 유형 산출(예: INTJ, ENFP)

3. **결과 저장**  
   로그인 상태에서 결과 페이지의 "기록에 저장" 클릭 시 `user_results` 테이블에 저장됩니다. 대시보드에서 과거 결과를 조회하고, 2개 이상 저장 시 재검사 비교 기능을 사용할 수 있습니다.

4. **AI 기능**  
   리포트의 AI 맞춤 해석, AI 커리어 조언은 `OPENAI_API_KEY`가 설정된 경우에만 동작합니다. 미설정 시 해당 기능 호출 시 503 응답이 반환됩니다.

### DB 스키마

- **users**: 회원 정보 (이메일, 비밀번호 해시, 닉네임, 성별, 연령대, 프로필 이미지)
- **mbti_sessions**: 검사 세션 (세션 ID, 48문항 답변 JSON)
- **shares**: 공유 링크 데이터 (공유 ID, 결과 JSON)
- **user_results**: 사용자별 저장된 검사 결과 (세션 ID, 유형, 퍼센트)

---

## 사용 방법

### 1. 홈 화면
- **MBTI 검사하기**: 검사 시작 (로그인 없이 가능)
- **기본 리포트**: 유형별 성격 해석
- **궁합 분석**: 두 유형 궁합 조회
- **직무 매칭**: 유형별 추천 직무
- **대시보드**: 내 검사 이력 (로그인 필요)
- **마이페이지**: 프로필 수정 (로그인 필요)

### 2. MBTI 검사 절차
1. "MBTI 검사하기" 클릭
2. 48문항에 1~5 중 하나 선택 후 "다음" (마지막 문항은 "결과 보기")
3. 결과 페이지에서 MBTI 유형·퍼센트 확인

### 3. 결과 활용
- **기록에 저장**: 로그인 후 클릭 시 대시보드에 저장
- **PDF 다운로드**: 결과 PDF 다운로드
- **공유 링크 만들기**: 링크 생성 후 복사

### 4. AI 맞춤 해석 (리포트)
- 리포트 페이지에서 MBTI 유형 선택
- 직업, 현재 고민, 관계 고민 입력 (선택)
- "AI 해석 생성" 클릭 (API 키 필요)

### 5. AI 커리어 조언 (직무)
- 직무 페이지에서 MBTI 유형·현재 직무 입력
- "AI 조언 받기" 클릭 (API 키 필요)

---

## 설치 및 실행

### 사전 요구사항
- Python 3.10+
- Node.js 18+
- (선택) Docker, Docker Compose

### 환경 설정
프로젝트 루트에 `.env` 파일 생성 (`.env.example` 참고):

```
OPENAI_API_KEY=sk-...                    # AI 기능용 (선택)
DATABASE_URL=sqlite:///./mindmbti.db     # 미설정 시 기본값
```

- **SQLite** (기본): `DATABASE_URL` 생략 또는 `sqlite:///./mindmbti.db`
- **PostgreSQL**: `DATABASE_URL=postgresql://user:pass@host:5432/dbname`

### 로컬 실행

**백엔드:**
```powershell
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

**프론트엔드:**
```powershell
cd frontend
npm install
npm run dev
```

- 프론트: http://localhost:5174  
- API 문서: http://localhost:8001/docs  

### Docker 실행

```powershell
docker compose up --build
```

- 프론트: http://localhost:5174  
- API: http://localhost:8001  
- SQLite DB는 volume에 영구 저장  

### 테스트

```powershell
cd backend
python -m pytest test_main.py -v
```

### DB 마이그레이션 (Alembic)

```powershell
cd backend
python -m alembic revision --autogenerate -m "설명"   # 새 마이그레이션 생성
python -m alembic upgrade head                       # 마이그레이션 적용
python -m alembic downgrade -1                       # 롤백
```

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| 백엔드 | FastAPI, SQLAlchemy, SQLite/PostgreSQL, JWT(bcrypt, python-jose) |
| 프론트엔드 | React, Vite, React Router, Recharts |
| AI | OpenAI API (gpt-4o-mini) |
| DB 마이그레이션 | Alembic |
| PDF | reportlab |

---

## 배포

### Render (무료, Sleep 있음)
자세한 절차는 [DEPLOY.md](DEPLOY.md) 참고.

### Railway (무료 크레딧 $5/월, Sleep 없음)
자세한 절차는 [DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md) 참고.

---

## 오케스트레이터로 단계별 개발

```powershell
cd d:\PMS\scripts\ai-orchestrator
python run.py --code-dir d:\PMS\mindmbti --task d:\PMS\mindmbti\tasks\task-phase-01.md --test-cmd "python -m pytest backend/test_main.py -v"
```

Phase 1 완료 후 → task-phase-02.md → ... 순서대로 진행
