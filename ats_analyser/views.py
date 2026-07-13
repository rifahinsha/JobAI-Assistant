from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from . import logic


@require_GET
def root(request):
    return JsonResponse({
        "message": "ATS Resume Analyzer API (Groq) is running.",
        "model": logic.GROQ_MODEL,
    })


@require_GET
def health(request):
    return JsonResponse({"status": "ok", "model": logic.GROQ_MODEL})


@csrf_exempt
@require_POST
def analyze_text(request):
    resume_text = request.POST.get("resume_text", "")
    jd_text = request.POST.get("jd_text", "")

    if not resume_text.strip():
        return JsonResponse({"detail": "resume_text cannot be empty."}, status=400)
    if not jd_text.strip():
        return JsonResponse({"detail": "jd_text cannot be empty."}, status=400)

    try:
        result = logic.analyze_with_groq(resume_text, jd_text)
    except ValueError as e:
        return JsonResponse({"detail": str(e)}, status=500)

    return JsonResponse({"success": True, "data": result})


@csrf_exempt
@require_POST
def analyze_files(request):
    resume_file = request.FILES.get("resume_file")
    if not resume_file:
        return JsonResponse({"detail": "resume_file is required."}, status=422)

    try:
        resume_text = logic.extract_text_from_file(resume_file.name, resume_file.read())
    except ValueError as e:
        return JsonResponse({"detail": str(e)}, status=400)

    if not resume_text:
        return JsonResponse({"detail": "Could not extract text from the resume file."}, status=422)

    jd_file = request.FILES.get("jd_file")
    jd_text_field = request.POST.get("jd_text")

    jd_content = None
    if jd_file:
        try:
            jd_content = logic.extract_text_from_file(jd_file.name, jd_file.read())
        except ValueError as e:
            return JsonResponse({"detail": str(e)}, status=400)
        if not jd_content:
            return JsonResponse({"detail": "Could not extract text from the job description."}, status=422)
    elif jd_text_field:
        jd_content = jd_text_field.strip()

    try:
        result = logic.analyze_with_groq(resume_text, jd_content)
    except ValueError as e:
        return JsonResponse({"detail": str(e)}, status=500)

    return JsonResponse({
        "success": True,
        "meta": {
            "resume_chars": len(resume_text),
            "jd_chars": len(jd_content) if jd_content else 0,
            "mode": "resume_vs_jd" if jd_content else "resume_only",
        },
        "data": result,
    })


@csrf_exempt
@require_POST
def analyze_mixed(request):
    resume_file = request.FILES.get("resume_file")
    resume_text_field = request.POST.get("resume_text")

    if resume_file:
        try:
            final_resume = logic.extract_text_from_file(resume_file.name, resume_file.read())
        except ValueError as e:
            return JsonResponse({"detail": str(e)}, status=400)
    elif resume_text_field:
        final_resume = resume_text_field.strip()
    else:
        return JsonResponse({"detail": "Provide resume_file or resume_text."}, status=400)

    jd_file = request.FILES.get("jd_file")
    jd_text_field = request.POST.get("jd_text")

    final_jd = None
    if jd_file:
        try:
            final_jd = logic.extract_text_from_file(jd_file.name, jd_file.read())
        except ValueError as e:
            return JsonResponse({"detail": str(e)}, status=400)
        if not final_jd:
            return JsonResponse({"detail": "Could not extract text from the job description."}, status=422)
    elif jd_text_field and jd_text_field.strip():
        final_jd = jd_text_field.strip()

    if not final_resume:
        return JsonResponse({"detail": "Resume text is empty after extraction."}, status=422)

    try:
        result = logic.analyze_with_groq(final_resume, final_jd)
    except ValueError as e:
        return JsonResponse({"detail": str(e)}, status=500)

    return JsonResponse({
        "success": True,
        "meta": {
            "resume_chars": len(final_resume),
            "jd_chars": len(final_jd) if final_jd else 0,
            "mode": "resume_vs_jd" if final_jd else "resume_only",
        },
        "data": result,
    })