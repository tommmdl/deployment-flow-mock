"""API stateless com métricas de cardinalidade limitada."""

import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field


def create_app() -> FastAPI:
    registry = CollectorRegistry()
    requests = Counter(
        "http_requests_total", "Requisições HTTP", ["method", "route", "status"], registry=registry
    )
    latency = Histogram("http_request_duration_seconds", "Duração HTTP", ["route"], registry=registry)

    @asynccontextmanager
    async def lifespan(api):
        api.state.ready = True
        yield
        api.state.ready = False

    api = FastAPI(title="Deployment Flow", version="1.0.0", lifespan=lifespan)
    api.state.ready = False

    @api.middleware("http")
    async def instrument(request: Request, call_next):
        start = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            route = getattr(request.scope.get("route"), "path", "unmatched")
            if route not in {"/metrics", "/health/live", "/health/ready"}:
                requests.labels(
                    request.method
                    if request.method in {"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"}
                    else "OTHER",
                    route,
                    str(status),
                ).inc()
                latency.labels(route).observe(time.perf_counter() - start)

    @api.get("/")
    def index():
        return {"service": "deployment-flow", "version": os.getenv("APP_VERSION", "dev")}

    @api.get("/health/live")
    def live():
        return {"status": "alive"}

    @api.get("/health/ready")
    def ready(response: Response):
        if not api.state.ready:
            response.status_code = 503
        return {"ready": api.state.ready}

    @api.get("/metrics")
    def metrics():
        return Response(generate_latest(registry), headers={"Content-Type": CONTENT_TYPE_LATEST})

    @api.post("/api/calculate")
    def calculate(payload: Calculation):
        return {"result": add(payload.a, payload.b)}

    return api


class Calculation(BaseModel):
    a: float = Field(ge=-1e12, le=1e12, allow_inf_nan=False)
    b: float = Field(ge=-1e12, le=1e12, allow_inf_nan=False)


def add(a: float, b: float) -> float:
    return a + b


app = create_app()
