from fastapi import APIRouter

from app.api.endpoints import (
    auth,
    cars,
)

router = APIRouter()

router.include_router(auth.router)
router.include_router(cars.router)
