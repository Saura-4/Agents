import os

from dotenv import load_dotenv
from google import genai
from tavily import TavilyClient

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
