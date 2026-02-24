# MindMBTI Railway 배포 가이드

Railway는 Sleep 없이 무료 크레딧($5/월)으로 배포합니다.

---

## 사전 준비

1. [Railway](https://railway.app) 계정 (GitHub 로그인)
2. GitHub에 mindmbti 저장소 push 완료

---

## 1단계: 프로젝트 생성

1. [railway.com/new](https://railway.com/new) 접속
2. **Deploy from GitHub repo** 선택
3. **kimjongmyeong/MindMBTI** 저장소 선택
4. **Add variables**는 나중에 설정 → **Deploy** (일단 건너뛰고 진행 가능)

---

## 2단계: PostgreSQL 추가

1. 프로젝트 대시보드에서 **+ New** → **Database** → **PostgreSQL**
2. 생성 후 **PostgreSQL** 서비스 클릭
3. **Variables** 탭 → **DATABASE_URL** 확인 (또는 **Connect** 탭에서 복사)
4. 이 값을 백엔드 서비스에 연결

---

## 3단계: 백엔드 서비스 설정

1. **+ New** → **GitHub Repo** → 같은 저장소(MindMBTI) 선택
2. 새로 생긴 서비스 클릭 → **Settings**
3. **Source** 섹션:
   - **Root Directory**: `backend` ← **필수!** (미설정 시 `pip: not found` 발생)
   - **Config file path**: `backend/railway.json` (저장소 루트 기준 경로)
4. **Build** 섹션 (있을 경우):
   - **Builder**: `Dockerfile` 로 설정
5. **Variables** 섹션:
   - **DATABASE_URL**: PostgreSQL 서비스의 Variables에서 **Add variable reference** → `DATABASE_URL` 연결
   - **OPENAI_API_KEY**: (선택) `sk-...`
   - **SECRET_KEY**: 아무 긴 문자열 (예: `railway-mindmbti-secret-xxx`)
   - **RAILWAY_DOCKERFILE_PATH**: `Dockerfile` ← pip 오류 시 Dockerfile 강제 사용
5. **Networking** → **Generate Domain** → URL 확인 (예: `mindmbti-api-production.up.railway.app`)
6. **이 URL을 메모해 두세요** (프론트엔드 설정에 사용)

---

## 4단계: 프론트엔드 서비스 설정

1. **+ New** → **GitHub Repo** → 같은 저장소(MindMBTI) 선택
2. 새로 생긴 서비스 클릭 → **Settings**
3. **Source** 섹션:
   - **Root Directory**: `frontend`
   - **Config file path** (선택): `frontend/railway.json`
4. **Variables** 섹션:
   - **VITE_API_URL**: `https://[3단계에서 메모한 백엔드 URL]/api` ← 끝에 `/api` **필수**
     - 예: `https://mindmbti-api-production.up.railway.app/api`
5. **Networking** → **Generate Domain** → 프론트엔드 URL 확인

---

## 5단계: 배포 확인

- **백엔드**: `https://[백엔드-도메인]/api/health` → `{"ok":true}` 확인
- **프론트엔드**: `https://[프론트엔드-도메인]` 접속 후 회원가입, MBTI 검사 테스트

---

## 비용

- **무료 크레딧**: 월 $5
- 소규모 트래픽 기준으로 수 개월 무료 사용 가능
- 크레딧 소진 시 결제 수단 등록 후 사용량 과금

---

## 트러블슈팅

| 증상 | 해결 |
|------|------|
| `pip: not found` / Build 실패 | 1) Root Directory가 `backend`인지 확인<br>2) Variables에 `RAILWAY_DOCKERFILE_PATH=Dockerfile` 추가<br>3) Settings → Build에서 Builder를 `Dockerfile`로 지정 |
| **Healthcheck failure** | 1) `railway.json`에 `healthcheckTimeout: 600` 반영 후 재배포<br>2) Variables에 `RAILWAY_HEALTHCHECK_TIMEOUT_SEC=600` 추가 (대안)<br>3) **DATABASE_URL** 연결 확인 (미연결 시 앱 시작 실패)<br>4) Deployments → View logs에서 앱 시작 오류 확인 |
| 프론트에서 API 호출 실패 | VITE_API_URL이 `https://[백엔드-도메인]/api` 형식인지 확인 (끝에 `/api` 필수) |
| DB 연결 오류 | 백엔드 Variables에 DATABASE_URL이 PostgreSQL에서 **변수 참조**로 연결되어 있는지 확인 |
| 빌드 실패 | 해당 서비스 Logs 탭에서 에러 메시지 확인 |
