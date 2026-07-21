from langgraph.graph import StateGraph, END

from .state import AgentState
from .skill_agent import discover_skills
from .gap_agent import find_skill_gap
from .decision_agent import decide_learning_path
from .roadmap_agent import generate_roadmap
from .validation_agent import validate_roadmap
from .resource_agents import get_resources
from .project_agent import generate_projects

workflow = StateGraph(AgentState)


def skill_node(state: AgentState):
    skills = discover_skills(state["role"])
    return {"required_skills": skills}


def gap_node(state: AgentState):
    if len(state["current_skills"]) == 0:
        missing_skills = state["required_skills"]
    else:
        missing_skills = find_skill_gap(state["current_skills"], state["required_skills"])
    return {"missing_skills": missing_skills}


def decision_node(state: AgentState):
    return {"learning_path": decide_learning_path(state)}


def roadmap_node(state: AgentState):
    roadmap = generate_roadmap(
        state["role"],
        state["missing_skills"],
        state["learning_path"],
        state["validator_feedback"],
    )
    return {"roadmap": roadmap}


def validation_node(state: AgentState):
    validation = validate_roadmap(state["roadmap"])
    return {"validation": validation, "validator_feedback": validation}


def resource_node(state: AgentState):
    return {"resources": get_resources(state["missing_skills"])}


def project_node(state: AgentState):
    return {"projects": generate_projects(state["role"])}


def retry_node(state: AgentState):
    return {"retry_count": state["retry_count"] + 1}


workflow.add_node("skill", skill_node)
workflow.add_node("gap", gap_node)
workflow.add_node("decision", decision_node)
workflow.add_node("roadmap", roadmap_node)
workflow.add_node("validation", validation_node)
workflow.add_node("resource", resource_node)
workflow.add_node("project", project_node)
workflow.add_node("retry", retry_node)

workflow.set_entry_point("skill")

workflow.add_edge("skill", "gap")
workflow.add_edge("gap", "decision")
workflow.add_edge("decision", "roadmap")
workflow.add_edge("roadmap", "validation")


def validation_router(state: AgentState):
    if "ROADMAP_OK" in state["validation"]:
        return "approved"
    if state["retry_count"] < state["max_retry"]:
        return "retry"
    return "approved"


workflow.add_conditional_edges(
    "validation",
    validation_router,
    {"approved": "resource", "retry": "retry"},
)

workflow.add_edge("resource", "project")
workflow.add_edge("project", END)
workflow.add_edge("retry", "roadmap")

graph = workflow.compile()
