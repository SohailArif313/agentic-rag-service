from pydantic import BaseModel, ConfigDict, Field

MAX_QUESTION_LENGTH = 500


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    route: str
    critic_reason: str
    rewrites: int