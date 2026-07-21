from typing import TypedDict


class AgentState(TypedDict):
    role: str
    current_skills: list[str]
    required_skills: list[str]
    missing_skills: list[str]
    learning_path: str
    roadmap: str
    resources: str
    projects: str
    validation: str
    validator_feedback: str
    retry_count: int
    max_retry: int


def new_state(role: str, current_skills: list[str]) -> AgentState:
    """Build a fresh pipeline state for one roadmap request."""
    return {
        "role": role,
        "current_skills": current_skills,
        "required_skills": [],
        "missing_skills": [],
        "learning_path": "",
        "roadmap": "",
        "resources": "",
        "projects": "",
        "validation": "",
        "validator_feedback": "",
        "retry_count": 0,
        "max_retry": 3,
    }
