from typing import Literal, TypedDict

from langchain_core.documents import Document


class AgentState(TypedDict):
    question: str
    search_query: str
    route: Literal["retrieve", "direct"]
    documents: list[Document]
    is_sufficient: bool
    critic_reason: str
    rewrites: int
    answer: str
    sources: list[str]


def new_state(question: str) -> AgentState:
    return AgentState(
        question=question,
        search_query=question,
        route="retrieve",
        documents=[],
        is_sufficient=False,
        critic_reason="",        
        rewrites=0,
        answer="",
        sources=[],
    )