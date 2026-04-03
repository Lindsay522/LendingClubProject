from fastapi import APIRouter

from app.api.routes import auth, closet, outfits, wellness, analytics


def build_v1_router() -> APIRouter:
    r = APIRouter(prefix="/api/v1")
    r.include_router(auth.router, prefix="/auth", tags=["auth"])
    r.include_router(closet.router, prefix="/closet", tags=["closet"])
    r.include_router(outfits.router, prefix="/outfits", tags=["outfits"])
    r.include_router(wellness.router, prefix="/wellness", tags=["wellness"])
    r.include_router(analytics.router, prefix="", tags=["analytics"])
    return r
