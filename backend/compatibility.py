"""
MBTI 궁합 분석 - 관계 유형, 갈등 포인트, 의사소통 전략
"""
from report_templates import VALID_MBTI_TYPES

RELATIONSHIP_TYPES = {
    "ideal": "이상적",
    "complementary": "보완적",
    "challenging": "갈등 가능성",
}


def _count_same_dimensions(type_a: str, type_b: str) -> int:
    """동일한 극을 가진 지표 개수 (0~4)"""
    return sum(1 for a, b in zip(type_a.upper(), type_b.upper()) if a == b)


def get_relationship_type(type_a: str, type_b: str) -> str:
    """관계 유형 분류"""
    a, b = type_a.upper(), type_b.upper()
    if a not in VALID_MBTI_TYPES or b not in VALID_MBTI_TYPES:
        raise ValueError("유효하지 않은 MBTI 유형")
    same = _count_same_dimensions(a, b)
    if same >= 3:
        return "ideal"
    if same == 2:
        return "complementary"
    return "challenging"


def get_conflict_points(type_a: str, type_b: str) -> list[str]:
    """갈등 포인트 도출"""
    a, b = type_a.upper(), type_b.upper()
    dims = [("E/I", "외향/내향"), ("S/N", "감각/직관"), ("T/F", "사고/감정"), ("J/P", "판단/인식")]
    conflicts = []
    for (dim, label), (pa, pb) in zip(dims, zip(a, b)):
        if pa != pb:
            conflicts.append(f"{label}: 한쪽은 {pa}적, 다른 쪽은 {pb}적 성향으로 의견이 어긋날 수 있음")
    if not conflicts:
        conflicts.append("유사한 성향으로 큰 갈등은 적을 수 있으나, 시야가 좁아질 수 있음")
    return conflicts


def get_communication_strategy(rel_type: str, type_a: str, type_b: str) -> list[str]:
    """관계 유형별 의사소통 전략"""
    a, b = type_a.upper(), type_b.upper()
    base = [
        "상대의 관점을 먼저 이해하려 노력하기",
        "감정보다 사실을 말할 때와 감정을 나눌 때를 구분하기",
    ]
    if rel_type == "ideal":
        return base + [
            "비슷한 성향을 활용해 깊은 공감 형성",
            "다만 같은 실수나 맹점을 함께 간과하지 않도록 서로 점검하기",
        ]
    if rel_type == "complementary":
        return base + [
            "서로 다른 강점을 인정하고 역할 분담 활용",
            "다름이 갈등이 아니라 보완임을 인식하기",
        ]
    # challenging
    return base + [
        "갈등 시 한숨 돌리며 재대화하는 시간 갖기",
        "결론을 재촉하지 않고, 상대의 처리 방식 존중하기",
    ]


def get_long_term_tips(rel_type: str, type_a: str, type_b: str) -> list[str]:
    """장기 관계 유지 팁"""
    a, b = type_a.upper(), type_b.upper()
    if rel_type == "ideal":
        return [
            "서로의 성향을 잘 알지만, 익숙함에 지루함이 생기지 않도록 새로운 경험을 함께 쌓기",
            "정기적으로 솔직한 대화 시간을 갖고 관계를 돌아보기",
            "비슷한 가치관을 바탕으로 함께 성장할 목표 세우기",
        ]
    if rel_type == "complementary":
        return [
            "서로 다른 강점을 존중하며, 각자의 방식으로 기여하는 공간 마련하기",
            "역할을 나누되 유연하게, 필요시 바꿀 수 있는 여유 갖기",
            "다름으로 인한 불편함이 생기면, 비난 없이 '우리 둘 다'의 관점으로 대화하기",
        ]
    # challenging
    return [
        "갈등이 생길 수 있는 지점을 미리 알고, 피하기보다 소통 방식 합의하기",
        "충분한 혼자만의 시간과 함께하는 시간의 균형을 서로 존중하기",
        "감정이 격해졌을 때는 잠시 멈추고, 차분할 때 다시 대화하기",
    ]


def analyze_compatibility(type_a: str, type_b: str) -> dict:
    """전체 궁합 분석 - 갈등 포인트, 의사소통 전략, 장기 관계 유지 팁"""
    rel_type = get_relationship_type(type_a, type_b)
    return {
        "type_a": type_a.upper(),
        "type_b": type_b.upper(),
        "relationship_type": RELATIONSHIP_TYPES[rel_type],
        "relationship_key": rel_type,
        "conflict_points": get_conflict_points(type_a, type_b),
        "communication_strategy": get_communication_strategy(rel_type, type_a, type_b),
        "long_term_tips": get_long_term_tips(rel_type, type_a, type_b),
    }
