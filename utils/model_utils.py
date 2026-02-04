from utils.load_env_settings import settings
from langchain_openai import ChatOpenAI


model = ChatOpenAI(model=settings.openai.model, temperature=1.0)