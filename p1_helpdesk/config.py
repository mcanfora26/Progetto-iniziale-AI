import os
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("MODEL", "openai:gpt-5.4")