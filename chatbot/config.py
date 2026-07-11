import re

SYSTEM_PROMPT = """
You are JobPath Assistant — a friendly, practical career coach.
You ONLY answer questions related to job seeking and career growth.

You CAN help with:
- Resume and cover letter writing
- Job search strategies (LinkedIn, Naukri, Indeed, etc.)
- Interview preparation and common questions (STAR method, HR rounds)
- Salary negotiation and evaluating job offers
- Career planning, skill building, and fresher guidance
- Internships, campus placements, and cold emailing recruiters
- LinkedIn profile tips and ATS optimization
- Career paths and how to become a professional in a given field
  (e.g. "how to become a data scientist", "is software engineering
  a good career", "what skills do I need for X role")

You CANNOT help with anything else — cooking, sports, math,
movies, general knowledge, coding problems unrelated to careers,
health, relationships, etc.

If the user asks anything off-topic, reply EXACTLY with this message
and nothing else:
"I'm your job search assistant! I can help with resumes, interviews,
salary negotiation, and job hunting strategies. What job-related
question can I answer for you?"

Keep responses concise, friendly, and actionable.
Use bullet points when listing tips.
""".strip() # remove unwanted spaces

JOB_KEYWORDS = [
    "job", "work", "career", "resume", "cv", "curriculum",
    "interview", "hire", "hiring", "salary", "pay", "ctc", "package",
    "apply", "application", "offer", "linkedin", "naukri", "indeed",
    "skill", "fresher", "intern", "internship", "experience",
    "company", "recruiter", "recruitment", "portfolio",
    "cover letter", "placement", "campus", "appraisal",
    "promotion", "layoff", "fired", "resign", "notice period",
    "reference", "ats", "background check", "onboarding",
    # career-path / role-exploration additions
    "profession", "professional", "occupation", "industry", "field",
    "qualification", "qualifications", "degree", "certification",
    "roadmap", "scope", "growth", "switch to", "transition into",
    "become a", "becoming a", "data scientist", "data analyst",
    "software engineer", "engineer", "developer", "designer",
    "manager", "analyst", "consultant", "freelance", "freelancing",
    "remote work", "wfh", "higher studies", "masters", "mba",
]


JOB_PATTERNS = [
    r"how (do|can) i become",
    r"how to become",
    r"what does an? .+ do",
    r"is .+ a good career",
    r"career in .+",
    r"path to becoming",
    r"skills (needed|required) for",
    r"how to get into .+",
    r"day in the life of",
]


def is_job_related(text: str) -> bool:
    """
    Returns True if the message contains a job-related keyword
    OR matches a career-question pattern.
    """
    lower = text.lower()

    if any(keyword in lower for keyword in JOB_KEYWORDS):
        return True

    return any(re.search(pattern, lower) for pattern in JOB_PATTERNS)


OFF_TOPIC_REPLY = (
    "I'm your job search assistant! I can help with resumes, interviews, "
    "salary negotiation, and job hunting strategies. "
    "What job-related question can I answer for you?"
)


SMALL_TALK_KEYWORDS = [
    "ok", "okay", "thanks", "thank you", "thank",
    "great", "got it", "sure", "cool", "nice",
    "hello", "hi", "hey", "bye", "goodbye",
    "yes", "no", "good", "perfect", "awesome",
    "alright", "noted", "understood", "makes sense",
    "wow", "interesting", "helpful", "appreciate"
]


def is_small_talk(text: str) -> bool:
    lower = text.lower().strip()
    return any(lower == word or lower.startswith(word)
               for word in SMALL_TALK_KEYWORDS)