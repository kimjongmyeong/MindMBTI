# MindMBTI Render 배포 가이드

Render.com에서 무료로 배포하는 방법입니다.

## 사전 준비

1. [Render](https://render.com) 계정 생성
2. GitHub에 mindmbti 저장소 Push (또는 GitLab/Bitbucket)
3. OpenAI API 키 (AI 리포트/커리어 조언용, 선택)

---

## 방법 1: Blueprint 한 번에 배포

### 1단계: Render 연결

1. [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint**
2. 저장소 연결 (GitHub/GitLab 선택 후 mindmbti 저장소 선택)
3. Render가 `render.yaml`을 감지하고 `Create Blueprint` 표시

### 2단계: 환경 변수 입력

Blueprint 생성 시 다음 항목을 **직접 입력**해야 합니다:

| 서비스 | 키 | 설명 |
|--------|-----|------|
| mindmbti-api | OPENAI_API_KEY | OpenAI API 키 (선택, 없으면 AI 기능 비활성화) |
| mindmbti-api | SECRET_KEY | 자동 생성됨 (generateValue: true) |
| mindmbti-web | VITE_API_URL | 백엔드 URL (기본값 사용 가능) |

**VITE_API_URL**  
- 기본값: `https://mindmbti-api.onrender.com`
- 백엔드 배포 후 실제 URL이 다르면 (예: `https://mindmbti-api-xxxx.onrender.com`) Dashboard에서 수정

### 3단계: 배포 실행

1. **Apply** 클릭
2. PostgreSQL DB, 백엔드, 프론트엔드 순으로 프로비저닝
3. 완료 후 `mindmbti-web` 서비스 URL로 접속

---

## API 연결 안 될 때 (모든 기능/로딩 실패)

**증상**: MBTI 검사, 로그인 등 모든 기능이 동작하지 않거나 매우 느림

**원인**: 프론트엔드가 잘못된 백엔드 URL로 호출 중

**해결**:

1. **Render Dashboard** → **Resources** → **mindmbti-api** 클릭
2. 상단 **URL** 확인 (예: `https://mindmbti-api-xyz12.onrender.com`)
3. **mindmbti-web** 서비스 클릭 → **Environment** 탭
4. **VITE_API_URL** 환경 변수 확인
   - 실제 mindmbti-api URL과 다르면 → 값 수정 후 **Save Changes**
5. **Manual Deploy** → **Deploy latest commit** (프론트엔드 재빌드)

---

## 방법 2: 수동 배포 (항목별 생성)

### 1. PostgreSQL 데이터베이스

1. **New** → **PostgreSQL**
2. Name: `mindmbti-db`
3. Plan: **Free**
4. 생성 후 **Connection String** (Internal) 복사

### 2. 백엔드 (Web Service)

1. **New** → **Web Service**
2. 저장소 연결, **Root Directory**: `backend`
3. 설정:
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Pre-Deploy Command**: `python -m alembic upgrade head`

4. 환경 변수:
   | Key | Value |
   |-----|-------|
   | DATABASE_URL | (PostgreSQL Connection String 붙여넣기) |
   | OPENAI_API_KEY | sk-... (선택) |
   | SECRET_KEY | (아무 긴 문자열 또는 Dashboard에서 Generate) |

5. **Create Web Service** → 배포 완료 후 URL 확인 (예: `https://mindmbti-api.onrender.com`)

### 3. 프론트엔드 (Static Site)

1. **New** → **Static Site**
2. 저장소 연결, **Root Directory**: `frontend`
3. 설정:
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. 환경 변수:
   | Key | Value |
   |-----|-------|
   | VITE_API_URL | `https://mindmbti-api.onrender.com` (백엔드 URL로 변경) |

5. **Create Static Site** → 배포 완료 후 URL로 접속

---

## 배포 후 확인

- 프론트엔드: `https://mindmbti-web.onrender.com` (또는 할당된 URL)
- API 문서: `https://mindmbti-api.onrender.com/docs`

---

## 주의사항

### 무료 플랜 제한
- **Sleep**: 15분 비활성 시 서비스가 Sleep → 첫 요청 시 30초~1분 대기
- **PostgreSQL**: 무료 DB는 90일 후 삭제 (데이터 백업 필요)
- **빌드 시간**: 무료 플랜은 월 빌드 시간 제한 있음

### CORS
백엔드는 `allow_origins=["*"]`로 설정되어 있어 다른 도메인에서의 API 호출이 가능합니다.

### SECRET_KEY
운영 환경에서는 `SECRET_KEY`를 안전한 값으로 설정하세요. Blueprint의 `generateValue: true`는 자동 생성된 값을 사용합니다.
