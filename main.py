from fastapi import FastAPI
from api.router import router
from core.config import settings
from core.middleware import add_cors_middleware

is_prod = settings.ENVIRONMENT == "production"

app = FastAPI(
    title       = settings.PROJECT_NAME,
    version     = settings.PROJECT_VERSION, 
    docs_url    = None if is_prod else "/docs",
    redoc_url   = None if is_prod else "/redoc",
    openapi_url = None if is_prod else "/openapi.json",
)

add_cors_middleware(app)

app.include_router(router)
