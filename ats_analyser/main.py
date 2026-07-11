from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from groq import Groq # LLM API client
import pdfplumber # extract text from PDF
import docx # extract text from DOCX
import json
import io # input/output
import re # regular expression
import os # operating system
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="ATS Resume Analyzer API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

GROQ_MODEL = "llama-3.3-70b-versatile"


# Text extraction from pdf , bytes into strings
def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

# Text extraction from docx
def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()

# file extension based text extraction
def extract_text_from_file(file: UploadFile, file_bytes: bytes) -> str:
    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif filename.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore") #ignore not valid bytes
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {filename}. Use PDF, DOCX, or TXT."
        )


# Prompt settings

SYSTEM_PROMPT = (
    "You are an expert ATS (Applicant Tracking System) resume analyst with 15+ years of "
    "experience in HR and recruitment. Analyze resumes against job descriptions and return "
    "structured, actionable feedback as valid JSON only — no markdown, no explanation."
)

# prompt when user upload resume + job description
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

# prompt when user upload resume only (no job description)
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

# Core analysis

def analyze_with_groq(resume_text: str, jd_text: Optional[str] = None) -> dict:
    """Send to Groq and parse the JSON response.

    If jd_text is None/empty, runs in resume-only mode (general ATS quality check,
    no JD keyword-matching).
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
        temperature=0.2, #score consistancy
        max_tokens=1500, #responce length
        response_format={"type": "json_object"}, #output type
        timeout=60, 
    )

    raw = chat_completion.choices[0].message.content
    clean = re.sub(r"```(?:json)?|```", "", raw).strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Groq returned invalid JSON: {e}. Raw: {clean[:300]}"
        )

# server checking 
@app.get("/")
def root():
    return {
        "message": "ATS Resume Analyzer API (Groq) is running.",
        "model": GROQ_MODEL,
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok", "model": GROQ_MODEL}


@app.post("/analyze/text")
async def analyze_text(
    resume_text: str = Form(..., description="Plain text of the resume"),
    jd_text: str = Form(..., description="Plain text of the job description"),
):
    """Analyze resume and JD provided as plain text form fields."""
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="resume_text cannot be empty.")
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="jd_text cannot be empty.")

    result = analyze_with_groq(resume_text, jd_text)
    return JSONResponse(content={"success": True, "data": result})


@app.post("/analyze/files")
async def analyze_files(
    resume_file: UploadFile = File(..., description="Resume file (PDF, DOCX, TXT)"),
    jd_file: Optional[UploadFile] = File(None, description="JD file (PDF, DOCX, TXT) — optional"),
    jd_text: Optional[str] = Form(None, description="JD as plain text — optional"),
):
    """
    Resume as file upload (required).
    JD as file OR plain text (optional) — if neither is given, runs resume-only scoring.
    """
    resume_bytes = await resume_file.read() #files into bytes
    resume_text = extract_text_from_file(resume_file, resume_bytes)

    if not resume_text:
        raise HTTPException(status_code=422, detail="Could not extract text from the resume file.")

    jd_content = None
    if jd_file:
        jd_bytes = await jd_file.read()
        jd_content = extract_text_from_file(jd_file, jd_bytes)
        if not jd_content:
            raise HTTPException(status_code=422, detail="Could not extract text from the job description.")
    elif jd_text:
        jd_content = jd_text.strip()

    result = analyze_with_groq(resume_text, jd_content)
    return JSONResponse(content={
        "success": True,
        "meta": {
            "resume_chars": len(resume_text),
            "jd_chars": len(jd_content) if jd_content else 0,
            "mode": "resume_vs_jd" if jd_content else "resume_only",
        },
        "data": result,
    })


@app.post("/analyze/mixed")
async def analyze_mixed(
    resume_file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
    jd_text: Optional[str] = Form(None),
):
    """
    Flexible endpoint — any combination of file upload or plain text
    for both resume and JD. File takes priority if both provided.
    """
    if resume_file:
        rb = await resume_file.read()
        final_resume = extract_text_from_file(resume_file, rb)
    elif resume_text:
        final_resume = resume_text.strip()
    else:
        raise HTTPException(status_code=400, detail="Provide resume_file or resume_text.")

    final_jd = None
    if jd_file:
        jb = await jd_file.read()
        final_jd = extract_text_from_file(jd_file, jb)
        if not final_jd:
            raise HTTPException(status_code=422, detail="Could not extract text from the job description.")
    elif jd_text and jd_text.strip():
        final_jd = jd_text.strip()
    # If neither jd_file nor jd_text is given, final_jd stays None —
    # analyze_with_groq will run resume-only scoring in that case.

    if not final_resume:
        raise HTTPException(status_code=422, detail="Resume text is empty after extraction.")

    result = analyze_with_groq(final_resume, final_jd)
    return JSONResponse(content={
        "success": True,
        "meta": {
            "resume_chars": len(final_resume),
            "jd_chars": len(final_jd) if final_jd else 0,
            "mode": "resume_vs_jd" if final_jd else "resume_only",
        },
        "data": result,
    })