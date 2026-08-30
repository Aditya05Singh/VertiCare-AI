from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "verticare-backend"


@router.get("/health", response_model=HealthResponse)
def health_check():
    """System health check endpoint."""
    return HealthResponse(
        status="ok",
        service="verticare-backend"
    )

