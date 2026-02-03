"""Workflow"""
from langgraph.graph import StateGraph, END
import operator
from langchain_groq import ChatGroq
from tools.web_search import WebSearchTool
from tools.links_fetcher import PreferredLinkFetcher
from agents.researcher import ResearcherAgent
from agents.knowledge_synthesizer import KnowledgeSynthesizerAgent
from agents.structure_builder import StructureBuilderAgent
from agents.validation import ValidationAgent
import config
from agent_state import AgentState




class Workflow:
    """Orchestrates the multi-agent course generation workflow"""
    
    def __init__(self):
        # Initialize LLMs
        self.researcher_llm = ChatGroq(
            model=config.RESEARCHER_MODEL,
            temperature=0.1,
            max_tokens=500,
            api_key=config.GROQ_API_KEY
        )
        self.synthesizer_llm = ChatGroq(
            model=config.SYNTHESIZER_MODEL,
            temperature=0.3,
            max_tokens=2000,
            api_key=config.GROQ_API_KEY
        )
        self.structure_llm = ChatGroq(
            model=config.STRUCTURE_MODEL,
            temperature=0.3,
            max_tokens=3000,
            api_key=config.GROQ_API_KEY
        )
        self.validator_llm = ChatGroq(
            model=config.VALIDATOR_MODEL,
            temperature=0.2,
            max_tokens=3000,
            api_key=config.GROQ_API_KEY
        )
        
        # Initialize tools
        self.search_tool = WebSearchTool(config.TAVILY_API_KEY)
        self.link_fetcher = PreferredLinkFetcher()
        
        # Initialize agents
        self.researcher = ResearcherAgent(self.researcher_llm, self.search_tool, self.link_fetcher)
        self.synthesizer = KnowledgeSynthesizerAgent(self.synthesizer_llm)
        self.structure_builder = StructureBuilderAgent(self.structure_llm)
        self.validator = ValidationAgent(self.validator_llm)
        
        # Build workflow graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Construct the agent workflow graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("researcher", self.researcher)
        workflow.add_node("synthesizer", self.synthesizer)
        workflow.add_node("structure_builder", self.structure_builder)
        workflow.add_node("validator", self.validator)
        
        # Define edges (workflow transitions)
        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "synthesizer")
        workflow.add_edge("synthesizer", "structure_builder")
        workflow.add_edge("structure_builder", "validator")
        workflow.add_edge("validator", END)
        
        return workflow.compile()
    
    def run(self, user_input: dict) -> dict:
        """Execute the workflow with user input"""
        initial_state = AgentState(
            messages=[],
            user_input=user_input,
            search_queries=[],
            web_search_results=[],
            preferred_link_content={},
            synthesized_knowledge={},
            course_structure={},
            validated_course={},
            next_agent="researcher"
        )
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        return {
            "user_input": user_input,
            "search_queries": result["search_queries"],
            "web_results_count": len(result["web_search_results"]),
            "preferred_link_fetched": result["preferred_link_content"].get("success", False),
            "synthesized_knowledge": result["synthesized_knowledge"],
            "course_structure": result["course_structure"],
            "validation_results": result["validated_course"],
            "final_course": result["validated_course"].get("final_course", {})
        }




def create_workflow():
    """Build the workflow"""
    workflow = StateGraph(CourseState)
    
    # Add agents
    workflow.add_node("curriculum_researcher", curriculum_researcher)
    workflow.add_node("content_analyst", content_analyst)
    
    # Connect them
    workflow.set_entry_point("curriculum_researcher")
    workflow.add_edge("curriculum_researcher", "content_analyst")
    # workflow.add_edge("content_analyst", "writer")
    # workflow.add_edge("writer", END)
    workflow.add_edge("content_analyst", END)
    
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