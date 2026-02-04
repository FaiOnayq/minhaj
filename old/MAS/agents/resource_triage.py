# agents/resource_triage.py
"""Agent 1: Filters and scores resources for quality/relevance"""
from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict
from states import CourseState
from tools.Curriculum import CurriculumTools


tools = CurriculumTools()


def resource_triage_agent(state: CourseState) -> CourseState:
    """Filters raw search results by relevance and authority"""
    print("🔍 Triage Agent: Filtering resources...")
    
    course = state["course_input"]
    filtered = tools.filter_resources_by_relevance(
        state["raw_search_results"], 
        course["course_title"],
        course["subject_domain"]
    )
    
    print(f"✓ Kept {len(filtered)}/{len(state['raw_search_results'])} relevant resources")
    
    return {
        **state,
        "filtered_resources": filtered,
        "validation_attempts": 0  # Initialize counter for validation loop
    }