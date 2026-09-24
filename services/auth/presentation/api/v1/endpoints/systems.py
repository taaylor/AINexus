from fastapi.routing import APIRouter
from starlette import status

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
def health_system() -> HealthResponse:
    return HealthResponse(status="ok")
