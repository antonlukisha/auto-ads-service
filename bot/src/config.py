import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()

POSTGRES_DSN: Final = os.getenv("POSTGRES_DSN")
TELEGRAM_TOKEN: Final = os.getenv("TELEGRAM_TOKEN")
LLM_URL: Final = os.getenv("LLM_URL")
LLM_API_KEY: Final = os.getenv("LLM_API_KEY")
LLM_MODEL: Final = os.getenv("LLM_MODEL")
