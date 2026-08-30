from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.risk import (
    RiskCategory,
    Recommendation,
    RecommendationCategory,
    RecommendationUrgency,
)


class RecommendationService:
    """
    Generates safe, non-prescriptive supportive lifestyle, environmental, and clinician consultation recommendations.
    CRITICAL MEDICAL INVARIANT: Never prescribes medications, alters dosages, or claims clinical diagnosis.
    """

    @staticmethod
    def generate_recommendations_for_assessment(
        db: Session,
        risk_assessment_id: str,
        risk_category: RiskCategory,
        contributing_factors: List[Dict[str, Any]],
        has_red_flags: bool = False
    ) -> List[Recommendation]:
        """Generate tailored supportive guidelines aligned with observed risk tier."""
        recs: List[Recommendation] = []

        if has_red_flags or risk_category == RiskCategory.HIGH:
            # High Risk / Red Flag Escalation
            recs.append(
                Recommendation(
                    risk_assessment_id=risk_assessment_id,
                    category=RecommendationCategory.IMMEDIATE_ESCALATION,
                    title="Urgent Medical Evaluation Required",
                    description=(
                        "Observed features include elevated instability or reported focal neurological red flags. "
                        "Do not drive or operate machinery. Seek prompt clinical evaluation at the nearest emergency department or contact your neurologist/physician immediately."
                    ),
                    urgency=RecommendationUrgency.IMMEDIATE,
                    disclaimer_text="Non-diagnostic safety advisory. Emergency symptoms require direct physical clinical assessment."
                )
            )
            recs.append(
                Recommendation(
                    risk_assessment_id=risk_assessment_id,
                    category=RecommendationCategory.SAFETY_ALERT,
                    title="Fall Prevention & Environmental Safety",
                    description=(
                        "Keep walkways well-lit and free of obstacles. Remain seated or supported if feeling off-balance. "
                        "Avoid sudden head turns or unassisted rapid standing."
                    ),
                    urgency=RecommendationUrgency.IMMEDIATE,
                    disclaimer_text="Supportive guidance for daily safety only."
                )
            )

        elif risk_category == RiskCategory.MEDIUM:
            # Medium Risk / Moderate Instability
            recs.append(
                Recommendation(
                    risk_assessment_id=risk_assessment_id,
                    category=RecommendationCategory.CLINICIAN_FOLLOW_UP,
                    title="Schedule Specialist Vestibular Evaluation",
                    description=(
                        "Moderate vertigo symptoms or noticeable gaze instability detected. "
                        "Consult an ENT / Otolaryngologist or Neurologist for comprehensive vestibular examination (e.g. Dix-Hallpike maneuver, audiometry, or videonystagmography)."
                    ),
                    urgency=RecommendationUrgency.SOON,
                    disclaimer_text="Screening output intended to assist your physician during consultation."
                )
            )
            recs.append(
                Recommendation(
                    risk_assessment_id=risk_assessment_id,
                    category=RecommendationCategory.LIFESTYLE_HYGIENE,
                    title="Postural Transition & Vestibular Hygiene",
                    description=(
                        "Allow 15-30 seconds when transitioning from lying to sitting, and from sitting to standing. "
                        "Maintain adequate hydration (2L/day unless fluid-restricted) and aim for regular, uninterrupted sleep to support vestibular compensation."
                    ),
                    urgency=RecommendationUrgency.ROUTINE,
                    disclaimer_text="General lifestyle recommendations. Not medical advice."
                )
            )

        else:
            # Low Risk / Baseline Stability
            recs.append(
                Recommendation(
                    risk_assessment_id=risk_assessment_id,
                    category=RecommendationCategory.LIFESTYLE_HYGIENE,
                    title="Continue Regular Daily Tracking & Hydration",
                    description=(
                        "Current metrics reflect stable gaze fixation and mild symptom ratings. "
                        "Continue logging daily check-ins to establish your baseline and discuss longitudinal trends during routine clinic visits."
                    ),
                    urgency=RecommendationUrgency.ROUTINE,
                    disclaimer_text="General supportive wellness tracking."
                )
            )
            recs.append(
                Recommendation(
                    risk_assessment_id=risk_assessment_id,
                    category=RecommendationCategory.SAFETY_ALERT,
                    title="Observe for Symptom Fluctuations",
                    description=(
                        "If you experience sudden hearing changes, new severe headache, or difficulty speaking, perform a new check-in and consult a clinician promptly."
                    ),
                    urgency=RecommendationUrgency.ROUTINE,
                    disclaimer_text="Standard observational precautions."
                )
            )

        for r in recs:
            db.add(r)
        db.commit()
        return recs
