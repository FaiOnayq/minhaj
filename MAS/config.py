"""Configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Models
RESEARCHER_MODEL = "llama-3.1-8b-instant"
ANALYST_MODEL = "llama-3.1-8b-instant"
WRITER_MODEL = "llama-3.3-70b-versatile"

# Search Settings
MAX_SEARCH_RESULTS = 5
SEARCH_DEPTH = "advanced"