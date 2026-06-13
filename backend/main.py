"""
main.py
-------
FastAPI entry point for UR Tutor.

Startup (lifespan): create the app DB tables and build the deep-agent harness (opens the
async SQLite checkpointer + store). Shutdown: close those connections. Auth and tutor
routes are mounted here; CORS is restricted to the configured frontend origin.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from db.base import init_db
    from core.agent import init_agent, close_agent

    init_db()
    if not settings.OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY is empty — /chat will fail until it is set in .env")
    await init_agent()
    logger.info("UR Tutor ready (model=%s)", settings.MODEL_NAME)
    try:
        yield
    finally:
        await close_agent()


app = FastAPI(
    title="UR Tutor API",
    description="Adaptive deep-agent tutor with auth, per-user isolation, and mastery-gated progress.",
    version="3.0.0",
    lifespan=lifespan,
)

# Allowed origins: the configured production frontend(s) (FRONTEND_URL may be a
# comma-separated list), plus any localhost/127.0.0.1 port for local dev via the regex.
_allowed_origins = [o.strip() for o in settings.FRONTEND_URL.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}


from auth.routes import router as auth_router  # noqa: E402
from api.routes import router as tutor_router  # noqa: E402

app.include_router(auth_router)
app.include_router(tutor_router)
