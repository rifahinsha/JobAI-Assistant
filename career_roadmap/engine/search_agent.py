import os

from tavily import TavilyClient

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None


def search_trending_skills(role: str) -> str:
    """Pull recent job-posting text for the role. Returns '' on any failure
    so the Skill Agent can safely fall back to LLM-only knowledge."""
    if _client is None:
        return ""

    query = f"{role} skills required in recent job postings"

    try:
        results = _client.search(query=query, max_results=5)

        all_text = ""
        for item in results["results"]:
            all_text += item["content"] + "\n\n"

        return all_text

    except Exception as e:
        print("[Search Agent Error]", e)
        return ""
