from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from app.models.questionnaire import QuestionType, SessionStatus


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class QuestionOption(BaseSchema):
    value: str
    label: str


class QuestionResponse(BaseSchema):
    id: str
    question_code: str
    version: str
    category: str
    question_type: QuestionType
    question_text: str
    options: List[QuestionOption] = []
    display_order: int


class AnswerSubmitRequest(BaseSchema):
    question_code: str = Field(..., min_length=1, max_length=50)
    answer: Any = Field(..., description="Value matching the question's type specification")


class SessionProgress(BaseSchema):
    answered_count: int
    estimated_total: int
    current_step: int


class SessionResponse(BaseSchema):
    session_id: str
    status: SessionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    current_question: Optional[QuestionResponse] = None
    progress: SessionProgress
    message: Optional[str] = None


class AnswerSummaryItem(BaseSchema):
    question_code: str
    question_text: str
    category: str = "general"
    question_type: QuestionType = QuestionType.TEXT
    answer: Any
    answered_at: datetime


class SessionSummaryResponse(BaseSchema):
    session_id: str
    patient_id: str
    status: SessionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_questions_answered: int
    answers: List[AnswerSummaryItem]
    notice: str = "This questionnaire is an academic screening prototype and does not represent a medical diagnosis or clinical prescription."
