from fastapi import FastAPI

from api.v1.router import router
from common.config import settings

app = FastAPI(title=settings.app_name, version=settings.version)
app.include_router(router, prefix="/api/v1")