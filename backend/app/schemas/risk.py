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


class GeneralSymptomAssessmentRequest(BaseSchema):
    fever: Optional[bool] = Field(None, description="Presence of fever (True/False)")
    cough: Optional[bool] = Field(None, description="Presence of cough (True/False)")
    fatigue: Optional[bool] = Field(None, description="Presence of systemic fatigue (True/False)")
    difficulty_breathing: Optional[bool] = Field(None, description="Presence of difficulty breathing (True/False)")
    age: Optional[int] = Field(None, ge=0, le=120, description="Patient age in years (auto-derived from profile if omitted)")
    gender: Optional[str] = Field(None, description="'Male' or 'Female' (auto-derived from profile if omitted)")
    blood_pressure: Optional[str] = Field("Normal", description="'Normal', 'Elevated', or 'High'")
    cholesterol_level: Optional[str] = Field("Normal", description="'Normal' or 'High'")


class GeneralSymptomAssessmentResponse(BaseSchema):
    assessment_type: str = Field(
        "EXPERIMENTAL_GENERAL_SYMPTOM_ASSESSMENT",
        description="Assessment modality and target domain"
    )
    model_version: str = Field("1.0.0", description="Model version")
    status: str = Field("AVAILABLE", description="Inference status ('AVAILABLE', 'UNAVAILABLE')")
    prediction: Optional[str] = Field(None, description="Binary general illness indicator ('Positive', 'Negative')")
    probability_positive: Optional[float] = Field(None, description="Model probability for positive illness outcome")
    confidence_tier: str = Field("UNKNOWN", description="Confidence tier ('HIGH', 'MODERATE', 'LOW', 'UNKNOWN')")
    data_quality_warnings: List[str] = Field(default_factory=list, description="Input data quality warnings")
    insufficient_information: bool = Field(False, description="Whether input lacked minimal information")
    relevant_limitations: List[str] = Field(default_factory=list, description="Explicit clinical boundary limitations")
    contributing_symptoms: List[str] = Field(default_factory=list, description="Key symptoms influencing assessment")
    notice: str = Field(
        "Experimental general-symptom pattern model trained on Kaggle benchmark data. "
        "DOES NOT evaluate vertigo, BPPV, vestibular hypofunction, or neurological balance disorders.",
        description="Non-vertigo disclaimer notice"
    )


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
    general_symptom_assessment: Optional[GeneralSymptomAssessmentResponse] = None
    created_at: datetime
    notice: str = "AI-assisted screening estimate for clinical decision support. Not a medical diagnosis."


class RiskAssessmentListResponse(BaseSchema):
    items: List[RiskAssessmentResponse]
    total: int
    limit: int
    offset: int

