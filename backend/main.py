"""
main.py
-------
This is the primary entry point for the UR Tutor backend.
It physically initiates the FastAPI web server, configures CORS (so the frontend can securely talk to it), 
and securely imports the conversational endpoints from the api/routes.py bridge file.
"""
import os
import logging
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from db import chat_store
# from database import engine
# from models import profile_db  # ensure model is imported

# Create all tables
# profile_db.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="UR Tutor API",
    description="Adaptive AI Teaching System",
    version="2.0.0",
    on_startup=[chat_store.clear_all_sessions],
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}

app.include_router(router, tags=["Chat"])
#nohup uvicorn main:app --host 0.0.0.0 --port 80 &