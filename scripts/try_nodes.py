from app.agent.llm import get_llm
from app.agent.nodes import AgentNodes
from app.agent.state import new_state
from app.config import get_settings
from app.rag.vector_store import get_vector_store

settings = get_settings()
nodes = AgentNodes(get_llm(settings), get_vector_store(settings), settings.top_k)

questions = [
    "Hi there!",
    "How many days do I have to ask for a refund?",
    "What are your phone support hours?",
]

for question in questions:
    print("=" * 60)
    print("Question:", question)
    state = new_state(question)

    state.update(nodes.router(state))
    print("Route:", state["route"])
    if state["route"] == "direct":
        continue

    state.update(nodes.retrieve(state))
    print("Sources:", [doc.metadata["source"] for doc in state["documents"]])

    state.update(nodes.critic(state))
    print("Sufficient:", state["is_sufficient"], "|", state["critic_reason"])