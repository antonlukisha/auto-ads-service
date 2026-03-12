import orjson
from openai import AsyncOpenAI
from dotenv import load_dotenv
import socket
from src.logging import get_logger
from src.models import LLMResult

from src.config import LLM_API_KEY, LLM_MODEL, LLM_URL

load_dotenv()
logger = get_logger("llm_agent")


class LLMAgent:
    def __init__(self) -> None:
        self.api_key = LLM_API_KEY
        self.url = LLM_URL
        self.model = LLM_MODEL
        if not self.api_key or not self.url or not self.model:
            logger.error("LLM_API_KEY, LLM_URL, LLM_MODEL are required")
            raise ValueError("LLM_API_KEY, LLM_URL, LLM_MODEL are required")

        self.client = AsyncOpenAI(
            base_url=self.url,
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": f"http://{socket.gethostname()}:5555",
                "X-Title": "Auto Ads Bot"
            }
        )

        self.search_function = {
            "type": "function",
            "function": {
                "name": "search_cars",
                "description": "Поиск автомобилей в базе данных по параметрам",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "brand": {
                            "type": "string",
                            "description": "Марка автомобиля (например: BMW, Toyota, Honda, Mercedes)"
                        },
                        "model": {
                            "type": "string",
                            "description": "Модель автомобиля (например: X5, Camry, Accord)"
                        },
                        "year": {
                            "type": "integer",
                            "description": "Конкретный год выпуска"
                        },
                        "color": {
                            "type": "string",
                            "description": "Цвет автомобиля (например: красный, черный, белый)"
                        },
                        "min_year": {
                            "type": "integer",
                            "description": "Минимальный год выпуска (от)"
                        },
                        "max_year": {
                            "type": "integer",
                            "description": "Максимальный год выпуска (до)"
                        },
                        "min_price": {
                            "type": "number",
                            "description": "Минимальная цена в рублях"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Максимальная цена в рублях"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Количество результатов (по умолчанию 10)",
                            "default": 10
                        }
                    }
                }
            }
        }

    async def invoke(self, user_prompt: str) -> LLMResult:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты — помощник для поиска автомобилей. "
                            "Извлекай параметры поиска из запроса пользователя. "
                            "Если запрос не связан с поиском машин, просто ответь вежливо.\n\n"
                            "Важно: Цены всегда указывай в рублях. "
                            "Важно: Цвета всегда указывай на русском языке. "
                            "Если пользователь говорит 'до 2 млн' — это max_price = 2000000. "
                            "Если 'от 1.5 млн' — min_price = 1500000. "
                            "Если 'после 2020' — min_year = 2020. "
                            "Если 'до 2018' — max_year = 2018."
                        )
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                tools=[self.search_function],
                tool_choice="auto",
                temperature=0.1
            )

            message = response.choices[0].message

            if message.tool_calls and len(message.tool_calls) > 0:
                tool_call = message.tool_calls[0]
                filters = orjson.loads(tool_call.function.arguments)
                logger.info(f"LLM extracted filters: {filters}")

                return LLMResult(
                    success=True,
                    filters=filters,
                    text=None
                )
            else:
                logger.info(f"LLM did not find any filters: {message.content}")
                return LLMResult(
                    success=False
                )

        except Exception as e:
            logger.error(f"Error in LLM: {e}")
            return LLMResult(
                success=False
            )


llm = LLMAgent()