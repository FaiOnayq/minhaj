"""Configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Model configurations
RESEARCHER_MODEL = "llama-3.1-8b-instant"
SYNTHESIZER_MODEL = "llama-3.1-8b-instant"
STRUCTURE_MODEL = "llama-3.3-70b-versatile"
VALIDATOR_MODEL = "llama-3.1-8b-instant"

# Search configuration
MAX_SEARCH_RESULTS = 5
SEARCH_DEPTH = "advanced"