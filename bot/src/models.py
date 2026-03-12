from dataclasses import dataclass

@dataclass
class Car:
    brand: str
    model: str
    year: int
    price: float
    color: str
    url: str

@dataclass
class SearchFilters:
    limit: int = 10
    brand: str | None = None
    model: str | None = None
    min_year: int | None = None
    max_year: int | None = None
    min_price: float | None = None
    max_price: float | None = None
    color: str | None = None

@dataclass
class LLMResult:
    type: str  # 'search', 'direct', 'error'
    text: str | None = None
    filters: dict | None = None