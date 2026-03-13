from dataclasses import dataclass
from typing import Any


@dataclass
class Car:
    brand: str
    model: str
    year: int
    price: float
    color: str
    url: str

    @classmethod
    def from_sqlalchemy(cls, sa_car: Any) -> "Car":
        """Create a Car object from a SQLAlchemy Car object."""
        return cls(
            brand=sa_car.brand,
            model=sa_car.model,
            year=sa_car.year,
            price=sa_car.price,
            color=sa_car.color,
            url=sa_car.url,
        )


@dataclass
class Filter:
    limit: int = 10
    brand: str | None = None
    model: str | None = None
    color: str | None = None
    year: str | None = None
    min_year: int | None = None
    max_year: int | None = None
    min_price: float | None = None
    max_price: float | None = None


@dataclass
class LLMResult:
    success: bool = False
    text: str | None = None
    filters: dict | None = None
