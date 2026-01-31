"""Search Tool"""
from tavily import TavilyClient
from config import TAVILY_API_KEY, MAX_SEARCH_RESULTS, SEARCH_DEPTH


def search_web(query):
    """Search the web using Tavily"""
    client = TavilyClient(api_key=TAVILY_API_KEY)
    try:
        response = client.search(
            query=query,
            max_results=MAX_SEARCH_RESULTS,
            search_depth=SEARCH_DEPTH,
            include_answer=True
        )
        return response.get('results', [])
    except Exception as e:
        print(f"Search error: {e}")
        return []