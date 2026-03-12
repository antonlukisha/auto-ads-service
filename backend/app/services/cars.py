from app.core.logging import get_logger
from app.core.mappers import CarMapper
from app.models.domain import Car
from app.repositories.cars import CarRepository

logger = get_logger("services.cars")


class CarService:
    def __init__(self, repo: CarRepository):
        self.repo = repo

    async def get_cars(
        self,
        skip: int = 0,
        limit: int = 100,
        brand: str | None = None,
        model: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        color: str | None = None,
        year: int | None = None,
        min_year: int | None = None,
        max_year: int | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[Car]:
        """
        Get cars with filters.

        :param skip: Number of records to skip
        :type skip: int
        :param limit: Number of records to return
        :type limit: int
        :param brand: Filter by brand
        :type brand: str | None
        :param model: Filter by model
        :type model: str | None
        :param min_price: Minimum price
        :type min_price: float | None
        :param max_price: Maximum price
        :type max_price: float | None
        :param color: Filter by color
        :type color: str | None
        :param year: Year
        :type year: int | None
        :param min_year: Minimum year
        :type min_year: int | None
        :param max_year: Maximum year
        :type max_year: int | None
        :param sort_by: Sort field
        :type sort_by: str
        :param sort_order: Sort order
        :type sort_order: str
        :return: List of cars
        :rtype: list[Car]
        """
        try:
            if min_price is not None and max_price is not None and max_price < min_price:
                raise ValueError("max_price must be greater than or equal to min_price")

            if min_year is not None and max_year is not None and max_year < min_year:
                raise ValueError("max_year must be greater than or equal to min_year")

            cars = await self.repo.get_cars(
                skip=skip,
                limit=limit,
                brand=brand,
                model=model,
                year=year,
                min_price=min_price,
                max_price=max_price,
                color=color,
                min_year=min_year,
                max_year=max_year,
                sort_by=sort_by,
                sort_order=sort_order,
            )

            return CarMapper.to_domain_list(cars)
        except Exception as e:
            logger.error(f"Error getting cars: {e}")
            raise e
