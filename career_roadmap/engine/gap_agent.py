def find_skill_gap(user_skills: list[str], required_skills: list[str]) -> list[str]:
    known = {s.lower() for s in user_skills}
    return [skill for skill in required_skills if skill.lower() not in known]
