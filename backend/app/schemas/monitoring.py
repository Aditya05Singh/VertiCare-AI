from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DailyHealthCheckCreate(BaseSchema):
    check_date: Optional[date] = Field(None, description="Check-in date (defaults to today)")
    dizziness_severity: int = Field(..., ge=0, le=10, description="Dizziness severity 0 (none) to 10 (worst)")
    episode_duration: str = Field(
        "None / Subsided",
        description="Duration of vertigo or dizzy episodes"
    )
    imbalance_severity: int = Field(..., ge=0, le=10, description="Imbalance / unsteadiness 0 to 10")
    nausea: bool = Field(False, description="Presence of nausea or autonomic distress")
    headache: bool = Field(False, description="Presence of headache or migraine")
    sleep_hours: float = Field(..., ge=0.0, le=24.0, description="Hours of sleep in past 24 hours")
    hydration_level: str = Field("Moderate (1-2L)", description="Estimated daily water intake")
    stress_level: int = Field(..., ge=0, le=10, description="Subjective stress level 0 to 10")
    medication_adherence: str = Field("Taken as prescribed", description="Medication adherence status")
    triggers: List[str] = Field(default_factory=list, description="List of recognized situational triggers")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional personal notes")

    @field_validator("triggers")
    @classmethod
    def validate_triggers(cls, v: List[str]) -> List[str]:
        return [str(t).strip()[:100] for t in v if str(t).strip()]


class DailyHealthCheckResponse(BaseSchema):
    id: str
    patient_id: str
    check_date: date
    dizziness_severity: int
    episode_duration: str
    imbalance_severity: int
    nausea: bool
    headache: bool
    sleep_hours: float
    hydration_level: str
    stress_level: int
    medication_adherence: str
    triggers: List[str]
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DailyHealthCheckListResponse(BaseSchema):
    items: List[DailyHealthCheckResponse]
    total: int
    limit: int
    offset: int


class DailyHealthTrendPoint(BaseSchema):
    date: str
    dizziness_severity: int
    imbalance_severity: int
    sleep_hours: float
    stress_level: int
    hydration_level: str
    nausea: bool
    headache: bool
    episode_duration: str


class DailyHealthTrendResponse(BaseSchema):
    patient_id: str
    days_range: int
    total_records: int
    average_dizziness: float
    average_imbalance: float
    average_sleep: float
    average_stress: float
    data_points: List[DailyHealthTrendPoint]
