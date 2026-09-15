import os

from groq import Groq

from .search_agent import search_trending_skills

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"


def discover_skills(role: str) -> list[str]:
    web_data = search_trending_skills(role)

    prompt = f"""
Target Role:
{role}

Web Data:
{web_data}

You are an expert Technical Recruiter and AI Career Mentor.

Analyze the latest job market information and identify the most important skills required to become a successful {role}.

Rules:

- Focus only on skills required for a learning roadmap.
- Arrange the skills from beginner to advanced.
- Prefer concepts before tools.
- Include only essential skills.
- Avoid duplicate skills.
- Avoid recommending multiple tools that serve the same purpose.
- If multiple tools perform the same job (for example: Power BI and Tableau, TensorFlow and PyTorch), recommend only ONE beginner-friendly and widely used tool.
- Recommend concepts before frameworks and libraries.
- Maximum 15 skills.

Skill Categories (for your understanding only):

1. Fundamentals
2. Programming
3. Core Domain Skills
4. Industry Tools
5. Advanced Topics

Examples:

AI ML Engineer:
Python,
Mathematics,
Statistics,
Data Structures,
Machine Learning,
Deep Learning,
Natural Language Processing,
Computer Vision,
MLOps,
Cloud Computing,
PyTorch

Data Analyst:
Excel,
SQL,
Statistics,
Python,
Pandas,
Data Cleaning,
Data Visualization,
Power BI,
Business Intelligence,
Data Modeling

Backend Developer:
Python,
Object-Oriented Programming,
Data Structures,
SQL,
REST APIs,
FastAPI,
Docker,
AWS

Return only a comma-separated list of skills.

Do NOT return:
- Categories
- Bullet points
- Numbering
- Explanations
- Duplicate technologies
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        reasoning_effort="low",
        timeout=45,
    )

    skills_text = response.choices[0].message.content.strip()

    return [skill.strip() for skill in skills_text.split(",") if skill.strip()]