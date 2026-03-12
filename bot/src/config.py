import os
from typing import Final

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN: Final = os.getenv("TELEGRAM_TOKEN")
LLM_API_KEY: Final = os.getenv("OPENROUTER_API_KEY")
LLM_MODEL: Final = os.getenv("LLM_MODEL")
