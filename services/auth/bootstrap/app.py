from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from auth.bootstrap.di import initialization_async_container
from auth.common.cors_ext import CorrectCORSMiddleware
from auth.presentation.api.routers import router as api_router


def initialization_app() -> FastAPI:
    container = initialization_async_container()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
        try:
            yield
        finally:
            await container.close()

    app = FastAPI(
        title="AINexus.Auth",
        version="0.1.0",
        docs_url="/docs/swagger",
        redoc_url="/docs/redoc",
        lifespan=lifespan,
        contact={
            "name": "Maksim Ushakov",
        },
        summary="AINexus Auth Service",
        description="""The authentication and user access management service in the NexusAI platform. 
        It is responsible for registration, login, issuance and renewal of JWT tokens, 
        session management, roles and access rights, 
        as well as integration with other microservices of the platform.
        """,
    )

    app.include_router(api_router)
    app.add_middleware(
        CorrectCORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    setup_dishka(container, app)

    return app
