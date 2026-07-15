import json

from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from . import email_cv
from .chatbot import JobChatbot

sessions: dict[str, JobChatbot] = {}


def get_bot(session_id: str) -> JobChatbot:
    if session_id not in sessions:
        sessions[session_id] = JobChatbot()
    return sessions[session_id]


def _parse_json_body(request):
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return None


@require_GET
def root(request):
    return JsonResponse({"status": "ok", "service": "Job Assistant Chatbot"})


@require_POST
def chat(request):
    body = _parse_json_body(request)
    if body is None:
        return HttpResponseBadRequest("Invalid JSON body")

    message = (body.get("message") or "").strip()
    session_id = body.get("session_id", "default")

    if not message:
        return JsonResponse({"detail": "Message cannot be empty"}, status=400)

    bot = get_bot(session_id)
    reply = bot.chat(message)
    return JsonResponse({"reply": reply, "session_id": session_id})


@require_POST
def reset_chat(request):
    session_id = request.GET.get("session_id", "default")
    bot = get_bot(session_id)
    bot.reset()
    return JsonResponse({"status": "cleared", "session_id": session_id})


@require_GET
def get_history(request):
    session_id = request.GET.get("session_id", "default")
    bot = get_bot(session_id)
    return JsonResponse({
        "session_id": session_id,
        "summary": bot.history_summary(),
        "messages": bot.memory.get_history(),
    })


@require_POST
def email_analyze(request):
    resume_text = request.POST.get("resume_text")
    jd_text = request.POST.get("jd_text")
    resume_file = request.FILES.get("resume_file")
    jd_file = request.FILES.get("jd_file")

    try:
        resume = email_cv.resolve_text(resume_text, resume_file, "resume")
        job_description = email_cv.resolve_text(jd_text, jd_file, "job description")
    except ValueError as e:
        return JsonResponse({"detail": str(e)}, status=400)

    resume_skills = email_cv.extract_skills(resume)
    jd_skills = email_cv.extract_skills(job_description)
    matched, missing = email_cv.compare_skills(resume_skills, jd_skills)
    email_text = email_cv.generate_email(matched, job_description)

    return JsonResponse({
        "matched_skills": matched,
        "missing_skills": missing,
        "email": email_text,
        "jd_text": job_description,
    })


@require_POST
def email_cover_letter(request):
    body = _parse_json_body(request)
    if body is None:
        return HttpResponseBadRequest("Invalid JSON body")

    matched_skills = body.get("matched_skills", [])
    job_description = body.get("job_description", "")
    text = email_cv.generate_cover_letter(matched_skills, job_description)
    return JsonResponse({"cover_letter": text})


@require_POST
def email_cover_letter_pdf(request):
    body = _parse_json_body(request)
    if body is None:
        return HttpResponseBadRequest("Invalid JSON body")

    cover_letter_text = (body.get("cover_letter_text") or "").strip()
    if not cover_letter_text:
        return JsonResponse({"detail": "cover_letter_text is empty"}, status=400)

    pdf_bytes = email_cv.cover_letter_pdf_bytes(cover_letter_text)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="cover_letter.pdf"'
    return response