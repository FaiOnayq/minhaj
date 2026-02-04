from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """Define the state that will be passed between agents"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_input: dict
    search_queries: list
    web_search_results: list
    preferred_link_content: dict
    synthesized_knowledge: dict
    course_structure: dict
    validated_course: dict
    next_agent: str