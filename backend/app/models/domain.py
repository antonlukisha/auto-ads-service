from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Car(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    brand: str
    model: str
    year: int
    price: float
    color: str
    url: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    password_hash: str
    created_at: datetime | None = None
