from fastapi.routing import APIRouter

from auth.src.presentation.api.v1.public.endpoints.auth import router as auth_router
from auth.src.presentation.api.v1.public.endpoints.systems import (
    router as systems_router,
)

router = APIRouter(prefix="/public/v1")
router.include_router(auth_router)
router.include_router(systems_router)
