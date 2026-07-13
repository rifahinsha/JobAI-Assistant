import io
import json
import os
import re
from pathlib import Path
from typing import Optional

import docx  # extract text from DOCX
import pdfplumber  # extract text from PDF
from dotenv import load_dotenv
from groq import Groq  # LLM API client

load_dotenv(Path(__file__).resolve().parent / ".env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = "llama-3.3-70b-versatile"


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()


def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    filename = filename.lower()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif filename.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {filename}. Use PDF, DOCX, or TXT.")


SYSTEM_PROMPT = (
    "You are an expert ATS (Applicant Tracking System) resume analyst with 15+ years of "
    "experience in HR and recruitment. Analyze resumes against job descriptions and return "
    "structured, actionable feedback as valid JSON only — no markdown, no explanation."
)


def build_analysis_prompt(resume_text: str, jd_text: str) -> str:
    return f"""Analyze the resume against the job description and return ONLY a valid JSON object.
No markdown fences, no explanation, no preamble. Start your response with {{ and end with }}.

Return exactly this structure:
{{
  "ats_score": <integer 0-100>,
  "rating": "<Excellent|Good|Fair|Weak>",
  "summary": "<2-3 sentence overall assessment mentioning key strengths and gaps>",
  "stats": {{
    "matched_keywords": <integer>,
    "total_keywords": <integer>,
    "years_experience_match": "<e.g. 3 of 5 years>",
    "education_match": "<Yes|Partial|No>"
  }},
  "categories": [
    {{"name": "Technical Skills", "score": <0-100>, "note": "<one specific insight>"}},
    {{"name": "Experience",       "score": <0-100>, "note": "<one specific insight>"}},
    {{"name": "Education",        "score": <0-100>, "note": "<one specific insight>"}},
    {{"name": "Keywords",         "score": <0-100>, "note": "<one specific insight>"}},
    {{"name": "Soft Skills",      "score": <0-100>, "note": "<one specific insight>"}}
  ],
  "skills": {{
    "matched": ["<skill>"],
    "missing": ["<skill>"],
    "partial": ["<skill>"]
  }},
  "action_plan": [
    {{"priority": "High",   "action": "<specific actionable step>", "impact": "<why it matters for ATS>"}},
    {{"priority": "High",   "action": "<specific actionable step>", "impact": "<why it matters for ATS>"}},
    {{"priority": "Medium", "action": "<specific actionable step>", "impact": "<why it matters for ATS>"}},
    {{"priority": "Medium", "action": "<specific actionable step>", "impact": "<why it matters for ATS>"}},
    {{"priority": "Low",    "action": "<specific actionable step>", "impact": "<why it matters for ATS>"}}
  ]
}}

Rating guide: Excellent >= 80 | Good 65-79 | Fair 40-64 | Weak < 40

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{jd_text[:1500]}"""


def build_resume_only_prompt(resume_text: str) -> str:
    """Used when no JD is provided — scores general resume quality / ATS-friendliness."""
    return f"""Analyze this resume on its own (no specific job description was provided) and
return ONLY a valid JSON object. Score it for general ATS-friendliness, structure, clarity,
use of action verbs, and quantifiable impact — as a recruiter would for ANY relevant role.
No markdown fences, no explanation, no preamble. Start your response with {{ and end with }}.

Return exactly this structure:
{{
  "ats_score": <integer 0-100>,
  "rating": "<Excellent|Good|Fair|Weak>",
  "summary": "<2-3 sentence overall assessment mentioning key strengths and gaps>",
  "stats": {{
    "matched_keywords": <integer, set to 0>,
    "total_keywords": <integer, set to 0>,
    "years_experience_match": "<e.g. 2 years of experience listed>",
    "education_match": "<Yes|Partial|No>"
  }},
  "categories": [
    {{"name": "Formatting & Structure", "score": <0-100>, "note": "<one specific insight>"}},
    {{"name": "Experience",             "score": <0-100>, "note": "<one specific insight>"}},
    {{"name": "Education",              "score": <0-100>, "note": "<one specific insight>"}},
    {{"name": "Action Verbs & Impact",  "score": <0-100>, "note": "<one specific insight>"}},
    {{"name": "ATS Compatibility",      "score": <0-100>, "note": "<one specific insight>"}}
  ],
  "skills": {{
    "matched": ["<key skills found in the resume>"],
    "missing": [],
    "partial": []
  }},
  "action_plan": [
    {{"priority": "High",   "action": "<specific actionable step>", "impact": "<why it matters for ATS>"}},
    {{"priority": "High",   "action": "<specific actionable step>", "impact": "<why it matters for ATS>"}},
    {{"priority": "Medium", "action": "<specific actionable step>", "impact": "<why it matters for ATS>"}},
    {{"priority": "Medium", "action": "<specific actionable step>", "impact": "<why it matters for ATS>"}},
    {{"priority": "Low",    "action": "<specific actionable step>", "impact": "<why it matters for ATS>"}}
  ]
}}

Rating guide: Excellent >= 80 | Good 65-79 | Fair 40-64 | Weak < 40

RESUME:
{resume_text[:2500]}"""


def analyze_with_groq(resume_text: str, jd_text: Optional[str] = None) -> dict:
    """Send to Groq and parse the JSON response.

    If jd_text is None/empty, runs in resume-only mode. Raises ValueError if
    Groq's response isn't valid JSON.
    """
    if jd_text:
        prompt = build_analysis_prompt(resume_text, jd_text)
    else:
        prompt = build_resume_only_prompt(resume_text)

    chat_completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1500,
        response_format={"type": "json_object"},
        timeout=60,
    )

    raw = chat_completion.choices[0].message.content
    clean = re.sub(r"```(?:json)?|```", "", raw).strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        raise ValueError(f"Groq returned invalid JSON: {e}. Raw: {clean[:300]}")