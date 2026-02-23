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
   - **Root Directory**: `backend`
   - **Config file path** (선택): `backend/railway.json`
4. **Variables** 섹션:
   - **DATABASE_URL**: PostgreSQL 서비스의 Variables에서 **Add variable reference** → `DATABASE_URL` 연결
   - **OPENAI_API_KEY**: (선택) `sk-...`
   - **SECRET_KEY**: 아무 긴 문자열 (예: `railway-mindmbti-secret-xxx`)
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
   - **VITE_API_URL**: `https://[3단계에서 메모한 백엔드 URL]`
     - 예: `https://mindmbti-api-production.up.railway.app`
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
| 프론트에서 API 호출 실패 | VITE_API_URL이 백엔드 URL과 정확히 일치하는지 확인 |
| DB 연결 오류 | 백엔드 Variables에 DATABASE_URL이 연결되어 있는지 확인 |
| 빌드 실패 | 해당 서비스 Logs 탭에서 에러 메시지 확인 |
