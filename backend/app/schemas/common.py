from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, ConfigDict
from app.config import settings

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class StandardResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    disclaimer: str = settings.MEDICAL_DISCLAIMER


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    disclaimer: str = settings.MEDICAL_DISCLAIMER
