"""
MindMBTI - MBTI 기반 심리 분석 서비스 API
"""
import os
from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
import bcrypt
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from database import get_db, init_db
from models import User, MbtiSession, Share, UserResult


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    pass


app = FastAPI(title="MindMBTI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
SECRET_KEY = "mindmbti-secret-key-change-in-production"
ALGORITHM = "HS256"
security = HTTPBearer(auto_error=False)
security_required = HTTPBearer(auto_error=True)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nickname: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def get_current_user_id(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def get_required_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security_required),
    db: Session = Depends(get_db),
) -> str:
    """로그인 필수 - 인증 실패 시 401"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get("sub")
        if not uid:
            raise HTTPException(status_code=401, detail="인증이 필요합니다")
        user = db.query(User).filter(User.id == uid).first()
        if not user:
            raise HTTPException(status_code=401, detail="인증이 필요합니다")
        return uid
    except JWTError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")


@app.get("/")
def root():
    return {"status": "ok", "service": "MindMBTI"}


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """회원가입 - 이메일, 비밀번호, 닉네임"""
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="이메일이 이미 등록되어 있습니다")
    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    user = User(
        id=user_id, email=req.email, password_hash=password_hash, nickname=req.nickname,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user_id, "email": req.email, "nickname": req.nickname}


@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """로그인 - 이메일, 비밀번호 → JWT 반환"""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not bcrypt.checkpw(req.password.encode(), user.password_hash.encode()):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다")
    token = jwt.encode({"sub": user.id}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/api/auth/logout")
def logout(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """로그아웃 - 클라이언트에서 토큰 삭제"""
    return {"message": "로그아웃되었습니다"}


# --- FR-003: 회원정보 수정 ---
class ProfileUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    gender: Optional[str] = None  # male, female, other, prefer_not_to_say
    age_range: Optional[str] = None  # 10s, 20s, 30s, 40s, 50s, 60+
    profile_image_url: Optional[str] = None


def _user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "nickname": user.nickname,
        "gender": user.gender,
        "age_range": user.age_range,
        "profile_image_url": user.profile_image_url,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@app.get("/api/user/me")
def get_my_profile(user_id: str = Depends(get_required_user_id), db: Session = Depends(get_db)):
    """내 프로필 조회"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다")
    return _user_to_dict(user)


@app.patch("/api/user/me")
def update_my_profile(
    req: ProfileUpdateRequest,
    user_id: str = Depends(get_required_user_id),
    db: Session = Depends(get_db),
):
    """회원정보 수정 - 닉네임, 성별, 연령대, 프로필 이미지 URL"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="회원을 찾을 수 없습니다")
    if req.nickname is not None:
        user.nickname = req.nickname
    if req.gender is not None:
        if req.gender not in ("male", "female", "other", "prefer_not_to_say", ""):
            raise HTTPException(status_code=400, detail="유효하지 않은 성별 값입니다")
        user.gender = req.gender if req.gender else None
    if req.age_range is not None:
        if req.age_range and req.age_range not in ("10s", "20s", "30s", "40s", "50s", "60+", ""):
            raise HTTPException(status_code=400, detail="유효하지 않은 연령대입니다")
        user.age_range = req.age_range if req.age_range else None
    if req.profile_image_url is not None:
        user.profile_image_url = req.profile_image_url if req.profile_image_url else None
    db.commit()
    db.refresh(user)
    return _user_to_dict(user)


# --- Phase 2: MBTI 설문 및 결과 ---
from mbti_questions import MBTI_QUESTIONS


class AnswerItem(BaseModel):
    question_id: int = Field(..., ge=1, le=48)
    value: int = Field(..., ge=1, le=5)


class SubmitRequest(BaseModel):
    session_id: Optional[str] = None
    answers: list[AnswerItem]


@app.get("/api/mbti/questions")
def get_mbti_questions():
    """48문항 MBTI 설문 반환"""
    return {"questions": MBTI_QUESTIONS}


@app.post("/api/mbti/submit")
def submit_mbti(req: SubmitRequest, db: Session = Depends(get_db)):
    """검사 답변 제출, 중간 저장"""
    sid = req.session_id or str(uuid.uuid4())
    answers_dict = {a.question_id: a.value for a in req.answers}
    sess = db.query(MbtiSession).filter(MbtiSession.id == sid).first()
    if sess:
        sess.answers = answers_dict
        sess.updated_at = datetime.utcnow()
    else:
        sess = MbtiSession(id=sid, answers=answers_dict)
        db.add(sess)
    db.commit()
    return {"session_id": sid, "saved": len(answers_dict)}


def _compute_mbti_result(answers: dict[int, int]) -> dict:
    """점수 기반 MBTI 유형 계산"""
    dim_scores: dict[str, dict[str, float]] = {
        "E/I": {"E": 0.0, "I": 0.0},
        "S/N": {"S": 0.0, "N": 0.0},
        "T/F": {"T": 0.0, "F": 0.0},
        "J/P": {"J": 0.0, "P": 0.0},
    }
    q_by_dim = {}
    for q in MBTI_QUESTIONS:
        dim = q["dimension"]
        if dim not in q_by_dim:
            q_by_dim[dim] = []
        q_by_dim[dim].append(q)
    for dim, poles in dim_scores.items():
        for q in q_by_dim.get(dim, []):
            qid, pos = q["id"], q["positive_pole"]
            neg = dim.split("/")[1] if pos == dim[0] else dim[0]
            val = answers.get(qid, 3)
            poles[pos] += val
            poles[neg] += 6 - val
    mbti_type = ""
    percentages = {}
    for dim, poles in dim_scores.items():
        a, b = dim[0], dim[2]
        sa, sb = poles[a], poles[b]
        total = sa + sb
        mbti_type += a if sa >= sb else b
        pct = round((sa / total * 100) if total > 0 else 50, 1)
        percentages[dim] = {a: pct, b: round(100 - pct, 1)}
    return {"type": mbti_type, "percentages": percentages}


@app.get("/api/mbti/result/{session_id}")
def get_mbti_result(session_id: str, db: Session = Depends(get_db)):
    """MBTI 결과 조회 - 유형 + 퍼센트"""
    sess = db.query(MbtiSession).filter(MbtiSession.id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
    answers = sess.answers or {}
    if len(answers) < 48:
        raise HTTPException(status_code=400, detail="모든 문항에 답변해 주세요")
    result = _compute_mbti_result(answers)
    return {"session_id": session_id, **result}


# --- Phase 3: 심리 분석 리포트 ---
from report_templates import MBTI_REPORTS, VALID_MBTI_TYPES


@app.get("/api/report/basic/{mbti_type}")
def get_basic_report(mbti_type: str):
    """MBTI 유형별 기본 리포트 - 성격 키워드, 강점, 약점, 스트레스 반응, 의사결정 스타일"""
    key = mbti_type.upper()
    if key not in VALID_MBTI_TYPES:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 MBTI 유형: {mbti_type}")
    return {"mbti_type": key, **MBTI_REPORTS[key]}


class AiReportRequest(BaseModel):
    mbti_type: str
    job: Optional[str] = None
    current_concern: Optional[str] = None
    relationship_concern: Optional[str] = None


@app.post("/api/report/ai")
def generate_ai_report(req: AiReportRequest):
    """AI 맞춤 해석 생성 - 직업, 현재 고민, 관계 고민 기반"""
    key = req.mbti_type.upper()
    if key not in VALID_MBTI_TYPES:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 MBTI 유형: {req.mbti_type}")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY가 설정되지 않았습니다. 관리자에게 문의하세요.")

    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    base_info = MBTI_REPORTS[key]
    user_input = []
    if req.job:
        user_input.append(f"직업: {req.job}")
    if req.current_concern:
        user_input.append(f"현재 고민: {req.current_concern}")
    if req.relationship_concern:
        user_input.append(f"관계 고민: {req.relationship_concern}")
    prompt = f"""당신은 MBTI 기반 심리 분석 전문가입니다.
사용자의 MBTI 유형은 {key}이며, 기본 성격 특성은 다음과 같습니다:
- 키워드: {', '.join(base_info['keywords'])}
- 강점: {base_info['strengths']}
- 약점: {base_info['weaknesses']}
- 스트레스 반응: {base_info['stress_reaction']}
- 의사결정 스타일: {base_info['decision_style']}

사용자 입력:
{chr(10).join(user_input) if user_input else '(추가 입력 없음)'}

위 정보를 바탕으로 200자 내외로 맞춤 심리 해석을 작성해 주세요. 따뜻하고 구체적으로 작성하며, 한국어로 답변하세요."""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        text = resp.choices[0].message.content
        return {"mbti_type": key, "ai_interpretation": text}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI 생성 중 오류: {str(e)}")


# --- FR-022: PDF 다운로드 & 공유 링크 ---
class ShareRequest(BaseModel):
    session_id: str


def _get_full_result(db: Session, session_id: str) -> dict | None:
    """세션 결과 + 기본 리포트 조합"""
    sess = db.query(MbtiSession).filter(MbtiSession.id == session_id).first()
    if not sess or len(sess.answers or {}) < 48:
        return None
    result = _compute_mbti_result(sess.answers)
    key = result.get("type", "")
    report = MBTI_REPORTS.get(key, {}) if key in VALID_MBTI_TYPES else {}
    return {**result, "session_id": session_id, "report": report}


@app.post("/api/share")
def create_share(req: ShareRequest, db: Session = Depends(get_db)):
    """공유 링크 생성 - session_id로 결과 저장 후 share_id 반환"""
    data = _get_full_result(db, req.session_id)
    if not data:
        raise HTTPException(status_code=400, detail="완료된 검사 결과가 없습니다")
    share_id = str(uuid.uuid4())[:8]
    rec = Share(id=share_id, data=data)
    db.add(rec)
    db.commit()
    return {"share_id": share_id, "share_url": f"/share/{share_id}"}


@app.get("/api/share/{share_id}")
def get_share(share_id: str, db: Session = Depends(get_db)):
    """공유된 결과 조회"""
    rec = db.query(Share).filter(Share.id == share_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="공유 링크를 찾을 수 없습니다")
    return rec.data


@app.get("/api/share/{share_id}/pdf")
def download_share_pdf(share_id: str, db: Session = Depends(get_db)):
    """공유 결과 PDF 다운로드"""
    rec = db.query(Share).filter(Share.id == share_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="공유 링크를 찾을 수 없습니다")
    data = rec.data
    from pdf_utils import create_mbti_pdf
    pdf_bytes = create_mbti_pdf(
        data.get("type", ""),
        data.get("percentages", {}),
        data.get("report", {}),
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="MindMBTI_{data.get("type", "result")}.pdf"'},
    )


# session_id로 직접 PDF 다운로드 (공유 없이)
@app.get("/api/mbti/result/{session_id}/pdf")
def download_result_pdf(session_id: str, db: Session = Depends(get_db)):
    """검사 결과 PDF 다운로드"""
    data = _get_full_result(db, session_id)
    if not data:
        raise HTTPException(status_code=400, detail="완료된 검사 결과가 없습니다")
    from pdf_utils import create_mbti_pdf
    pdf_bytes = create_mbti_pdf(
        data.get("type", ""),
        data.get("percentages", {}),
        data.get("report", {}),
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="MindMBTI_{data.get("type", "result")}.pdf"'},
    )


# --- Phase 4: 궁합 분석 & 직무 적합도 ---
from compatibility import analyze_compatibility
from career_match import get_career_recommendations


class CompatibilityRequest(BaseModel):
    type_a: str
    type_b: str


@app.post("/api/compatibility")
def compatibility(req: CompatibilityRequest):
    """MBTI 궁합 분석 - 관계 유형, 갈등 포인트, 의사소통 전략"""
    try:
        return analyze_compatibility(req.type_a, req.type_b)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/career/match/{mbti_type}")
def career_match(mbti_type: str):
    """직무 매칭 - MBTI 유형별 직무군 추천"""
    try:
        return get_career_recommendations(mbti_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- FR-041: AI 커리어 조언 ---
class CareerAdviceRequest(BaseModel):
    mbti_type: str
    current_job: str


@app.post("/api/career/ai-advice")
def get_ai_career_advice(req: CareerAdviceRequest):
    """AI 커리어 조언 - 현재 직무 + MBTI 기반, 강점 활용 전략 제안"""
    key = req.mbti_type.upper()
    if key not in VALID_MBTI_TYPES:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 MBTI 유형: {req.mbti_type}")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY가 설정되지 않았습니다.")

    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    base_info = MBTI_REPORTS[key]
    careers = get_career_recommendations(key)["recommended_careers"]

    prompt = f"""당신은 MBTI 기반 커리어 코치입니다.
사용자 정보:
- MBTI: {key}
- 현재 직무: {req.current_job}
- 성격 키워드: {', '.join(base_info['keywords'])}
- 강점: {base_info['strengths']}
- 약점: {base_info['weaknesses']}
- 추천 직무군: {', '.join(careers)}

다음 두 가지를 각각 150자 내외로 한국어로 작성해 주세요. JSON 형식으로만 답변하세요.
{{"career_advice": "현재 직무에서의 성장 방향, MBTI 강점을 활용한 조언",
 "strength_strategy": "강점 활용 전략 2~3가지 구체적 제안"}}"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
        )
        import json
        text = (resp.choices[0].message.content or "").strip()
        text = text.removeprefix("```json").removeprefix("```").strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = {"career_advice": text, "strength_strategy": ""}
        return {
            "mbti_type": key,
            "current_job": req.current_job,
            "career_advice": data.get("career_advice", text),
            "strength_strategy": data.get("strength_strategy", ""),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI 생성 중 오류: {str(e)}")


# --- FR-050: 대시보드 - 내 분석 기록, 재검사 비교 ---
class DashboardSaveRequest(BaseModel):
    session_id: str


def _result_to_record(r: UserResult) -> dict:
    return {
        "session_id": r.session_id,
        "type": r.mbti_type,
        "percentages": r.percentages,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


@app.post("/api/dashboard/save")
def save_result_to_history(
    req: DashboardSaveRequest,
    user_id: str = Depends(get_required_user_id),
    db: Session = Depends(get_db),
):
    """검사 결과를 내 기록에 저장"""
    sess = db.query(MbtiSession).filter(MbtiSession.id == req.session_id).first()
    if not sess or len(sess.answers or {}) < 48:
        raise HTTPException(status_code=400, detail="완료된 검사 결과가 없습니다")
    result = _compute_mbti_result(sess.answers)
    rec = UserResult(
        id=str(uuid.uuid4()),
        user_id=user_id,
        session_id=req.session_id,
        mbti_type=result["type"],
        percentages=result["percentages"],
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    record = _result_to_record(rec)
    return {"saved": True, "record": record}


@app.get("/api/dashboard/history")
def get_my_history(user_id: str = Depends(get_required_user_id), db: Session = Depends(get_db)):
    """과거 검사 이력 조회 (최신순)"""
    rows = db.query(UserResult).filter(UserResult.user_id == user_id).order_by(UserResult.created_at.desc()).all()
    records = [_result_to_record(r) for r in rows]
    return {"history": records}


@app.get("/api/dashboard/compare")
def compare_results(
    session_a: str,
    session_b: str,
    user_id: str = Depends(get_required_user_id),
    db: Session = Depends(get_db),
):
    """재검사 비교 - 두 결과의 MBTI 변화, 지표별 변화"""
    ra = db.query(UserResult).filter(UserResult.user_id == user_id, UserResult.session_id == session_a).first()
    rb = db.query(UserResult).filter(UserResult.user_id == user_id, UserResult.session_id == session_b).first()
    if not ra or not rb:
        raise HTTPException(status_code=400, detail="저장된 결과를 찾을 수 없습니다. 먼저 기록에 저장하세요.")
    dims = ["E/I", "S/N", "T/F", "J/P"]
    changes = []
    for dim in dims:
        pa = (ra.percentages or {}).get(dim, {})
        pb = (rb.percentages or {}).get(dim, {})
        a_first = dim[0]
        da = (pb.get(a_first, 50) or 50) - (pa.get(a_first, 50) or 50)
        changes.append({"dimension": dim, "change": round(da, 1), "before": pa, "after": pb})
    return {
        "result_a": {"session_id": session_a, "type": ra.mbti_type, "created_at": ra.created_at.isoformat() if ra.created_at else None},
        "result_b": {"session_id": session_b, "type": rb.mbti_type, "created_at": rb.created_at.isoformat() if rb.created_at else None},
        "type_changed": ra.mbti_type != rb.mbti_type,
        "dimension_changes": changes,
    }
