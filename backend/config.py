"""
config.py
---------
Central settings loaded from the environment (.env). Importing this module is the
single place that calls load_dotenv(), so every other module just reads from `settings`.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Settings:
    # --- LLM ---
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "claude-haiku-4-5")
    MODEL_MAX_TOKENS: int = int(os.getenv("MODEL_MAX_TOKENS", "8000"))

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
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")


settings = Settings()
