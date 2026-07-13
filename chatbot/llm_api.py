import os
from pathlib import Path

from groq import Groq
from .config import SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 1024


def call_llm(history: list[dict]) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *history
        ]
    )
    return response.choices[0].message.content