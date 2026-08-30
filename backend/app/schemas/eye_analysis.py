import math
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models.eye_analysis import EyeAnalysisStatus
from cv.src.validation import ALLOWED_CV_FEATURE_NAMES, is_finite_number


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class QualitySummarySchema(BaseSchema):
    total_frames: int = Field(..., ge=0)
    valid_frames: int = Field(..., ge=0)
    valid_ratio: float = Field(..., ge=0.0, le=1.0)
    face_detected_ratio: float = Field(..., ge=0.0, le=1.0)
    is_sufficient: bool


class EyeMovementFeaturesSubmitRequest(BaseSchema):
    features: Dict[str, float] = Field(..., description="Dictionary of named finite numerical features")
    quality_summary: QualitySummarySchema

    @field_validator("features")
    @classmethod
    def validate_features_payload(cls, v: Dict[str, float]) -> Dict[str, float]:
        if not v:
            raise ValueError("Features payload cannot be empty.")
        if len(v) > 50:
            raise ValueError("Features payload exceeds maximum size limit (50).")

        cleaned = {}
        for key, val in v.items():
            if key not in ALLOWED_CV_FEATURE_NAMES:
                raise ValueError(f"Unrecognized feature name '{key}'. Allowed: {sorted(list(ALLOWED_CV_FEATURE_NAMES))}")
            if not is_finite_number(val):
                raise ValueError(f"Feature '{key}' must be a finite numerical value (got '{val}').")
            cleaned[key] = float(val)
        return cleaned


class EyeFeatureItem(BaseSchema):
    id: str
    feature_name: str
    feature_value: float
    created_at: datetime


class EyeScreeningInterpretationResponse(BaseSchema):
    status: str = Field("AVAILABLE", description="'AVAILABLE' or 'UNAVAILABLE'")
    label: str = Field("NORMAL_FIXATION_PATTERN", description="Screening pattern classification")
    confidence: Optional[float] = Field(None, description="Calibrated model probability (0.0 to 1.0)")
    model_name: str = Field("verticare-eye-screening-xgboost", description="Screening model name")
    model_version: str = Field("1.0.0", description="Model version identifier")
    explanation: str = Field("", description="Evidence-based rationale for the observed pattern")
    contributing_factors: List[str] = Field(default_factory=list, description="Key kinematic features influencing the screening output")
    disclaimer: str = Field(
        "AI-assisted screening observation. Not a medical diagnosis. "
        "Clinical interpretation should be performed by a qualified healthcare professional.",
        description="Mandatory clinical disclaimer"
    )
    domain_shift_notice: str = Field(
        "Captured via consumer RGB webcam under visible lighting. "
        "Does not replace infrared video-oculography (VNG/VOG) in darkness.",
        description="Webcam vs Infrared VOG hardware domain-shift notice"
    )


class EyeAnalysisSessionResponse(BaseSchema):
    id: str
    patient_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    analysis_status: EyeAnalysisStatus
    quality_summary: Dict[str, Any] = {}
    features: List[EyeFeatureItem] = []
    screening: Optional[EyeScreeningInterpretationResponse] = None
    created_at: datetime
    notice: str = "Computer-vision eye-movement feature extraction for clinical screening support. Not a medical diagnosis."
