"""Researcher Agent"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from tools.web_search import search_web
from config import GROQ_API_KEY, RESEARCHER_MODEL


# Initialize LLMs
researcher_llm = ChatGroq(model=RESEARCHER_MODEL, temperature=0.1, api_key=GROQ_API_KEY)


def researcher(state):
    """Search the web for information"""
    query = state["query"]
    
    # Generate search queries
    prompt = f"Generate 1-2 search queries for: {query}\nOutput only the queries, one per line."
    response = researcher_llm.invoke([HumanMessage(content=prompt)])
    
    queries = [line.strip() for line in response.content.split("\n") if line.strip()][:2]
    print(f"$$ Research queries: {queries}")
    # Search
    results = []
    for q in queries:
        results.extend(search_web(q))
    
    state["search_results"] = results
    print(f"✓ Researcher: Found {len(results)} results")
    return state
