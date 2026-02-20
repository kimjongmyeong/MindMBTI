"""
MBTI 결과 PDF 생성
"""
import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 한글 폰트 등록 (Windows Malgun)
PDF_FONT = "Helvetica"
PDF_BOLD = "Helvetica-Bold"
try:
    for path in [
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/gulim.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    ]:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont("KorFont", path))
            PDF_FONT = PDF_BOLD = "KorFont"
            break
except Exception:
    pass


def _truncate(s: str, max_len: int = 100) -> str:
    return (str(s) or "")[:max_len]


def create_mbti_pdf(mbti_type: str, percentages: dict, report: dict) -> bytes:
    """MBTI 결과 + 기본 리포트 PDF 생성"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4
    y = h - 40

    def draw(text: str, size: int = 12, bold: bool = False):
        nonlocal y
        c.setFont(PDF_BOLD if bold else PDF_FONT, size)
        for line in str(text).split("\n")[:3]:
            c.drawString(40, y, _truncate(line, 70))
            y -= 16
        y -= 4

    draw("MindMBTI - MBTI Analysis Report", 18, bold=True)
    draw(f"MBTI Type: {mbti_type}", 16, bold=True)

    if percentages:
        draw("Percentage by Dimension:", 12, bold=True)
        for dim, pct in (percentages or {}).items():
            if isinstance(pct, dict):
                parts = " / ".join(f"{k} {v}%" for k, v in pct.items())
                draw(f"  {dim}: {parts}", 10)
        y -= 8

    if report:
        kw = report.get("keywords") or []
        draw("Keywords: " + (", ".join(kw) if isinstance(kw, list) else str(kw)), 12, bold=True)
        draw("Strengths: " + _truncate(report.get("strengths"), 150), 10)
        draw("Weaknesses: " + _truncate(report.get("weaknesses"), 150), 10)
        draw("Stress: " + _truncate(report.get("stress_reaction"), 150), 10)
        draw("Decision: " + _truncate(report.get("decision_style"), 150), 10)

    c.save()
    return buffer.getvalue()
