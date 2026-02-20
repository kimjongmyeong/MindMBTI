"""MindMBTI API 테스트"""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "MindMBTI" in r.json().get("service", "")


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json().get("ok") is True


def test_register():
    r = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "test1234", "nickname": "테스터"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "test@example.com"
    assert data["nickname"] == "테스터"
    assert "id" in data


def test_register_duplicate_email():
    client.post("/api/auth/register", json={"email": "dup@example.com", "password": "pwd", "nickname": "A"})
    r = client.post("/api/auth/register", json={"email": "dup@example.com", "password": "pwd2", "nickname": "B"})
    assert r.status_code == 400
    assert "이미 등록" in r.json().get("detail", "")


def test_login():
    client.post("/api/auth/register", json={"email": "login@example.com", "password": "secret", "nickname": "L"})
    r = client.post("/api/auth/login", json={"email": "login@example.com", "password": "secret"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    client.post("/api/auth/register", json={"email": "wrong@example.com", "password": "right", "nickname": "W"})
    r = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "wrong"})
    assert r.status_code == 401


# --- FR-003: 회원정보 수정 ---
def test_get_profile_unauthorized():
    r = client.get("/api/user/me")
    assert r.status_code in (401, 403)  # 인증 없을 때


def test_get_and_update_profile():
    client.post("/api/auth/register", json={"email": "profile@example.com", "password": "pwd", "nickname": "초기"})
    r = client.post("/api/auth/login", json={"email": "profile@example.com", "password": "pwd"})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r2 = client.get("/api/user/me", headers=headers)
    assert r2.status_code == 200
    assert r2.json()["nickname"] == "초기"
    assert r2.json()["email"] == "profile@example.com"

    r3 = client.patch(
        "/api/user/me",
        headers=headers,
        json={"nickname": "수정됨", "gender": "male", "age_range": "20s", "profile_image_url": "https://example.com/img.png"},
    )
    assert r3.status_code == 200
    data = r3.json()
    assert data["nickname"] == "수정됨"
    assert data["gender"] == "male"
    assert data["age_range"] == "20s"
    assert data["profile_image_url"] == "https://example.com/img.png"


def test_update_profile_invalid_gender():
    client.post("/api/auth/register", json={"email": "invalid@example.com", "password": "pwd", "nickname": "A"})
    r = client.post("/api/auth/login", json={"email": "invalid@example.com", "password": "pwd"})
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r2 = client.patch("/api/user/me", headers=headers, json={"gender": "invalid"})
    assert r2.status_code == 400


# --- Phase 2: MBTI 설문 및 결과 ---
def test_mbti_questions():
    r = client.get("/api/mbti/questions")
    assert r.status_code == 200
    qs = r.json()["questions"]
    assert len(qs) == 48
    assert all("id" in q and "dimension" in q and "text" in q for q in qs)
    dims = {q["dimension"] for q in qs}
    assert dims == {"E/I", "S/N", "T/F", "J/P"}


def test_mbti_submit_and_result():
    answers = [{"question_id": i, "value": 3} for i in range(1, 49)]
    r = client.post("/api/mbti/submit", json={"answers": answers})
    assert r.status_code == 200
    sid = r.json()["session_id"]
    assert r.json()["saved"] == 48

    r2 = client.get(f"/api/mbti/result/{sid}")
    assert r2.status_code == 200
    data = r2.json()
    assert "type" in data
    assert len(data["type"]) == 4
    assert data["type"].isalpha()
    assert "percentages" in data
    for dim in ["E/I", "S/N", "T/F", "J/P"]:
        assert dim in data["percentages"]


def test_mbti_result_incomplete():
    answers = [{"question_id": i, "value": 3} for i in range(1, 30)]
    r = client.post("/api/mbti/submit", json={"answers": answers})
    sid = r.json()["session_id"]
    r2 = client.get(f"/api/mbti/result/{sid}")
    assert r2.status_code == 400


def test_mbti_result_not_found():
    r = client.get("/api/mbti/result/nonexistent-session-id")
    assert r.status_code == 404


# --- Phase 3: 심리 분석 리포트 ---
def test_basic_report():
    r = client.get("/api/report/basic/ENFP")
    assert r.status_code == 200
    data = r.json()
    assert data["mbti_type"] == "ENFP"
    assert len(data["keywords"]) == 5
    assert "strengths" in data
    assert "weaknesses" in data
    assert "stress_reaction" in data
    assert "decision_style" in data


def test_basic_report_invalid():
    r = client.get("/api/report/basic/XXXX")
    assert r.status_code == 400


def test_basic_report_case_insensitive():
    r = client.get("/api/report/basic/infp")
    assert r.status_code == 200
    assert r.json()["mbti_type"] == "INFP"


@patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test-key"})
@patch("openai.OpenAI")
def test_ai_report(mock_openai):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="테스트 AI 해석입니다."))]
    )
    mock_openai.return_value = mock_client

    r = client.post(
        "/api/report/ai",
        json={
            "mbti_type": "INTJ",
            "job": "개발자",
            "current_concern": "커리어 전환",
            "relationship_concern": "팀 커뮤니케이션",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["mbti_type"] == "INTJ"
    assert "ai_interpretation" in data
    assert "테스트 AI 해석" in data["ai_interpretation"]


@patch("main.os.getenv", return_value="")
def test_ai_report_no_api_key(mock_getenv):
    r = client.post(
        "/api/report/ai",
        json={"mbti_type": "ENFP", "job": "디자이너"},
    )
    assert r.status_code == 503


# --- Phase 4: 궁합 분석 & 직무 적합도 ---
def test_compatibility():
    r = client.post("/api/compatibility", json={"type_a": "ENFP", "type_b": "INTJ"})
    assert r.status_code == 200
    data = r.json()
    assert data["type_a"] == "ENFP"
    assert data["type_b"] == "INTJ"
    assert data["relationship_type"] in ["이상적", "보완적", "갈등 가능성"]
    assert "conflict_points" in data
    assert "communication_strategy" in data
    assert "long_term_tips" in data
    assert len(data["long_term_tips"]) >= 2


def test_compatibility_invalid():
    r = client.post("/api/compatibility", json={"type_a": "ENFP", "type_b": "XXXX"})
    assert r.status_code == 400


def test_career_match():
    r = client.get("/api/career/match/INTJ")
    assert r.status_code == 200
    data = r.json()
    assert data["mbti_type"] == "INTJ"
    assert "recommended_careers" in data
    assert len(data["recommended_careers"]) >= 5


def test_career_match_invalid():
    r = client.get("/api/career/match/INVALID")
    assert r.status_code == 400


@patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test-key"})
@patch("openai.OpenAI")
def test_ai_career_advice(mock_openai):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"career_advice": "테스트 조언", "strength_strategy": "강점 전략"}'))]
    )
    mock_openai.return_value = mock_client
    r = client.post(
        "/api/career/ai-advice",
        json={"mbti_type": "INTJ", "current_job": "개발자"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["mbti_type"] == "INTJ"
    assert data["current_job"] == "개발자"
    assert "career_advice" in data
    assert "strength_strategy" in data


@patch("main.os.getenv", return_value="")
def test_ai_career_advice_no_key(mock_getenv):
    r = client.post("/api/career/ai-advice", json={"mbti_type": "ENFP", "current_job": "디자이너"})
    assert r.status_code == 503


# --- FR-050: 대시보드 ---
def test_dashboard_save_and_history():
    client.post("/api/auth/register", json={"email": "dash@example.com", "password": "pwd", "nickname": "D"})
    r = client.post("/api/auth/login", json={"email": "dash@example.com", "password": "pwd"})
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    answers = [{"question_id": i, "value": 3} for i in range(1, 49)]
    sub = client.post("/api/mbti/submit", json={"answers": answers})
    sid = sub.json()["session_id"]

    r2 = client.post("/api/dashboard/save", headers=headers, json={"session_id": sid})
    assert r2.status_code == 200
    assert r2.json()["saved"] is True

    r3 = client.get("/api/dashboard/history", headers=headers)
    assert r3.status_code == 200
    hist = r3.json()["history"]
    assert len(hist) >= 1
    assert hist[0]["type"] in ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
                               "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]


def test_dashboard_compare():
    client.post("/api/auth/register", json={"email": "comp@example.com", "password": "pwd", "nickname": "C"})
    r = client.post("/api/auth/login", json={"email": "comp@example.com", "password": "pwd"})
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    ans1 = [{"question_id": i, "value": 2} for i in range(1, 49)]
    ans2 = [{"question_id": i, "value": 4} for i in range(1, 49)]
    s1 = client.post("/api/mbti/submit", json={"answers": ans1}).json()["session_id"]
    s2 = client.post("/api/mbti/submit", json={"answers": ans2}).json()["session_id"]
    client.post("/api/dashboard/save", headers=headers, json={"session_id": s1})
    client.post("/api/dashboard/save", headers=headers, json={"session_id": s2})

    r2 = client.get(f"/api/dashboard/compare?session_a={s1}&session_b={s2}", headers=headers)
    assert r2.status_code == 200
    data = r2.json()
    assert "result_a" in data
    assert "result_b" in data
    assert "dimension_changes" in data


# --- FR-022: PDF & 공유 링크 ---
def test_share_and_pdf():
    answers = [{"question_id": i, "value": 3} for i in range(1, 49)]
    r = client.post("/api/mbti/submit", json={"answers": answers})
    sid = r.json()["session_id"]

    r2 = client.post("/api/share", json={"session_id": sid})
    assert r2.status_code == 200
    share_id = r2.json()["share_id"]
    assert "share_url" in r2.json()

    r3 = client.get(f"/api/share/{share_id}")
    assert r3.status_code == 200
    data = r3.json()
    assert "type" in data
    assert "percentages" in data
    assert "report" in data

    r4 = client.get(f"/api/share/{share_id}/pdf")
    assert r4.status_code == 200
    assert r4.headers.get("content-type", "").startswith("application/pdf")
    assert len(r4.content) > 100

    r5 = client.get(f"/api/mbti/result/{sid}/pdf")
    assert r5.status_code == 200
    assert r5.headers.get("content-type", "").startswith("application/pdf")
