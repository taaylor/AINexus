from fastapi import Depends
from fastapi.routing import APIRouter

from auth.src.presentation.api.v1.dependencies import auth_proxy_data
from auth.src.presentation.api.v1.protected.endpoints.profile import (
    router as profile_router,
)

router = APIRouter(
    prefix="/protected/v1",
    dependencies=[Depends(auth_proxy_data)],
)
router.include_router(profile_router)
