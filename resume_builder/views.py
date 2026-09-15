import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from groq import Groq

from .pdf_export import resume_pdf_bytes, TEMPLATES

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"

FORM_FIELDS = [
    "resumeType",
    "personalInfo",
    "education",
    "experience",
    "projects",
    "skills",
    "extracurricular",
]

TEMPLATE_CHOICES = [
    ("classic", "Classic Serif"),
    ("modern", "Modern Sans"),
    ("minimal", "Minimal"),
]
DEFAULT_TEMPLATE = "classic"


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
    render the generated resume straight into the same page -- no JS."""
    if request.method != "POST":
        return render(request, "resume_builder.html", {
            "form_data": {}, "templates": TEMPLATE_CHOICES, "selected_template": DEFAULT_TEMPLATE,
        })

    data = {field: request.POST.get(field, "").strip() for field in FORM_FIELDS}
    template = request.POST.get("template") or DEFAULT_TEMPLATE
    if template not in TEMPLATES:
        template = DEFAULT_TEMPLATE

    ctx = {"form_data": data, "templates": TEMPLATE_CHOICES, "selected_template": template}

    if not data.get("personalInfo") or not data.get("education"):
        messages.error(request, "Please provide at least Personal Information and Education.")
        return render(request, "resume_builder.html", ctx)

    if not os.getenv("GROQ_API_KEY"):
        messages.error(request, "Server is missing a Groq API key. Contact the administrator.")
        return render(request, "resume_builder.html", ctx)

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
        return render(request, "resume_builder.html", ctx)

    resume_html = response.choices[0].message.content
    clean_html = resume_html.replace("```html", "").replace("```", "").strip()

    # Kept in the session so the download endpoint (and manual edits) can
    # re-serve/re-export the same resume without another API call.
    request.session["generated_resume_html"] = clean_html
    request.session["generated_resume_template"] = template

    ctx["generated_html"] = clean_html
    return render(request, "resume_builder.html", ctx)


@login_required(login_url="login")
@require_POST
def save_edits(request):
    """Persists in-preview edits (from the contenteditable Edit mode) back
    into the session, so Download PDF reflects what the user actually sees
    -- including their manual tweaks."""
    edited_html = request.POST.get("html", "").strip()
    if not edited_html:
        return JsonResponse({"error": "No content to save."}, status=400)

    if not request.session.get("generated_resume_html"):
        return JsonResponse({"error": "Please generate a resume first."}, status=400)

    request.session["generated_resume_html"] = edited_html
    return JsonResponse({"status": "saved"})


@login_required(login_url="login")
@require_POST
def set_template(request):
    """Switches the active template for the currently generated resume."""
    template = request.POST.get("template")
    if template not in TEMPLATES:
        return JsonResponse({"error": "Unknown template."}, status=400)

    if not request.session.get("generated_resume_html"):
        return JsonResponse({"error": "Please generate a resume first."}, status=400)

    request.session["generated_resume_template"] = template
    return JsonResponse({"status": "updated", "template": template})


@login_required(login_url="login")
def download_resume_pdf(request):
    """Serves the most recently generated (and possibly edited) resume as a
    PDF, built from the same HTML + template kept in the session."""
    resume_html = request.session.get("generated_resume_html")
    if not resume_html:
        messages.error(request, "Please generate a resume first.")
        return redirect("resume_builder:resume_builder")

    template = request.session.get("generated_resume_template", DEFAULT_TEMPLATE)
    pdf_bytes = resume_pdf_bytes(resume_html, template)

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="resume.pdf"'
    return response