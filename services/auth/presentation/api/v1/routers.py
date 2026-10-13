from fastapi.routing import APIRouter

from auth.presentation.api.v1.endpoints.auth import router as auth_router
from auth.presentation.api.v1.endpoints.systems import router as systems_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(systems_router)
