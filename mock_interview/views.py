import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import logic


def _body(request) -> dict:
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return {}


@login_required(login_url="login")
@csrf_exempt
@require_POST
def start_interview(request):
    data = _body(request)
    role = (data.get("role") or "").strip()
    experience = (data.get("experience") or "").strip()
    jd = (data.get("jd") or "").strip()

    if not role or not experience or not jd:
        return JsonResponse(
            {"detail": "role, experience and jd are all required."}, status=400
        )

    try:
        raw = logic.generate_questions(role, experience, jd)
        questions = logic.parse_questions(raw)
    except Exception as e:
        return JsonResponse({"detail": f"Could not generate questions: {e}"}, status=500)

    if not questions:
        return JsonResponse(
            {"detail": "No questions could be generated. Try a more detailed job description."},
            status=422,
        )

    # Interview state lives in the session, one interview at a time per user.
    request.session["mi_role"] = role
    request.session["mi_experience"] = experience
    request.session["mi_questions"] = questions
    request.session["mi_index"] = 0
    request.session["mi_history"] = []

    return JsonResponse(
        {
            "success": True,
            "total": len(questions),
            "index": 0,
            "question": questions[0],
        }
    )


@login_required(login_url="login")
@csrf_exempt
@require_POST
def submit_answer(request):
    data = _body(request)
    answer = (data.get("answer") or "").strip()

    questions = request.session.get("mi_questions")
    index = request.session.get("mi_index")

    if not questions or index is None:
        return JsonResponse({"detail": "No interview in progress. Start one first."}, status=400)
    if not answer:
        return JsonResponse({"detail": "answer cannot be empty."}, status=400)
    if index >= len(questions):
        return JsonResponse({"detail": "Interview already completed."}, status=400)

    question = questions[index]

    try:
        result = logic.evaluate_answer(question, answer)
    except Exception as e:
        return JsonResponse({"detail": f"Could not evaluate answer: {e}"}, status=500)

    history = request.session.get("mi_history", [])
    history.append(
        {"question": question, "answer": answer, "score": result["score"], "feedback": result["feedback"]}
    )
    request.session["mi_history"] = history

    next_index = index + 1
    done = next_index >= len(questions)
    request.session["mi_index"] = next_index

    return JsonResponse(
        {
            "success": True,
            "score": result["score"],
            "feedback": result["feedback"],
            "done": done,
            "index": next_index,
            "total": len(questions),
            "next_question": None if done else questions[next_index],
            "history": history if done else None,
        }
    )


@login_required(login_url="login")
@csrf_exempt
@require_POST
def reset_interview(request):
    for key in ("mi_role", "mi_experience", "mi_questions", "mi_index", "mi_history"):
        request.session.pop(key, None)
    return JsonResponse({"success": True})
