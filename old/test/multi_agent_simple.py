"""
Multi-Agent System with Groq, Tavily Web Search, and LangGraph
A modular template for building intelligent agent workflows
"""

import os
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from tavily import TavilyClient
import operator
from dotenv import load_dotenv
import json
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Centralized configuration for the multi-agent system"""
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    # Model configurations
    RESEARCHER_MODEL = "llama-3.1-8b-instant"
    ANALYST_MODEL = "llama-3.1-8b-instant"
    WRITER_MODEL = "llama-3.3-70b-versatile"
    
    # Search configuration
    MAX_SEARCH_RESULTS = 5
    SEARCH_DEPTH = "advanced"


# ============================================================================
# STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """Define the state that will be passed between agents"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    search_results: list
    analysis: str
    next_agent: str


# ============================================================================
# TOOLS & UTILITIES
# ============================================================================

class WebSearchTool:
    """Web search tool using Tavily API"""
    
    def __init__(self, api_key: str):
        self.client = TavilyClient(api_key=api_key)
    
    def search(self, query: str, max_results: int = 5, search_depth: str = "advanced") -> list:
        """Perform web search and return results"""
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_answer=True
            )
            return response.get('results', [])
        except Exception as e:
            print(f"Search error: {e}")
            return []


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================


def ResearcherAgent(state):
    """
    Agent generates search queries and retrieves curriculum signals from web
    """
    course_input = state["course_input"]
    
    # Extract key information
    title = course_input["course_title"]
    domain = course_input["subject_domain"]
    level = course_input["education_level"]
    duration = course_input["duration_weeks"]
    
    # Agent decides what to search for
    prompt = f"""You are a curriculum researcher. Generate 5-6 specific search queries to find:
- Course syllabi and curriculum structures for {title}
- {level} level {domain} topics and sequences
- Learning outcomes for {duration}-week courses in {domain}
- Technical coverage: algorithms, frameworks, tools for {title}
- Industry-standard {domain} skills at {level} level

Generate ONLY the search queries, one per line. Be specific and academic."""
    
    response = researcher_llm.invoke([HumanMessage(content=prompt)])
    
    # Parse queries
    queries = [
        line.strip()
        for line in response.content.split("\n")
        if line.strip() and len(line.strip()) > 10
    ][:6]
    
    print(f"✓ Researcher generated {len(queries)} queries")
    for i, q in enumerate(queries, 1):
        print(f"  {i}. {q}")
    
    # Search for each query
    all_results = []
    for query in queries:
        results = search_web(query)
        all_results.extend(results)
    
    # Normalize resources
    normalized_resources = []
    for result in all_results:
        resource = {
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "content": result.get("content", ""),
            "relevance_score": result.get("score", 0),
            "source_type": _detect_source_type(result.get("url", ""))
        }
        normalized_resources.append(resource)
    
    state["search_results"] = normalized_resources
    print(f"✓ Researcher found {len(normalized_resources)} resources")
    # for res in normalized_resources:
    #     print(f"- {res['title']} ({res['url']})")
    #     print(f"   content: {res['content'][:500]}...")
    #     print(f"   type: {res['source_type']}, score: {res['relevance_score']}")
    #     print("=" * 40  )
    #     print("\n")
    # sys.exit(0)
    
    return {**state, "raw_search_results": normalized_resources}


def _detect_source_type(url):
    """Detect if source is academic, documentation, tutorial, etc."""
    url_lower = url.lower()
    if any(x in url_lower for x in ['.edu', 'arxiv', 'scholar', 'academic']):
        return "academic"
    elif any(x in url_lower for x in ['docs', 'documentation', 'reference']):
        return "documentation"
    elif any(x in url_lower for x in ['tutorial', 'course', 'learn']):
        return "tutorial"
    elif any(x in url_lower for x in ['github', 'gitlab']):
        return "code_repository"
    else:
        return "general"

def AnalystAgent(state):
    """
    Agent analyzes resources and structures curriculum signals
    """
    course_input = state["course_input"]
    resources = state["search_results"]
    
    if not resources:
        state["curriculum_structure"] = {"error": "No resources found"}
        return state
    
    # Prepare resources text
    resources_text = "\n\n".join([
        f"Source {i+1} ({r['source_type']}): {r['title']}\n{r['content'][:500]}"
        for i, r in enumerate(resources[:15])
    ])
    
    # Agent analyzes and structures content
    prompt = f"""Analyze these resources and extract curriculum structure for:
Course: {course_input['course_title']}
Level: {course_input['education_level']}
Duration: {course_input['duration_weeks']} weeks
Goals: {course_input['teaching_goals']}

Resources:
{resources_text}

Extract and structure as JSON:
{{
  "topics": [
    {{
      "week": 1,
      "topic_name": "...",
      "subtopics": ["...", "..."],
      "learning_outcomes": ["...", "..."],
      "technical_coverage": {{
        "core_concepts": ["...", "..."],
        "algorithms_models": ["...", "..."],
        "frameworks_tools": ["...", "..."]
      }},
      "difficulty_level": "beginner/intermediate/advanced"
    }}
  ],
  "overall_structure": {{
    "total_weeks": {course_input['duration_weeks']},
    "recommended_prerequisites": ["...", "..."],
    "assessment_pattern": "...",
    "lab_project_ratio": "..."
  }},
  "domain_technical_coverage": {{
    "core_concepts": ["...", "..."],
    "key_algorithms": ["...", "..."],
    "recommended_frameworks": ["...", "..."],
    "standard_libraries": ["...", "..."]
  }}
}}

Generate ONLY valid JSON. Be specific and technical."""
    
    response = analyst_llm.invoke([HumanMessage(content=prompt)])
    
    # Parse JSON
    try:
        # Extract JSON from response
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        curriculum = json.loads(content)
        state["curriculum_structure"] = curriculum
        print(f"✓ Analyst structured {len(curriculum.get('topics', []))} weeks of content")
        print("analyst output:", curriculum)
        
    except json.JSONDecodeError as e:
        print(f"✗ JSON parsing error: {e}")
        state["curriculum_structure"] = {"raw_response": response.content}
    return state




# ============================================================================
# WORKFLOW CONSTRUCTION
# ============================================================================

class MultiAgentWorkflow:
    """Orchestrates the multi-agent workflow using LangGraph"""
    
    def __init__(self):
        # Initialize LLMs
        self.researcher_llm = ChatGroq(
            model=Config.RESEARCHER_MODEL,
            temperature=0.1,
            max_tokens=100,
            api_key=Config.GROQ_API_KEY
        )
        self.analyst_llm = ChatGroq(
            model=Config.ANALYST_MODEL,
            temperature=0.3,
            max_tokens=400,
            api_key=Config.GROQ_API_KEY
        )
        
        # Initialize tools
        self.search_tool = WebSearchTool(Config.TAVILY_API_KEY)
        
        # Initialize agents
        self.researcher = ResearcherAgent(self.researcher_llm, self.search_tool)
        self.analyst = AnalystAgent(self.analyst_llm)
        
        # Build workflow graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Construct the agent workflow graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("researcher", self.researcher)
        workflow.add_node("analyst", self.analyst)
        
        # Define edges (workflow transitions)
        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "analyst")
        workflow.add_edge("analyst", END)
        
        return workflow.compile()
    
    def run(self, query: str) -> dict:
        """Execute the workflow with a given query"""
        initial_state = AgentState(
            messages=[HumanMessage(content=query)],
            query=query,
            search_results=[],
            analysis="",
            next_agent="researcher"
        )
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        return {
            "query": query,
            "search_results_count": len(result["search_results"]),
            
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    # Initialize workflow
    print("🤖 Initializing Multi-Agent System...")
    workflow = MultiAgentWorkflow()
    
    # Example query
    query = {
  "target_topic": "machine learning",
  "learner_level": "intermediate",
  "duration_weeks": 2,
  "preferred_tools": "",
  "learning_goals": "must understand machine learning main concepts",
  "constraints_requests": "Focus on practical labs and minimal math",
  "reference_link": ""
}
    
    print(f"\n📝 Query: {query}")
    print("\n" + "="*80)
    print("🔄 Running multi-agent workflow...\n")
    
    # Execute workflow
    result = workflow.run(query)
    
    # Display results
    print("="*80)
    print("\n✅ FINAL OUTPUT:\n")
    print("\n" + "="*80)
    print(f"\n📊 Metadata:")
    print(f"  - Search results processed: {result['search_results_count']}")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()