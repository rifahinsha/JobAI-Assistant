"""Converts the AI-generated resume HTML (see views._build_prompt for the
fixed set of CSS classes the model is instructed to use) into a real PDF,
using reportlab -- the same library already used for cover letters in
chatbot/email_cv.py.

We deliberately parse the known resume-* classes rather than rendering
arbitrary HTML: this keeps the output ATS-friendly (real selectable text,
predictable single-column layout) instead of a screenshot-like render.
"""
import io

from bs4 import BeautifulSoup
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

INK = colors.HexColor("#16241C")
INK_SOFT = colors.HexColor("#5C6B62")
GREEN_DEEP = colors.HexColor("#163C2C")

NAME_STYLE = ParagraphStyle(
    "ResumeName", fontName="Times-Bold", fontSize=20, alignment=TA_CENTER,
    spaceAfter=4, textColor=INK,
)
CONTACT_STYLE = ParagraphStyle(
    "ResumeContact", fontName="Times-Roman", fontSize=9.5, alignment=TA_CENTER,
    textColor=INK_SOFT, spaceAfter=12,
)
SECTION_TITLE_STYLE = ParagraphStyle(
    "SectionTitle", fontName="Times-Bold", fontSize=12,
    spaceBefore=10, spaceAfter=5, textColor=GREEN_DEEP,
)
ITEM_HEADER_STYLE = ParagraphStyle(
    "ItemHeader", fontName="Times-Bold", fontSize=10.5, spaceAfter=1, textColor=INK,
)
ITEM_SUBTITLE_STYLE = ParagraphStyle(
    "ItemSubtitle", fontName="Times-Italic", fontSize=10, textColor=INK_SOFT, spaceAfter=4,
)
BULLET_STYLE = ParagraphStyle(
    "Bullet", fontName="Times-Roman", fontSize=10, leftIndent=14,
    spaceAfter=2, leading=13, textColor=INK,
)
SKILL_STYLE = ParagraphStyle(
    "Skill", fontName="Times-Roman", fontSize=10, spaceAfter=3, textColor=INK,
)


def _text(node) -> str:
    return node.get_text(" ", strip=True) if node else ""


def resume_pdf_bytes(html: str) -> bytes:
    """Parses the resume-* class structure and builds a single-column,
    ATS-friendly PDF. Falls back gracefully if a section is missing pieces
    (the model doesn't always emit every optional class)."""
    soup = BeautifulSoup(html or "", "html.parser")
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=LETTER,
        topMargin=0.55 * inch, bottomMargin=0.55 * inch,
        leftMargin=0.65 * inch, rightMargin=0.65 * inch,
    )

    story = []

    header = soup.find(class_="resume-header")
    if header:
        name = _text(header.find(class_="resume-name"))
        if name:
            story.append(Paragraph(name, NAME_STYLE))

        contact = header.find(class_="resume-contact")
        if contact:
            links = [a.get_text(strip=True) for a in contact.find_all("a")]
            contact_text = " | ".join(links) if links else _text(contact)
            if contact_text:
                story.append(Paragraph(contact_text, CONTACT_STYLE))

    sections = soup.find_all(class_="resume-section")
    for section in sections:
        title = _text(section.find(class_="resume-section-title"))
        if title:
            story.append(Paragraph(title.upper(), SECTION_TITLE_STYLE))

        # Standard items (Education / Experience / Projects / Extracurricular)
        for item in section.find_all(class_="resume-item"):
            item_header = _text(item.find(class_="resume-item-header"))
            if item_header:
                story.append(Paragraph(item_header, ITEM_HEADER_STYLE))

            subtitle = _text(item.find(class_="resume-item-subtitle"))
            location = _text(item.find(class_="resume-item-location"))
            if subtitle or location:
                line = subtitle
                if location:
                    line = f"{line} — {location}" if line else location
                story.append(Paragraph(line, ITEM_SUBTITLE_STYLE))

            for li in item.find_all("li"):
                bullet_text = li.get_text(" ", strip=True)
                if bullet_text:
                    story.append(Paragraph(f"&bull; {bullet_text}", BULLET_STYLE))

            story.append(Spacer(1, 3))

        # Skills sections: skill-item elements sitting directly in the section
        for skill in section.find_all(class_="skill-item"):
            skill_text = skill.get_text(" ", strip=True)
            if skill_text:
                story.append(Paragraph(skill_text, SKILL_STYLE))

        # Coursework-style grids with no resume-item wrapper
        for grid in section.find_all(class_="coursework-grid"):
            for li in grid.find_all("li"):
                bullet_text = li.get_text(" ", strip=True)
                if bullet_text:
                    story.append(Paragraph(f"&bull; {bullet_text}", BULLET_STYLE))

    if not story:
        # Extremely defensive fallback: never return an empty/broken PDF.
        story.append(Paragraph("Resume content could not be parsed.", ITEM_HEADER_STYLE))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()