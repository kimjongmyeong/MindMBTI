"""
MBTI 유형별 직무 적합도
"""
from report_templates import VALID_MBTI_TYPES

# 직무군: 개발, 기획, 마케팅, 연구, 상담, 예술, 관리, 영업, 디자인, 교육 등
CAREER_MATCH = {
    "INTJ": ["연구", "기획", "개발", "전략", "컨설팅"],
    "INTP": ["연구", "개발", "기획", "분석", "학술"],
    "ENTJ": ["관리", "기획", "컨설팅", "법률", "경영"],
    "ENTP": ["기획", "마케팅", "창업", "컨설팅", "영업"],
    "INFJ": ["상담", "교육", "예술", "사회복지", "작가"],
    "INFP": ["예술", "상담", "작가", "교육", "사회복지"],
    "ENFJ": ["교육", "상담", "HR", "마케팅", "사회복지"],
    "ENFP": ["마케팅", "교육", "상담", "예술", "미디어"],
    "ISTJ": ["회계", "관리", "법률", "공공", "의료"],
    "ISFJ": ["의료", "교육", "행정", "사회복지", "사서"],
    "ESTJ": ["관리", "경영", "법률", "영업", "공공"],
    "ESFJ": ["교육", "의료", "HR", "고객서비스", "행정"],
    "ISTP": ["개발", "엔지니어", "정비", "경영", "조사"],
    "ISFP": ["예술", "디자인", "의료", "요리", "재능"],
    "ESTP": ["영업", "마케팅", "스포츠", "경영", "응급"],
    "ESFP": ["연예", "마케팅", "영업", "이벤트", "고객서비스"],
}


def get_career_recommendations(mbti_type: str) -> dict:
    """MBTI 유형별 직무군 추천"""
    key = mbti_type.upper()
    if key not in VALID_MBTI_TYPES:
        raise ValueError(f"유효하지 않은 MBTI 유형: {mbti_type}")
    return {"mbti_type": key, "recommended_careers": CAREER_MATCH[key]}
