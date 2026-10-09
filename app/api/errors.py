import logging

import openai
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(openai.RateLimitError)
    async def handle_openai_rate_limit(request: Request, exc: openai.RateLimitError):
        logger.error("OpenAI rate/spend limit: %s", exc)
        return JSONResponse(
            status_code=503,
            content={"detail": "The demo has reached its usage limit. Please try again later."},
        )

    @app.exception_handler(openai.OpenAIError)
    async def handle_openai_error(request: Request, exc: openai.OpenAIError):
        logger.error("OpenAI error: %s", exc)
        return JSONResponse(
            status_code=502,
            content={"detail": "The AI service had a problem. Please try again."},
        )