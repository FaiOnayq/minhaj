"""analyst Agent"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from config import GROQ_API_KEY,  ANALYST_MODEL


# Initialize LLMs
analyst_llm = ChatGroq(model=ANALYST_MODEL, temperature=0.3, api_key=GROQ_API_KEY)


def analyst(state):
    """Analyze search results"""
    query = state["query"]
    results = state["search_results"]
    
    if not results:
        state["analysis"] = "No search results found."
        return state
    
    # Format results
    results_text = "\n\n".join([
        f"Source: {r.get('title')}\nContent: {r.get('content')}"
        for r in results[:5]
    ])
    
    # Analyze
    prompt = f"""Analyze these search results for: {query}

Results:
{results_text}

Provide key findings and insights."""
    
    response = analyst_llm.invoke([HumanMessage(content=prompt)])
    state["analysis"] = response.content
    print("✓ Analyst: Analysis complete")
    return state

