from fastapi import FastAPI

from src.api.routes.health import router as health_router
from src.api.routes.system import router as system_router
from src.api.routes.auth import router as auth_router
from src.core.config import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(system_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix=settings.api_v1_prefix)