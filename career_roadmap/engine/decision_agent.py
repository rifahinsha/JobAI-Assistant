def decide_learning_path(state) -> str:
    if len(state["current_skills"]) == 0:
        return "beginner"
    elif len(state["missing_skills"]) <= 3:
        return "fast_track"
    else:
        return "full_roadmap"
