import os

from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def generate_roadmap(role: str, skills: list[str], learning_path: str, feedback: str = "") -> str:
    skills_text = ", ".join(skills)

    prompt = f"""
You are an expert AI Career Mentor.

Target Role:
{role}

Learning Path:
{learning_path}

Skills to Learn:
{skills_text}

Previous Validator Feedback:
{feedback}

Instructions:

- If there is no validator feedback, generate a fresh roadmap.
- If validator feedback is provided, revise the roadmap to fix ONLY the issues mentioned.
- Keep the good parts of the roadmap unchanged.
- Do not introduce duplicate topics.
- Ensure the skill order is logical.
- Include all important prerequisite skills.
- Make the timeline realistic.
- Generate a roadmap suitable for the selected learning path.

Learning Path Rules:

If learning_path is "beginner":
- Create an 8-week roadmap.
- Assume the user has no prior knowledge.

If learning_path is "fast_track":
- Create a 4-week roadmap.
- Focus only on the missing skills.

If learning_path is "full_roadmap":
- Create a detailed 12-week roadmap.
- Cover fundamentals to advanced topics.

For each week include:
1. Topics to Study
2. Recommended Learning Platform
3. Practice Task or Mini Project
4. A short explanation (1-2 lines)

Return ONLY the roadmap.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    except Exception as e:
        print("Groq Error:", e)
        return "Roadmap generation failed."
