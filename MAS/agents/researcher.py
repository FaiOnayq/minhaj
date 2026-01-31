"""Researcher Agent"""
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from tools.web_search import search_web
from config import GROQ_API_KEY, RESEARCHER_MODEL
import sys

# Initialize LLMs
researcher_llm = ChatGroq(model=RESEARCHER_MODEL, temperature=0.1, api_key=GROQ_API_KEY)

def curriculum_researcher(state):
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
    
    return state


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