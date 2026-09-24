from fastapi.routing import APIRouter

from auth.presentation.api.v1.routers import router as v1_router

router = APIRouter(prefix="/api")
router.include_router(v1_router)
