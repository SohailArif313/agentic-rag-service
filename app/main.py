import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agent.graph import create_agent
from app.api.errors import register_error_handlers
from app.api.rate_limit import RateLimiter
from app.api.routes import router
from app.config import get_settings
from app.rag.indexing import index_docs_folder, is_index_empty
from app.rag.vector_store import get_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    vector_store = get_vector_store(settings)
    if is_index_empty(vector_store):
        logger.info("Index is empty. Indexing documents from %s", settings.docs_dir)
        count = index_docs_folder(settings, vector_store)
        logger.info("Indexed %s chunks", count)

    app.state.agent = create_agent(settings, vector_store)
    app.state.rate_limiter = RateLimiter(
        per_minute=settings.rate_limit_per_minute,
        daily_cap=settings.daily_request_cap,
    )
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

register_error_handlers(app)
app.include_router(router)