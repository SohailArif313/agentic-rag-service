from app.agent.graph import create_agent
from app.agent.state import new_state
from app.config import get_settings

agent = create_agent(get_settings())

questions = [
    "Hi there!",
    "How many days do I have to ask for a refund?",
    "Is express shipping available and what does it cost?",
    "What are your phone support hours?",
]

for question in questions:
    result = agent.invoke(new_state(question))
    print("=" * 60)
    print("Question:", question)
    print("Route:", result["route"], "| Rewrites:", result["rewrites"])
    print("Critic:", result["critic_reason"])
    print("Answer:", result["answer"])
    print("Sources:", result["sources"])