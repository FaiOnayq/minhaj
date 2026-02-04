"""Workflow"""
from langgraph.graph import StateGraph, END
from typing import TypedDict
from agents.researcher import curriculum_researcher
from agents.analyst import content_analyst 
from agents.writer import writer  


class State(TypedDict):
    """Workflow state"""
    query: str
    search_results: list
    analysis: str
    final_output: str

class CourseState(TypedDict):
    """Workflow state for course generation"""
    course_input: dict
    search_results: list
    curriculum_structure: dict
    final_course: dict


def create_workflow():
    """Build the workflow"""
    workflow = StateGraph(CourseState)
    
    # Add agents
    workflow.add_node("curriculum_researcher", curriculum_researcher)
    workflow.add_node("content_analyst", content_analyst)
    workflow.add_node("writer", writer)
    
    # Connect them
    workflow.set_entry_point("curriculum_researcher")
    workflow.add_edge("curriculum_researcher", "content_analyst")
    workflow.add_edge("content_analyst", "writer")
    workflow.add_edge("writer", END)
    
    return workflow.compile()


def generate_course(course_input):
    """
    Generate complete course from input JSON
    
    Args:
        course_input: Dict with course_title, subject_domain, duration_weeks, 
                     education_level, teaching_goals, reference_link
    
    Returns:
        Complete course structure with weekly breakdown, resources, assessments
    """
    graph = create_workflow()
    
    result = graph.invoke({
        "course_input": course_input,
        "search_results": [],
        "curriculum_structure": {},
        "final_course": {}
    })
    
    return result["final_course"]


def run(query):
    """Run the workflow"""
    graph = create_workflow()
    
    result = graph.invoke({
        "query": query,
        "search_results": [],
        "analysis": "",
        "final_output": ""
    })
    
    return result["final_output"]