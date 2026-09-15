import os
import re
from urllib.parse import quote_plus

from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"


def get_resources(skills: list[str]) -> str:
    skills_text = "\n".join(skills)

    prompt = f"""
You are an expert AI Career Mentor.

For each skill below, recommend:

- ONE Best Course, together with a real, working URL to that exact course
- ONE Official Documentation site, together with its real URL
- ONE Best Practice Platform, together with its real URL

Skills:
{skills_text}

Rules:
- Keep answers short.
- Do NOT explain.
- Every Course/Documentation/Practice line MUST be followed by a "Link:" line with a real URL (e.g. https://www.coursera.org/learn/python, https://docs.python.org/3/).
- If you are not fully sure of the exact URL, link to the platform's own search results page for that course name instead of guessing a broken URL.
- Use only this format.

Skill: Python
Course: Python for Everybody (Coursera)
Link: https://www.coursera.org/specializations/python
Documentation: Python Official Documentation
Link: https://docs.python.org/3/
Practice: HackerRank
Link: https://www.hackerrank.com/domains/python

Skill: SQL
Course: SQL for Data Science (Coursera)
Link: https://www.coursera.org/learn/sql-for-data-science
Documentation: PostgreSQL Documentation
Link: https://www.postgresql.org/docs/
Practice: LeetCode
Link: https://leetcode.com/studyplan/top-sql-50/

Continue for every skill.

Return only the resources.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            reasoning_effort="low",
            timeout=45,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Groq Error:", e)
        return "Resources could not be generated."


_LINE_RE = re.compile(r"^(Skill|Course|Documentation|Practice|Link)\s*:\s*(.+)$", re.IGNORECASE)


def _fallback_link(label: str) -> str:
    """A search-results URL so a resource always has *something* clickable,
    even if the model didn't return (or hallucinated) a real course URL."""
    return f"https://www.google.com/search?q={quote_plus(label)}"


def parse_resources(resources_text: str) -> list[dict]:
    """Turns the raw 'Skill/Course/Link/...' text block from get_resources()
    into a list of structured dicts the template can render as clickable
    course links, instead of a wall of plain text.

    [{
        "skill": "Python",
        "course": "Python for Everybody (Coursera)", "course_link": "https://...",
        "documentation": "Python Official Documentation", "documentation_link": "https://...",
        "practice": "HackerRank", "practice_link": "https://...",
    }, ...]
    """
    entries: list[dict] = []
    current: dict = {}
    pending_field = None

    for raw_line in (resources_text or "").splitlines():
        line = raw_line.strip().lstrip("-").strip()
        if not line:
            continue

        match = _LINE_RE.match(line)
        if not match:
            continue

        key, value = match.group(1).lower(), match.group(2).strip()

        if key == "skill":
            if current:
                entries.append(current)
            current = {"skill": value}
            pending_field = None
        elif key == "link":
            if pending_field and current:
                current[f"{pending_field}_link"] = value
            pending_field = None
        elif key in ("course", "documentation", "practice"):
            current[key] = value
            pending_field = key

    if current:
        entries.append(current)

    # Guarantee every resource has a usable link, even if the model
    # skipped a "Link:" line or produced something unusable.
    for entry in entries:
        for field in ("course", "documentation", "practice"):
            if entry.get(field) and not entry.get(f"{field}_link"):
                entry[f"{field}_link"] = _fallback_link(entry[field])

    return entries