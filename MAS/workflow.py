"""Workflow"""
from langgraph.graph import StateGraph, END
from typing import TypedDict
from agents.researcher import researcher
from agents.analyst import analyst
from agents.writer import writer  


class State(TypedDict):
    """Workflow state"""
    query: str
    search_results: list
    analysis: str
    final_output: str


def create_workflow():
    """Build the workflow"""
    workflow = StateGraph(State)
    
    # Add agents
    workflow.add_node("researcher", researcher)
    workflow.add_node("analyst", analyst)
    workflow.add_node("writer", writer)
    
    # Connect them
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "writer")
    workflow.add_edge("writer", END)
    
    return workflow.compile()


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