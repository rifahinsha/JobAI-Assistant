import httpx, os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"

@app.get("/api/jobs")
async def get_jobs(keyword: str = "developers", location: str = "", results: int = 10):
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results,
        "what": keyword,
        "where": location,
        "content-type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch jobs")
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

    return {"count": data.get("count"), "jobs": jobs}