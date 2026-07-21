import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .engine.graph import graph
from .engine.state import new_state
from .engine.pdf_report import build_roadmap_pdf


def _body(request) -> dict:
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return {}


@login_required(login_url="login")
@csrf_exempt
@require_POST
def generate(request):
    """Runs the full 6-agent pipeline and returns the roadmap as JSON.

    This is a synchronous call (several Groq requests chained together),
    so it can take 15-30 seconds - the frontend should show a loading state.
    """
    data = _body(request)
    role = (data.get("role") or "").strip()
    skills_raw = (data.get("current_skills") or "").strip()

    if not role:
        return JsonResponse({"detail": "role is required."}, status=400)

    if skills_raw == "" or skills_raw.lower() == "none":
        current_skills = []
    else:
        current_skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

    state = new_state(role, current_skills)

    try:
        result = graph.invoke(state)
    except Exception as e:
        return JsonResponse({"detail": f"Could not generate roadmap: {e}"}, status=500)

    # Stash the result so the download-pdf view can rebuild the same report
    # without re-running the (expensive) pipeline.
    request.session["roadmap_result"] = {
        "role": result["role"],
        "required_skills": result["required_skills"],
        "missing_skills": result["missing_skills"],
        "learning_path": result["learning_path"],
        "roadmap": result["roadmap"],
        "resources": result["resources"],
        "projects": result["projects"],
        "validation": result["validation"],
    }

    return JsonResponse({"success": True, "data": request.session["roadmap_result"]})


@login_required(login_url="login")
@require_GET
def download_pdf(request):
    """Streams the most recently generated roadmap as a PDF download."""
    saved = request.session.get("roadmap_result")

    if not saved:
        return JsonResponse(
            {"detail": "No roadmap found for this session. Generate one first."}, status=400
        )

    pdf_bytes = build_roadmap_pdf(
        saved["role"],
        saved["required_skills"],
        saved["missing_skills"],
        saved["roadmap"],
        saved["resources"],
        saved["projects"],
        saved["validation"],
    )

    filename = f"{saved['role'].replace(' ', '_')}_Roadmap.pdf"
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
