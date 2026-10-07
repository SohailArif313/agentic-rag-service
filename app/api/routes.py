from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.schemas import HealthResponse
from app.config import Settings, get_settings

router = APIRouter()


@router.get("/health")
def health(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )