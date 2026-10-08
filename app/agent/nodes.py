from typing import Literal

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, Field

from app.agent.state import AgentState
from app.rag.vector_store import search

ROUTER_PROMPT = """You route questions for a company support assistant.
Answer 'retrieve' if the question needs company information (policies, shipping, accounts, products).
Answer 'direct' only for greetings, thanks or small talk.
When unsure, answer 'retrieve'."""

CRITIC_PROMPT = """You check whether retrieved documents contain enough information to answer a question.
Say the documents are sufficient only if the answer is clearly stated in them.
If they are only loosely related, or the specific fact is missing, say they are not sufficient.
Do not use outside knowledge."""

REWRITE_PROMPT = """You rewrite questions into better search queries for a company knowledge base.
Use clear keywords and drop filler words. Do not answer the question.
Return only the new query."""

ANSWER_PROMPT = """You answer questions using only the provided documents.
Be short and clear. Do not add facts that are not in the documents.
In 'sources', list only the source names (the text in square brackets) of documents you actually used."""

DIRECT_PROMPT = """You are a friendly company support assistant.
Reply briefly to greetings or small talk. If the user needs company information, ask them to put a specific question."""

NOT_FOUND_MESSAGE = (
    "I could not find this information in the available documents. "
    "Please contact our support team for help."
)


class RouteDecision(BaseModel):
    route: Literal["retrieve", "direct"] = Field(
        description="'retrieve' if company documents are needed, 'direct' for small talk."
    )


class CriticVerdict(BaseModel):
    reason: str = Field(description="One short sentence explaining the decision.")
    is_sufficient: bool = Field(
        description="True only if the documents clearly contain the answer."
    )


class AnswerOutput(BaseModel):
    answer: str = Field(description="The final answer, using only the documents.")
    sources: list[str] = Field(description="Source names of the documents actually used.")


def format_documents(documents: list[Document]) -> str:
    if not documents:
        return "(no documents)"
    return "\n\n".join(
        f"[{doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in documents
    )


class AgentNodes:
    def __init__(self, llm: BaseChatModel, vector_store: Chroma, top_k: int):
        self.llm = llm
        self.vector_store = vector_store
        self.top_k = top_k
        self.router_llm = llm.with_structured_output(RouteDecision)
        self.critic_llm = llm.with_structured_output(CriticVerdict)
        self.answer_llm = llm.with_structured_output(AnswerOutput)

    def router(self, state: AgentState) -> dict:
        decision = self.router_llm.invoke(
            [("system", ROUTER_PROMPT), ("human", state["question"])]
        )
        return {"route": decision.route}

    def retrieve(self, state: AgentState) -> dict:
        documents = search(self.vector_store, state["search_query"], k=self.top_k)
        return {"documents": documents}

    def critic(self, state: AgentState) -> dict:
        human_message = (
            f"Question: {state['question']}\n\n"
            f"Documents:\n{format_documents(state['documents'])}"
        )
        verdict = self.critic_llm.invoke(
            [("system", CRITIC_PROMPT), ("human", human_message)]
        )
        return {
            "is_sufficient": verdict.is_sufficient,
            "critic_reason": verdict.reason,
        }

    def rewrite(self, state: AgentState) -> dict:
        human_message = (
            f"Question: {state['question']}\n"
            f"Previous query: {state['search_query']}\n"
            f"Why it failed: {state['critic_reason']}"
        )
        reply = self.llm.invoke([("system", REWRITE_PROMPT), ("human", human_message)])
        return {
            "search_query": str(reply.content).strip(),
            "rewrites": state["rewrites"] + 1,
        }

    def generate(self, state: AgentState) -> dict:
        if state["route"] == "direct":
            reply = self.llm.invoke(
                [("system", DIRECT_PROMPT), ("human", state["question"])]
            )
            return {"answer": str(reply.content).strip(), "sources": []}

        if not state["is_sufficient"]:
            return {"answer": NOT_FOUND_MESSAGE, "sources": []}

        human_message = (
            f"Question: {state['question']}\n\n"
            f"Documents:\n{format_documents(state['documents'])}"
        )
        output = self.answer_llm.invoke(
            [("system", ANSWER_PROMPT), ("human", human_message)]
        )
        retrieved = {doc.metadata.get("source", "unknown") for doc in state["documents"]}
        sources = [name for name in output.sources if name in retrieved]
        return {"answer": output.answer, "sources": sources}