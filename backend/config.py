

"""
config.py
---------
Central settings loaded from the environment (.env). Importing this module is the
single place that calls load_dotenv(), so every other module just reads from `settings`.

Note: there is no server-side model API key. UR Tutor is bring-your-own-key — each user
supplies their own Anthropic API key from the frontend and it arrives on every /chat
request in the X-Anthropic-Key header.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Settings:
    # --- LLM (Claude Haiku 4.5 on the native Anthropic Messages API) ---
    # The key is per-user and comes from the request, not from here.
    ANTHROPIC_BASE_URL: str = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "claude-haiku-4-5")
    MODEL_MAX_TOKENS: int = int(os.getenv("MODEL_MAX_TOKENS", "8000"))
    # How many per-key agent graphs to keep compiled in memory at once.
    AGENT_CACHE_SIZE: int = int(os.getenv("AGENT_CACHE_SIZE", "32"))

    # --- Auth ---
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-only-insecure-change-me")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))

    # --- Progress / mastery ---
    PASS_THRESHOLD: float = float(os.getenv("PASS_THRESHOLD", "0.8"))

    # --- Persistence (SQLite) ---
    APP_DB_PATH: str = os.getenv("APP_DB_PATH", os.path.join(BASE_DIR, "urtutor.db"))
    CHECKPOINT_DB_PATH: str = os.getenv("CHECKPOINT_DB_PATH", os.path.join(BASE_DIR, "checkpoints.db"))
    STORE_DB_PATH: str = os.getenv("STORE_DB_PATH", os.path.join(BASE_DIR, "agent_store.db"))

    # --- Skills ---
    SKILLS_DIR: str = os.path.join(BASE_DIR, "skills")

    # --- CORS ---
    # Exact allowed origin(s); comma-separated for multiple.
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    # Regex of additional allowed origins. Default covers localhost (any port) plus
    # Vercel and Netlify deployments (production + per-deploy preview URLs).
    CORS_ORIGIN_REGEX: str = os.getenv(
        "CORS_ORIGIN_REGEX",
        r"https?://(localhost|127\.0\.0\.1)(:\d+)?|https://[a-z0-9-]+\.(vercel\.app|netlify\.app)",
    )


settings = Settings()
