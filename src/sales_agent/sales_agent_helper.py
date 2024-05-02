import os
from langchain_google_genai import ChatGoogleGenerativeAI

from src.sales_agent.constants import GEMINI_API_KEY


def get_llm():
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
    return llm