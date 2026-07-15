"""
email_cv.py — Email & Cover Letter Generator helpers.

Plain functions used by chatbot/views.py (previously a standalone FastAPI
router; the HTTP layer now lives in views.py so this module has no
FastAPI/pydantic dependency).
"""
import io
import json
import os
from pathlib import Path

from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


MODEL = "llama-3.1-8b-instant"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def read_pdf_bytes(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def extract_skills(text: str) -> list[str]:
    prompt = f"""
Extract technical skills from the text.

Return JSON:
{{ "skills": ["Python", "SQL", "Machine Learning"] }}

Text:
{text}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        data = json.loads(response.choices[0].message.content)
        return data.get("skills", [])
    except (json.JSONDecodeError, AttributeError, KeyError):
        return []


def compare_skills(resume_skills, jd_skills):
    resume_lower = [s.lower() for s in resume_skills]
    matched, missing = [], []
    for skill in jd_skills:
        if skill.lower() in resume_lower:
            matched.append(skill)
        else:
            missing.append(skill)
    return matched, missing


def generate_email(matched_skills, job_description) -> str:
    prompt = f"""
    Write a professional job application email.

    Keep it short (5-7 lines).
    No bullet points.
    Include subject line.

    Resume: {matched_skills}
    Job Description: {job_description}
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def generate_cover_letter(matched_skills, job_description) -> str:
    prompt = f"""
Write a professional and well-structured cover letter for a job application.

Details:
- Candidate skills: {matched_skills}
- Job description: {job_description}

Instructions:
- The cover letter must be tailored to the given job description
- Do NOT assume a specific job role (infer from job description)
- Use a formal and professional tone
- Keep it 3–4 paragraphs (not too long, not too short)
- No bullet points
- Highlight relevant skills and how they match the job
- Include 1–2 impact statements (projects, achievements, or outcomes)
- Make it sound natural and human, not robotic

Format strictly like this:

[Your Name]
[City, State]
[Email] | [Phone Number]

[Date]

Hiring Manager
[Company Name]

Dear Hiring Manager,

(Paragraph 1: Strong introduction showing interest in the role)

(Paragraph 2: Skills + technical strengths aligned with job)

(Paragraph 3: Experience/projects + impact/results)

(Paragraph 4: Closing + interest in company + call to action)

Sincerely,
[Your Name]

Important:
- Do NOT include placeholders like [Your Name] inside paragraphs
- Keep formatting clean for PDF generation
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def cover_letter_pdf_bytes(text: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    story = []
    for para in text.split("\n\n"):
        story.append(Paragraph(para.strip(), styles["Normal"]))
        story.append(Spacer(1, 14))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def resolve_text(text_field: str | None, file_field, label: str) -> str:
    """email_cv.html sends EITHER a *_text form field OR a *_file upload."""
    if file_field is not None:
        raw = file_field.read()
        if file_field.name.lower().endswith(".pdf"):
            return read_pdf_bytes(raw)
        return raw.decode("utf-8", errors="ignore")

    if text_field and text_field.strip():
        return text_field.strip()

    raise ValueError(f"Missing {label} (provide text or a file).")