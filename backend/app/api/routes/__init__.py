from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health_checks import router as health_checks_router
from app.api.routes.questionnaire import router as questionnaire_router
from app.api.routes.eye_analysis import router as eye_analysis_router
from app.api.routes.risk_assessment import router as risk_assessment_router
from app.api.routes.doctor import router as doctor_router
from app.api.routes.emergency import router as emergency_router
from app.api.routes.assignment import router as assignment_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(health_checks_router)
api_router.include_router(questionnaire_router)
api_router.include_router(eye_analysis_router)
api_router.include_router(risk_assessment_router)
api_router.include_router(doctor_router)
api_router.include_router(emergency_router)
api_router.include_router(assignment_router)
