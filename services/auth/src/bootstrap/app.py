from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from auth.src.bootstrap.di import initialization_async_container
from auth.src.common.logger import init_logging
from auth.src.common.settings import settings
from auth.src.presentation.api.exchandlers import exception_handlers
from auth.src.presentation.api.middleware import (
    CorrectCORSMiddleware,
    ExceptionLoggingMiddleware,
)
from auth.src.presentation.api.routers import router as api_router


def initialization_app() -> FastAPI:
    init_logging()
    container = initialization_async_container()
    trace_provider = None

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
        try:
            yield
        finally:
            await container.close()
            if trace_provider is not None:
                trace_provider.shutdown()

    app = FastAPI(
        title="AINexus.Auth",
        version="0.1.0",
        openapi_url="/auth-service/docs/openapi.json",
        docs_url="/auth-service/docs/swagger",
        redoc_url="/auth-service/docs/redoc",
        lifespan=lifespan,
        summary="AINexus Auth Service",
        description="""The authentication and user access management service in the NexusAI platform.
        It is responsible for registration, login, issuance and renewal of JWT tokens,
        session management and user access,
        as well as integration with other microservices of the platform.
        """,
        exception_handlers=exception_handlers,
    )

    app.include_router(api_router)
    app.add_middleware(ExceptionLoggingMiddleware)
    app.add_middleware(
        CorrectCORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    setup_dishka(container, app)

    if settings.trace:
        from services.trace.tracer import init_trace

        trace_provider = init_trace(app, service="AINexus.Auth")

    return app
