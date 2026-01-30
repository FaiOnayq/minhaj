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
    final_output: str
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

class ResearcherAgent:
    """Agent responsible for gathering information via web search"""
    
    def __init__(self, llm: ChatGroq, search_tool: WebSearchTool):
        self.llm = llm
        self.search_tool = search_tool
        self.system_prompt = """You are a research assistant.\n"
            "Generate 1 or 2 web search queries for the user request.\n\n"
            "RULES:\n"
            "- Output ONLY the queries\n"
            "- One query per line\n"
            "- No explanations\n"
            "- No numbering\n"
            "- No quotes\n"""
    
    def __call__(self, state: AgentState) -> AgentState:
        """Execute research task"""
        query = state["query"]
        
        # Use LLM to refine search query
        refine_prompt = f"{self.system_prompt}\nUser question: {query}"
        response = self.llm.invoke([HumanMessage(content=refine_prompt)])
        
        raw_lines = response.content.split("\n")
        search_queries = [
            line.strip().strip("-•1234567890. ").strip()
            for line in raw_lines
            if line.strip()
        ]
        
        # Fallback if LLM fails
        if not search_queries:
            search_queries = [query]
        print(f"Refined search queries: {search_queries}")
        
        # Perform searches
        all_results = []
        for search_query in search_queries[:2]:  # Limit to 2 searches
            results = self.search_tool.search(
                query=search_query.strip(),
                max_results=Config.MAX_SEARCH_RESULTS
            )
            all_results.extend(results)
        
        # Update state
        state["search_results"] = all_results
        state["messages"].append(AIMessage(
            content=f"Research completed. Found {len(all_results)} results.",
            name="Researcher"
        ))
        state["next_agent"] = "analyst"
        
        return state


class AnalystAgent:
    """Agent responsible for analyzing search results"""
    
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.system_prompt = """You are an analytical expert. Your job is to:
                1. Review search results carefully
                2. Identify key insights and patterns
                3. Synthesize information from multiple sources
                4. Provide a structured analysis

                Focus on accuracy and relevance."""
    
    def __call__(self, state: AgentState) -> AgentState:
        """Execute analysis task"""
        
        query = state["query"]
        search_results = state["search_results"]
        
        if not search_results:
            state["analysis"] = (
                "No reliable web results were found. "
                "Providing a general industry overview based on existing knowledge."
            )
            state["next_agent"] = "writer"
            return state

        
        # Format search results for analysis
        results_text = "\n\n".join([
            f"Source: {r.get('title', 'N/A')}\nURL: {r.get('url', 'N/A')}\nContent: {r.get('content', 'N/A')}"
            for r in search_results[:5]
        ])
        
        # Perform analysis
        analysis_prompt = f"""{self.system_prompt}

User Query: {query}

Search Results:
{results_text}

Provide a comprehensive analysis addressing the user's query. Include:
- Key findings
- Relevant insights
- Important trends or patterns
- Source citations"""
        
        response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
        
        # Update state
        state["analysis"] = response.content
        state["messages"].append(AIMessage(
            content="Analysis completed.",
            name="Analyst"
        ))
        state["next_agent"] = "writer"
        
        return state


class WriterAgent:
    """Agent responsible for creating the final output"""
    
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.system_prompt = ("You are a professional technical writer.\n\n"
    "RULES:\n"
    "- Do NOT repeat points\n"
    "- Max 5 bullet points\n"
    "- Be concise\n"
    "- Cite sources if available\n"
    "- End after the conclusion\n")
    
    def __call__(self, state: AgentState) -> AgentState:
        """Execute writing task"""
        query = state["query"]
        analysis = state["analysis"]
        
        # Generate final output
        writing_prompt = f"""{self.system_prompt}

User Query: {query}

Analysis:
{analysis}

Create a well-structured, comprehensive response that directly addresses the user's query.
Include relevant details and cite sources where appropriate."""
        
        response = self.llm.invoke([HumanMessage(content=writing_prompt)])
        
        # Update state
        state["final_output"] = response.content
        state["messages"].append(AIMessage(
            content="Final output ready.",
            name="Writer"
        ))
        state["next_agent"] = "end"
        
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
        self.writer_llm = ChatGroq(
            model=Config.WRITER_MODEL,
            temperature=0.5,
            max_tokens=400,
            api_key=Config.GROQ_API_KEY
        )
        
        # Initialize tools
        self.search_tool = WebSearchTool(Config.TAVILY_API_KEY)
        
        # Initialize agents
        self.researcher = ResearcherAgent(self.researcher_llm, self.search_tool)
        self.analyst = AnalystAgent(self.analyst_llm)
        self.writer = WriterAgent(self.writer_llm)
        
        # Build workflow graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Construct the agent workflow graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes (agents)
        workflow.add_node("researcher", self.researcher)
        workflow.add_node("analyst", self.analyst)
        workflow.add_node("writer", self.writer)
        
        # Define edges (workflow transitions)
        workflow.set_entry_point("researcher")
        workflow.add_edge("researcher", "analyst")
        workflow.add_edge("analyst", "writer")
        workflow.add_edge("writer", END)
        
        return workflow.compile()
    
    def run(self, query: str) -> dict:
        """Execute the workflow with a given query"""
        initial_state = AgentState(
            messages=[HumanMessage(content=query)],
            query=query,
            search_results=[],
            analysis="",
            final_output="",
            next_agent="researcher"
        )
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        return {
            "query": query,
            "final_output": result["final_output"],
            "search_results_count": len(result["search_results"]),
            "agent_messages": [msg.content for msg in result["messages"]]
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
    query = "What are recent AI startup funding announcements?"
    
    print(f"\n📝 Query: {query}")
    print("\n" + "="*80)
    print("🔄 Running multi-agent workflow...\n")
    
    # Execute workflow
    result = workflow.run(query)
    
    # Display results
    print("="*80)
    print("\n✅ FINAL OUTPUT:\n")
    print(result["final_output"])
    print("\n" + "="*80)
    print(f"\n📊 Metadata:")
    print(f"  - Search results processed: {result['search_results_count']}")
    print(f"  - Agents involved: {len(result['agent_messages'])}")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()