from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.models.risk import RiskLevel


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RiskAssessmentCreateRequest(BaseSchema):
    health_check_id: Optional[str] = None
    questionnaire_session_id: Optional[str] = None
    eye_analysis_session_id: Optional[str] = None


class RiskAssessmentResponse(BaseSchema):
    id: str
    patient_id: str
    health_check_id: Optional[str] = None
    questionnaire_session_id: Optional[str] = None
    eye_analysis_session_id: Optional[str] = None
    risk_score: float
    risk_level: RiskLevel
    model_name: str
    model_version: str
    contributing_factors: List[str] = []
    created_at: datetime
    notice: str = "AI-assisted screening estimate for clinical decision support. Not a medical diagnosis."


class RiskAssessmentListResponse(BaseSchema):
    items: List[RiskAssessmentResponse]
    total: int
    limit: int
    offset: int
