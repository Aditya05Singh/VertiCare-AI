from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.routes import api_router
from app.api.routes.health import health_check


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    description="VertiCare AI - Academic Vertigo Screening & Clinician Decision Support Backend",
    version="1.0.0",
    debug=bool(settings.DEBUG),
    lifespan=lifespan,
)

# CORS configuration foundation
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount root and direct health endpoint
@app.get("/", tags=["Root"])
def root():
    return {
        "status": "ok",
        "service": "verticare-backend",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_url": "/health"
    }

app.get("/health", tags=["Health"])(health_check)

# Mount versioned API routes (/api/v1 and /api)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.include_router(api_router, prefix="/api")
