from fastapi.requests import Request
from fastapi.routing import APIRouter
from starlette import status

from auth.presentation.api.v1.schemes.system import HealthResponse

router = APIRouter(
    prefix="/systems",
    tags=["Systems"],
)


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check system health",
    description="Returns the current health status of the service.",
)
async def health_system(request: Request) -> HealthResponse:
    (
        host,
        port,
    ) = (
        (
            request.client.host,
            request.client.port,
        )
        if request.client is not None
        else (None, None)
    )
    return HealthResponse(
        status="ok",
        ip_address=host,
        port=port,
        user_agent=request.headers.get("User-Agent"),
    )
