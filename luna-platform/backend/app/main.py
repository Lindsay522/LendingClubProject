"""Luna Platform — FastAPI entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import build_v1_router
from app.config import get_settings
from app.database import Base, engine

# Import models so SQLAlchemy registers tables
from app import models  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


settings = get_settings()
app = FastAPI(
    title="Luna Platform API",
    description="Full-stack backend for Luna — wardrobe, wellness, analytics, recommendations.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(build_v1_router())


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "luna-platform"}
