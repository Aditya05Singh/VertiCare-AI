from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.routes import api_router
from app.api.routes.health import health_check
from app.db.seed_demo import seed_demo_accounts


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode")
    try:
        seed_demo_accounts()
    except Exception as e:
        logger.warning(f"Demo account seeding skipped: {e}")
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

@app.get("/download/research-bundle", tags=["Downloads"])
def download_research_bundle():
    from fastapi.responses import FileResponse
    from fastapi import HTTPException
    import os
    candidates = [
        os.path.abspath("VertiCare_AI_Research_Bundle.zip"),
        os.path.abspath("../VertiCare_AI_Research_Bundle.zip"),
        "/Users/dineshkumarsingh/Documents/antigravity/goofy-mendeleev/VertiCare_AI_Research_Bundle.zip"
    ]
    for c in candidates:
        if os.path.exists(c):
            return FileResponse(
                path=c,
                filename="VertiCare_AI_Research_Bundle.zip",
                media_type="application/zip"
            )
    raise HTTPException(status_code=404, detail="Research bundle archive not found")

@app.get("/download/report-docx", tags=["Downloads"])
def download_report_docx():
    from fastapi.responses import FileResponse
    from fastapi import HTTPException
    import os
    candidates = [
        os.path.abspath("VertiCare_AI_BCSE497J_Project_I_Report.docx"),
        os.path.abspath("../VertiCare_AI_BCSE497J_Project_I_Report.docx"),
        "/Users/dineshkumarsingh/Documents/antigravity/goofy-mendeleev/VertiCare_AI_BCSE497J_Project_I_Report.docx"
    ]
    for c in candidates:
        if os.path.exists(c):
            return FileResponse(
                path=c,
                filename="VertiCare_AI_BCSE497J_Project_I_Report.docx",
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    raise HTTPException(status_code=404, detail="Project report DOCX not found")

@app.get("/download/presentation-pptx", tags=["Downloads"])
def download_presentation_pptx():
    from fastapi.responses import FileResponse
    from fastapi import HTTPException
    import os
    candidates = [
        os.path.abspath("VertiCare_AI_BCSE497J_Project_I_Presentation.pptx"),
        os.path.abspath("../VertiCare_AI_BCSE497J_Project_I_Presentation.pptx"),
        "/Users/dineshkumarsingh/Documents/antigravity/goofy-mendeleev/VertiCare_AI_BCSE497J_Project_I_Presentation.pptx"
    ]
    for c in candidates:
        if os.path.exists(c):
            return FileResponse(
                path=c,
                filename="VertiCare_AI_BCSE497J_Project_I_Presentation.pptx",
                media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
    raise HTTPException(status_code=404, detail="Project presentation PPTX not found")


# Mount versioned API routes (/api/v1 and /api)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.include_router(api_router, prefix="/api")
