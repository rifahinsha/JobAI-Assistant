import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from groq import Groq

from .pdf_export import resume_pdf_bytes

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

FORM_FIELDS = [
    "resumeType",
    "personalInfo",
    "education",
    "experience",
    "projects",
    "skills",
    "extracurricular",
]


def _build_prompt(data):
    resume_type = data.get("resumeType") or "software"
    return f"""You are a professional resume writer. Create a polished, ATS-friendly resume as clean HTML for a {resume_type} role.

Use ONLY these CSS classes (already defined in an external stylesheet, do not add inline styles or <style> tags):
- resume-header, resume-name, resume-contact
- resume-section, resume-section-title
- resume-item, resume-item-header, resume-item-subtitle, resume-item-location
- resume-list (ul), with plain <li> items
- coursework-grid (ul) for relevant coursework, if any
- skill-item, skill-label

Structure: header (name + contact), then sections in this order: Education, Experience, Projects, Skills, and Leadership/Extracurricular (only if content is provided).

Candidate information:
PERSONAL INFO:
{data.get('personalInfo', '')}

EDUCATION:
{data.get('education', '')}

EXPERIENCE:
{data.get('experience') or '(none provided)'}

PROJECTS:
{data.get('projects') or '(none provided)'}

SKILLS:
{data.get('skills') or '(none provided)'}

LEADERSHIP / EXTRACURRICULAR:
{data.get('extracurricular') or '(none provided)'}

Return ONLY the HTML for the resume content (no <html>, <head>, or <body> tags, no markdown code fences, no commentary)."""


@login_required(login_url="login")
def resume_builder(request):
    """GET: show the empty form. POST: call Groq server-side and
    render the generated resume straight into the same page — no JS."""
    if request.method != "POST":
        return render(request, "resume_builder.html", {"form_data": {}})

    data = {field: request.POST.get(field, "").strip() for field in FORM_FIELDS}

    if not data.get("personalInfo") or not data.get("education"):
        messages.error(request, "Please provide at least Personal Information and Education.")
        return render(request, "resume_builder.html", {"form_data": data})

    if not os.getenv("GROQ_API_KEY"):
        messages.error(request, "Server is missing a Groq API key. Contact the administrator.")
        return render(request, "resume_builder.html", {"form_data": data})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=2048,
            messages=[
                {"role": "system", "content": "You are a professional resume writer."},
                {"role": "user", "content": _build_prompt(data)},
            ],
        )
    except Exception as exc:
        messages.error(request, f"Error contacting Groq: {exc}")
        return render(request, "resume_builder.html", {"form_data": data})

    resume_html = response.choices[0].message.content

    clean_html = resume_html.replace("```html", "").replace("```", "").strip()

    # Kept in the session so the download endpoint can re-serve the same
    # resume as a file without another API call.
    request.session["generated_resume_html"] = clean_html

    return render(
        request,
        "resume_builder.html",
        {"form_data": data, "generated_html": clean_html},
    )


@login_required(login_url="login")
def download_resume_pdf(request):
    """Serves the most recently generated resume as a PDF, built from the
    same HTML kept in the session (no extra API call needed)."""
    resume_html = request.session.get("generated_resume_html")
    if not resume_html:
        messages.error(request, "Please generate a resume first.")
        return redirect("resume_builder:resume_builder")

    pdf_bytes = resume_pdf_bytes(resume_html)

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="resume.pdf"'
    return response