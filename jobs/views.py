import os
from pathlib import Path

import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from dotenv import load_dotenv


ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"


@require_GET
def get_jobs(request):
    keyword = request.GET.get("keyword", "developers")
    location = request.GET.get("location", "")
    results = request.GET.get("results", 10)

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results,
        "what": keyword,
        "where": location,
        "content-type": "application/json",
    }
    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        return JsonResponse({"detail": "Failed to fetch jobs"}, status=response.status_code)

    data = response.json()
    jobs = [
        {
            "id": j.get("id"),
            "title": j.get("title"),
            "company": j.get("company", {}).get("display_name"),
            "location": j.get("location", {}).get("display_name"),
            "description": j.get("description"),
            "salary_min": j.get("salary_min"),
            "salary_max": j.get("salary_max"),
            "url": j.get("redirect_url"),
            "created": j.get("created"),
        }
        for j in data.get("results", [])
    ]

    return JsonResponse({"count": data.get("count"), "jobs": jobs})