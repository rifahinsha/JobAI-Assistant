import os

from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"


def generate_projects(role: str) -> str:
    prompt = f"""
Target Role: {role}

Suggest:

1. Beginner Projects
2. Intermediate Projects
3. Advanced Projects
- Each project:
  Name
  Short Description (2 line)
  Skills Used
- no explanations.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    except Exception as e:
        print("Groq Error:", e)
        return "Project recommendations could not be generated."
