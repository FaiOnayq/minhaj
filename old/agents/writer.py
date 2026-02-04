"""Writer Agent"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from config import GROQ_API_KEY, WRITER_MODEL


# Initialize LLMs

writer_llm = ChatGroq(model=WRITER_MODEL, temperature=0.5, api_key=GROQ_API_KEY)


def writer(state):
    """Create final output"""
    query = state["query"]
    analysis = state["analysis"]
    
    prompt = f"""Create a clear response for: {query}

Analysis:
{analysis}

Write a concise, well-structured answer."""
    
    response = writer_llm.invoke([HumanMessage(content=prompt)])
    state["final_output"] = response.content
    print("✓ Writer: Output ready")
    return state