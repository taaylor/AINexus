import functools
import inspect
from collections.abc import Callable
from typing import Any, cast, override

from fastapi import FastAPI
from opentelemetry import context, trace
from opentelemetry.baggage import get_baggage
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.trace import Context, Span
from opentelemetry.util.types import AttributeValue

from .settings import settings as trace_settings


class RequestIdSpanProcessor(SpanProcessor):
    @override
    def on_start(self, span: Span, parent_context: Context | None = None) -> None:
        if parent_context is None:
            parent_context = context.get_current()

        attributes = {
            "http.request_id": cast(
                AttributeValue | None,
                get_baggage("request_id", parent_context),
            ),
            "http.method": cast(
                AttributeValue | None,
                get_baggage("http.method", parent_context),
            ),
            "http.route": cast(
                AttributeValue | None,
                get_baggage("http.route", parent_context),
            ),
        }
        for name, value in attributes.items():
            if value is not None:
                span.set_attribute(name, value)


def init_trace(
    app: FastAPI,
    service: str,
) -> TracerProvider:
    provider = TracerProvider(
        sampler=TraceIdRatioBased(trace_settings.sample_ratio),
        resource=Resource(attributes={"service.name": service}),
    )
    exporter = OTLPSpanExporter(
        endpoint=trace_settings.otlp_endpoint,
        insecure=trace_settings.insecure,
    )

    provider.add_span_processor(RequestIdSpanProcessor())
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)

    return provider


def traced(name: str | None = None):
    def decorate[**P](func: Callable[P, Any]) -> Callable[P, Any]:
        tracer = trace.get_tracer(__name__)
        span_name = name or func.__qualname__

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
                with tracer.start_as_current_span(span_name):
                    return await func(*args, **kwargs)

            return async_wrapper

        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            with tracer.start_as_current_span(span_name):
                return func(*args, **kwargs)

        return sync_wrapper

    return decorate
