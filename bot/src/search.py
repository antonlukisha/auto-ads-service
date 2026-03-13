from typing import cast

from sqlalchemy import BinaryExpression, asc, select
from sqlalchemy.sql import and_

from src.database import get_db
from src.llm_agent import llm
from src.logging import get_logger
from src.models import Car, Filter, LLMResult
from src.sqlalchemy_models import Car as DBCar

logger = get_logger("search")


async def search_cars_via_llm(user_prompt: str) -> str:
    """
    Search cars via LLM.

    :param user_prompt: User prompt
    :type user_prompt: str
    :return: Answer from LLM
    :rtype: str
    """
    try:
        result: LLMResult = await llm.invoke(user_prompt)

        if not result.success:
            raise Exception("Request failed")
        filters = Filter(
            limit=result.filters.get("limit", 10),
            brand=result.filters.get("brand"),
            model=result.filters.get("model"),
            year=result.filters.get("year"),
            color=result.filters.get("color"),
            min_price=result.filters.get("min_price"),
            max_price=result.filters.get("max_price"),
            min_year=result.filters.get("min_year"),
            max_year=result.filters.get("max_year"),
        )

        cars: list[Car] = await get_cars_from_db(filters)
        return format_answer(user_prompt, cars, filters)

    except Exception as e:
        logger.error(f"Error while searching cars: {e}")
        raise Exception("Не удалось найти автомобиль")


async def get_cars_from_db(filters: Filter) -> list[Car]:
    """
    Get cars from DB.

    :param filters: Filters
    :type filters: Filter
    :return: List of cars
    :rtype: list[Car]
    """
    cars = []

    try:
        async for session in get_db():
            query = select(DBCar)

            conditions = []

            if filters.brand:
                conditions.append(DBCar.brand.ilike(f"%{filters.brand}%"))
            if filters.model:
                conditions.append(DBCar.model.ilike(f"%{filters.model}%"))
            if filters.color:
                conditions.append(DBCar.color.ilike(f"%{filters.color}%"))

            if filters.min_price is not None:
                conditions.append(cast(BinaryExpression, DBCar.price >= filters.min_price))
            if filters.max_price is not None:
                conditions.append(cast(BinaryExpression, DBCar.price <= filters.max_price))

            if filters.min_year is not None:
                conditions.append(cast(BinaryExpression, DBCar.year >= filters.min_year))
            if filters.max_year is not None:
                conditions.append(cast(BinaryExpression, DBCar.year <= filters.max_year))

            if filters.year is not None:
                conditions.append(cast(BinaryExpression, DBCar.year == filters.year))

            if conditions:
                query = query.where(and_(*conditions))

            query = query.order_by(asc(DBCar.price))

            if filters.limit:
                query = query.limit(filters.limit)

            result = await session.execute(query)
            cars = list(result.scalars().all())
            break
        return [Car.from_sqlalchemy(c) for c in cars]
    except Exception as e:
        logger.error(f"Error getting cars: {e}")
        raise e


def format_answer(user_prompt: str, cars: list[Car], filters: Filter) -> str:
    """
    Format answer.

    :param user_prompt: User prompt
    :type user_prompt: str
    :param cars: List of cars
    :type cars: list[Car]
    :param filters: Filter params
    :type filters: Filter
    :return: Formatted answer
    :rtype: str
    """
    if not cars:
        return f"По запросу `{user_prompt}` ничего не найдено.\n\nПопробуйте изменить параметры поиска."

    filter_desc = []
    if filters.brand:
        filter_desc.append(f"марка: {filters.brand}")
    if filters.model:
        filter_desc.append(f"модель: {filters.model}")
    if filters.color:
        filter_desc.append(f"цвет: {filters.color}")
    if filters.min_price or filters.max_price:
        price_desc = []
        if filters.min_price:
            price_desc.append(f"от {filters.min_price:,.0f}")
        if filters.max_price:
            price_desc.append(f"до {filters.max_price:,.0f}")
        if price_desc:
            filter_desc.append(f"цена {' '.join(price_desc)} ₽")
    if filters.min_year or filters.max_year:
        year_desc = []
        if filters.min_year:
            year_desc.append(f"c {filters.min_year}")
        if filters.max_year:
            year_desc.append(f"по {filters.max_year}")
        if year_desc:
            filter_desc.append(f"год {' '.join(year_desc)}")

    header = f"По запросу: {', '.join(filter_desc)}\n\n" if filter_desc else ""

    if len(cars) == 1:
        car = cars[0]
        return header + (
            f"Найден 1 автомобиль:\n\n"
            f"*{car.brand} {car.model}* ({car.year})\n"
            f"Стоимость: {car.price:,.0f} ₽\n"
            f"Цвет: {car.color}\n"
            f"[Смотреть объявление]({car.url})"
        )

    lines = [header + f"Найдено {len(cars)} автомобилей(я):\n"]

    for i, car in enumerate(cars, 1):
        lines.append(
            f"{i}. *{car.brand} {car.model}* ({car.year})\n"
            f"Стоимость: {car.price:,.0f} ₽\n"
            f"Цвет: {car.color}\n"
            f"[Смотреть объявление]({car.url})"
        )

    return "\n\n".join(lines)
