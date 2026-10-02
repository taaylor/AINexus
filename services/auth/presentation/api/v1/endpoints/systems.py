from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from fastapi.requests import Request

from auth.presentation.api.v1.schemes.system import HealthResponse

router = APIRouter(prefix="/system")


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check system health",
    description="Returns the current health status of the service.",
    tags=["system"],
)
@inject
async def health_system(
    request: Request,
    sasession: FromDishka[AsyncSession],
) -> HealthResponse:
    await sasession.execute(select(1))
    return HealthResponse(
        status="ok",
        ip_address=request.client.host,
        port=request.client.port,
        user_agent=request.headers.get("User-Agent"),
    )
