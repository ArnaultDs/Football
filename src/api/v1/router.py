from fastapi import APIRouter

from common.settings import settings
from api.v1.routers.ctl.rate_limiter import rate_limiter_router

router = APIRouter()
router.include_router(rate_limiter_router)

@router.get("/health", tags=["health"])
def read_health(): 
    return {"status": "ok", "version": settings.version}