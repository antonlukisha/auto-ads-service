from typing import Any, cast

from sqlalchemy import BinaryExpression, asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.sqlalchemy_models import Car
from app.repositories.base import BaseRepository

logger = get_logger("repositories.cars")


class CarRepository(BaseRepository[Car]):
    def __init__(self, session: AsyncSession):
        super().__init__(Car, session)

    async def get_cars(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        **filters: Any,
    ) -> list[Car]:
        """
        Get cars with filters

        :param skip: Number of cars to skip
        :type skip: int
        :param limit: Number of cars to return
        :type limit: int
        :param sort_by: Column to sort by
        :type sort_by: str
        :param sort_order: Sort order (asc or desc)
        :type sort_order: str
        :param filters: Filters to apply
        :type filters: Any
        :return: List of cars
        :rtype: list[Car]
        """
        try:
            query = select(self.model)

            if filters:
                if brand := filters.get("brand"):
                    query = query.where(self.model.brand.ilike(f"%{brand}%"))
                if model := filters.get("model"):
                    query = query.where(self.model.model.ilike(f"%{model}%"))
                if color := filters.get("color"):
                    query = query.where(self.model.color.ilike(f"%{color}%"))
                if min_price := filters.get("min_price"):
                    query = query.where(cast(BinaryExpression, self.model.price >= min_price))
                if max_price := filters.get("max_price"):
                    query = query.where(cast(BinaryExpression, self.model.price <= max_price))
                if min_year := filters.get("min_year"):
                    query = query.where(cast(BinaryExpression, self.model.year >= min_year))
                if max_year := filters.get("max_year"):
                    query = query.where(cast(BinaryExpression, self.model.year <= max_year))

            sort_column = getattr(self.model, sort_by, self.model.created_at)
            if sort_order == "asc":
                query = query.order_by(asc(sort_column))
            else:
                query = query.order_by(desc(sort_column))

            query = query.offset(skip).limit(limit)

            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting cars: {e}")
            raise e
