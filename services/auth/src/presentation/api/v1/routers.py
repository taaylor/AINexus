from fastapi.routing import APIRouter

from auth.src.presentation.api.v1.internal.routers import router as internal_router
from auth.src.presentation.api.v1.protected.routers import (
    router as protected_router,
)
from auth.src.presentation.api.v1.public.routers import router as public_router

router = APIRouter()
router.include_router(public_router)
router.include_router(protected_router)
router.include_router(internal_router)
