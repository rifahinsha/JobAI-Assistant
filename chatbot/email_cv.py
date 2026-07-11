"""
email_cv.py — FastAPI router for the Email & Cover Letter Generator feature.

Place this file in your chatbot/ folder, next to main.py.
main.py already does:

    from email_cv import router as email_cv_router
    app.include_router(email_cv_router)

Endpoints (all under /email-cover, matching email_cv.html's `API` const):
  POST /email-cover/analyze            -> matched/missing skills + email
  POST /email-cover/cover-letter       -> cover letter text
  POST /email-cover/cover-letter/pdf   -> cover letter PDF (binary)

Ported from the standalone AI_Job_Assistant script:
- Same skill extraction / matching / email / cover letter prompts (Groq,
  llama-3.1-8b-instant).
- read_resume() now accepts raw bytes (from an uploaded PDF) instead of a
  filesystem path.
- PDF generation happens in memory (BytesIO) and is streamed back directly,
  instead of being written to output/cover_letter.pdf on disk.
"""
import io
import json
import os

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from pydantic import BaseModel
from pypdf import PdfReader
from groq import Groq
from dotenv import load_dotenv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

load_dotenv()

router = APIRouter(prefix="/email-cover", tags=["email-cover"])

MODEL = "llama-3.1-8b-instant"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ---------- helpers (ported from the standalone script) ----------

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


async def _resolve_text(text_field: str | None, file_field: UploadFile | None, label: str) -> str:
    """email_cv.html sends EITHER a *_text form field OR a *_file upload."""
    if file_field is not None:
        raw = await file_field.read()
        if file_field.filename.lower().endswith(".pdf"):
            return read_pdf_bytes(raw)
        return raw.decode("utf-8", errors="ignore")

    if text_field and text_field.strip():
        return text_field.strip()

    raise HTTPException(status_code=400, detail=f"Missing {label} (provide text or a file).")


# ---------- request/response models for the JSON endpoints ----------

class CoverLetterRequest(BaseModel):
    matched_skills: list[str]
    job_description: str


class CoverLetterPdfRequest(BaseModel):
    cover_letter_text: str


# ---------- routes ----------

@router.post("/analyze")
async def analyze(
    resume_text: str | None = Form(default=None),
    jd_text: str | None = Form(default=None),
    resume_file: UploadFile | None = File(default=None),
    jd_file: UploadFile | None = File(default=None),
):
    resume = await _resolve_text(resume_text, resume_file, "resume")
    job_description = await _resolve_text(jd_text, jd_file, "job description")

    resume_skills = extract_skills(resume)
    jd_skills = extract_skills(job_description)
    matched, missing = compare_skills(resume_skills, jd_skills)
    email = generate_email(matched, job_description)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "email": email,
        "jd_text": job_description,
    }


@router.post("/cover-letter")
def cover_letter(req: CoverLetterRequest):
    text = generate_cover_letter(req.matched_skills, req.job_description)
    return {"cover_letter": text}


@router.post("/cover-letter/pdf")
def cover_letter_pdf(req: CoverLetterPdfRequest):
    if not req.cover_letter_text.strip():
        raise HTTPException(status_code=400, detail="cover_letter_text is empty")

    pdf_bytes = cover_letter_pdf_bytes(req.cover_letter_text)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="cover_letter.pdf"'},
    )