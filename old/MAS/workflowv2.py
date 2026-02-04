# workflow.py
"""Enhanced workflow with validation loop"""
from langgraph.graph import StateGraph, END
from states import CourseState
from agents.researcher import curriculum_researcher
from agents.resource_triage import resource_triage_agent
from agents.pedagogy_designer import pedagogy_designer_agent
from agents.technical_depth import technical_depth_agent
from agents.curriculum_validator import curriculum_validator_agent, should_retry_validation
from agents.writer import writer


def create_workflow():
    """Build multi-agent workflow with validation loop"""
    workflow = StateGraph(CourseState)
    
    # Add specialized agents
    workflow.add_node("curriculum_researcher", curriculum_researcher)
    workflow.add_node("resource_triage", resource_triage_agent)
    workflow.add_node("pedagogy_designer", pedagogy_designer_agent)
    workflow.add_node("technical_depth", technical_depth_agent)
    workflow.add_node("curriculum_validator", curriculum_validator_agent)
    workflow.add_node("writer", writer)
    
    # Entry point
    workflow.set_entry_point("curriculum_researcher")
    
    # Linear flow to first validation
    workflow.add_edge("curriculum_researcher", "resource_triage")
    workflow.add_edge("resource_triage", "pedagogy_designer")
    workflow.add_edge("pedagogy_designer", "technical_depth")
    
    # Merge components → validation
    def merge_components(state: CourseState) -> CourseState:
        """Helper node to merge pedagogy + technical specs into draft"""
        return state  # Actual merge happens in validator for simplicity
    
    workflow.add_node("merge_components", merge_components)
    workflow.add_edge("technical_depth", "merge_components")
    workflow.add_edge("merge_components", "curriculum_validator")
    
    # Conditional edge: validation → writer OR retry loop
    workflow.add_conditional_edges(
        "curriculum_validator",
        should_retry_validation,  # Returns "writer" or "pedagogy_designer"
        {
            "writer": "writer",
            "pedagogy_designer": "pedagogy_designer"  # Loop back for redesign
        }
    )
    
    workflow.add_edge("writer", END)
    
    return workflow.compile()


def generate_course(course_input: dict) -> dict:
    """
    Generate complete course with self-correcting validation loop
    
    Args:
        course_input: Dict with course_title, subject_domain, duration_weeks, 
                     education_level, teaching_goals, reference_link
    
    Returns:
        Complete course structure with syllabus, curriculum, and validation report
    """
    graph = create_workflow()
    
    # Initialize state with validation parameters
    initial_state = {
        "course_input": course_input,
        "raw_search_results": [],
        "filtered_resources": [],
        "learning_progression": {},
        "technical_specifications": {},
        "draft_curriculum": {},
        "validation_report": None,
        "final_course": {},
        "validation_attempts": 0,
        "max_validation_attempts": 3  # Configurable retry limit
    }
    
    result = graph.invoke(initial_state)
    
    return result["final_course"]