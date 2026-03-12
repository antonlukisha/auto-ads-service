from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_auth_service
from app.models.schemas import (
    ErrorResponse,
    LoginRequest,
    LoginResponse,
    UserResponse,
)
from app.services.auth import AuthService

router = APIRouter(tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Admin user login",
    description="Authenticate admin user and return JWT token",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def login(request: LoginRequest, service: AuthService = Depends(get_auth_service)):
    try:
        access_token, user = await service.login(request.username, request.password)

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=str(user.id),
                username=user.username,
                created_at=user.created_at,
            ),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
