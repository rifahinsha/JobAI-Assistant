"""
Core AI logic for the Mock Interview feature.

This is the web-safe version of the original ai_interview.zip scripts
(question_generator.py + evaluator.py + input_handler.py), rewritten as
plain functions with no input()/print() calls, so views.py can call them
directly. Session/state handling lives in views.py — this file only talks
to Groq.
"""
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

# Load this app's own .env, same pattern as ats_analyser/logic.py
load_dotenv(Path(__file__).resolve().parent / ".env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"


def generate_questions(role: str, experience: str, jd: str) -> str:
    """Ask Groq for a raw, numbered list of interview questions."""
    prompt = f"""
You are an expert interviewer.

Generate interview questions for a {role} ({experience} level).

Job Description:
{jd}

Rules:
- Cover the complete job description
- Include basic and JD-specific questions
- Include skills, tools, technologies, and project questions
- Start from beginner level and increase difficulty
- No coding problems
- Generate at least 15 questions

Output format:
1. Question
2. Question
3. Question
...
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()


def parse_questions(raw_text: str) -> list[str]:
    """Turn the numbered '1. Question' text block into a clean list."""
    questions = []
    for line in raw_text.split("\n"):
        line = line.strip()
        if line.startswith(tuple(f"{i}." for i in range(1, 50))):
            questions.append(line.split(".", 1)[1].strip())
    return questions


def evaluate_answer(question: str, answer: str) -> dict:
    """Score a single answer and return {'score': int|None, 'feedback': str}."""
    prompt = f"""
You are an interviewer.

Evaluate ONLY this candidate answer.

Question:
{question}

Candidate Answer:
{answer}

Rules:
- Do not create an answer
- Do not assume anything
- Judge only given response

Output:
Score: X/10
Feedback: 1-2 lines
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    raw = response.choices[0].message.content.strip()

    score_match = re.search(r"Score:\s*(\d+)", raw, re.IGNORECASE)
    feedback_match = re.search(r"Feedback:\s*(.+)", raw, re.IGNORECASE | re.DOTALL)

    return {
        "score": int(score_match.group(1)) if score_match else None,
        "feedback": feedback_match.group(1).strip() if feedback_match else raw,
        "raw": raw,
    }
