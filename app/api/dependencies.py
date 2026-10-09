import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from langgraph.graph.state import CompiledStateGraph

from app.api.rate_limit import RateLimiter
from app.config import Settings, get_settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_agent(request: Request) -> CompiledStateGraph:
    return request.app.state.agent


def verify_access_key(
    key: Annotated[str | None, Security(api_key_header)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    expected = settings.access_key.get_secret_value()
    if not key or not secrets.compare_digest(key.encode(), expected.encode()):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing X-API-Key header.",
        )


def rate_limit(request: Request) -> None:
    limiter: RateLimiter = request.app.state.rate_limiter
    client_id = request.client.host if request.client else "unknown"
    message = limiter.check(client_id)
    if message:
        raise HTTPException(status_code=429, detail=message)