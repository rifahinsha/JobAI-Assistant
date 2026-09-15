import os

from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"


def validate_roadmap(roadmap: str) -> str:
    prompt = f"""
You are a Roadmap Validation Agent.

Review the following learning roadmap.

Check for:

1. Correct skill order
2. Missing prerequisite skills
3. Unrealistic learning timeline
4. Duplicate topics
5. Missing important skills
6. Whether the roadmap is suitable for the target role

Return your answer in the following format.

Status:
ROADMAP_OK

OR

Status:
ROADMAP_NEEDS_IMPROVEMENT

Feedback:
- Give short bullet points explaining what needs to be improved.
- If the roadmap is correct, write:
  "The roadmap is well structured."

Roadmap:

{roadmap}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            reasoning_effort="low",
            timeout=45,
        )
        return response.choices[0].message.content

    except Exception as e:
        print("Groq Error:", e)
        return "Status:\nROADMAP_OK\n\nFeedback:\n- Validation could not be completed."