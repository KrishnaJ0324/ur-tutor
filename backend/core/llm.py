import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# We instantiate the LLM ONCE globally to save huge overhead
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview", 
    temperature=0.7,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# For quiz generation, we might want lower temp
llm_strict = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview", 
    temperature=0.2,
    google_api_key=os.getenv("GEMINI_API_KEY")
)
