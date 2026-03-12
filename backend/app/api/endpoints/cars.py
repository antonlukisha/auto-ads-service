from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_car_service, get_current_user_id
from app.models.schemas import CarResponse, ErrorResponse
from app.services.cars import CarService

router = APIRouter(prefix="/cars", tags=["cars"])


@router.get(
    "/",
    response_model=list[CarResponse],
    summary="Get cars",
    description="Get a list of cars",
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_cars(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    brand: str | None = Query(None, description="Filter by brand"),
    model: str | None = Query(None, description="Filter by model"),
    min_price: float | None = Query(None, ge=0, description="Minimum price"),
    max_price: float | None = Query(None, ge=0, description="Maximum price"),
    color: str | None = Query(None, description="Filter by color"),
    min_year: int | None = Query(
        None, ge=1900, le=datetime.now().year + 1, description="Minimum year"
    ),
    max_year: int | None = Query(
        None, ge=1900, le=datetime.now().year + 1, description="Maximum year"
    ),
    sort_by: str = Query(
        "created_at", pattern="^(price|year|created_at|brand)$", description="Sort field"
    ),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort order"),
    _: str = Depends(get_current_user_id),
    service: CarService = Depends(get_car_service),
):
    try:
        cars = await service.get_cars(
            skip,
            limit,
            brand,
            model,
            min_price,
            max_price,
            color,
            min_year,
            max_year,
            sort_by,
            sort_order,
        )
        return [CarResponse.model_validate(car) for car in cars]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
