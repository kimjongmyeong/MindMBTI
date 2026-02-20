# Phase 1: 회원 관리 기반

## 구현 항목

### FR-001 회원가입 (이메일 기반)
- `POST /api/auth/register` - 이메일, 비밀번호, 닉네임
- 비밀번호 해시 저장 (bcrypt)
- 이메일 중복 검사

### FR-002 로그인/로그아웃
- `POST /api/auth/login` - 이메일, 비밀번호 → JWT 반환
- `POST /api/auth/logout` - (클라이언트에서 토큰 삭제)

### 데이터
- 메모리 dict로 User 저장 (추후 DB 연동)
- User: id, email, password_hash, nickname, created_at

### 테스트
- 회원가입 API 테스트
- 로그인 API 테스트
