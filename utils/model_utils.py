import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(model=os.getenv("LLM_MODEL"), temperature=1.0)