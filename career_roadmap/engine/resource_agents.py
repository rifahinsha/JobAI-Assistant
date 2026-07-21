import os

from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def get_resources(skills: list[str]) -> str:
    skills_text = "\n".join(skills)

    prompt = f"""
You are an expert AI Career Mentor.

For each skill below, recommend:

- ONE Best Course
- ONE Official Documentation
- ONE Best Practice Platform

Skills:
{skills_text}

Rules:
- Keep answers short.
- Do NOT explain.
- Use only this format.

Skill: Python
Course: Python for Everybody (Coursera)
Documentation: Python Official Documentation
Practice: HackerRank

Skill: SQL
Course: SQL for Data Science (Coursera)
Documentation: PostgreSQL Documentation
Practice: LeetCode

Continue for every skill.

Return only the resources.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Groq Error:", e)
        return "Resources could not be generated."
