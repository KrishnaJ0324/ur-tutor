import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
# from database import engine
# from models import profile_db  # ensure model is imported

# Create all tables
# profile_db.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="UR Tutor API",
    description="Adaptive AI Teaching System",
    version="2.0.0",
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