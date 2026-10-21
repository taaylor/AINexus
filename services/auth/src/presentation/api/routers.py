from fastapi.routing import APIRouter

from auth.src.presentation.api.v1.routers import router as v1_router

router = APIRouter(prefix="/api/auth-service")
router.include_router(v1_router)
