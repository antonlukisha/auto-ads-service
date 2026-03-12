from src.logging import get_logger
from src.models import LLMResult
from src.models import Filter
from src.models import Car
from src.llm_agent import llm

logger = get_logger("search")

async def search_cars_via_llm(user_prompt: str) -> str:
    try:
        result: LLMResult = await llm.invoke(user_prompt)
        logger.info(result.success)

        if not result.success:
            raise Exception("Request failed")
        logger.info("1")
        filters = Filter(
            limit=result.filters.get("limit", 10),
            brand=result.filters.get("brand"),
            model=result.filters.get("model"),
            year=result.filters.get("year"),
            color=result.filters.get("color"),
            min_price=result.filters.get("min_price"),
            max_price=result.filters.get("max_price"),
            min_year=result.filters.get("min_year"),
            max_year=result.filters.get("max_year")
        )
        logger.info("2")

        cars: list[Car] = [] # await db.get_cars(filters)
        return format_answer(user_prompt, cars, filters)


    except Exception as e:
        logger.error(f"Error while searching cars: {e}")
        raise Exception("Не удалось найти автомобиль")


def format_answer(user_prompt: str, cars: list[Car], filters: Filter) -> str:
    return f"Найдено {len(cars)} автомобилей по запросу {user_prompt}.\n{cars} {filters}"
