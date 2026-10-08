from langchain_openai import ChatOpenAI

from app.config import Settings


def get_llm(settings: Settings) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.chat_model,
        api_key=settings.openai_api_key,
        temperature=0,
    )