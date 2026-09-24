from fastapi.routing import APIRouter

from auth.presentation.api.v1.endpoints.systems import router as systems_router

router = APIRouter(prefix="/v1")
router.include_router(systems_router)
