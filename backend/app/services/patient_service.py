from datetime import date, datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.profile import PatientProfile
from app.models.monitoring import DailyHealthCheck
from app.schemas.monitoring import DailyHealthCheckCreate, DailyHealthCheckResponse, SymptomTrendsResponse
from app.core.exceptions import ResourceNotFoundException, ConflictException


class PatientService:
    @staticmethod
    def record_daily_check_in(
        db: Session,
        patient_id: str,
        data: DailyHealthCheckCreate
    ) -> DailyHealthCheck:
        """Create or update a patient's daily health check-in."""
        target_date = data.check_in_date or date.today()

        # Check if record already exists for today
        existing = db.query(DailyHealthCheck).filter(
            DailyHealthCheck.patient_id == patient_id,
            DailyHealthCheck.check_in_date == target_date
        ).first()

        if existing:
            # Update existing record
            existing.dizziness_severity = data.dizziness_severity
            existing.nausea_severity = data.nausea_severity
            existing.headache_severity = data.headache_severity
            existing.unsteadiness_severity = data.unsteadiness_severity
            existing.sleep_hours = data.sleep_hours
            existing.water_intake_liters = data.water_intake_liters
            existing.stress_level = data.stress_level
            existing.medications_taken_today = data.medications_taken_today
            existing.medication_notes = data.medication_notes
            existing.triggers_identified = data.triggers_identified
            existing.patient_notes = data.patient_notes
            check_in = existing
        else:
            check_in = DailyHealthCheck(
                patient_id=patient_id,
                check_in_date=target_date,
                dizziness_severity=data.dizziness_severity,
                nausea_severity=data.nausea_severity,
                headache_severity=data.headache_severity,
                unsteadiness_severity=data.unsteadiness_severity,
                sleep_hours=data.sleep_hours,
                water_intake_liters=data.water_intake_liters,
                stress_level=data.stress_level,
                medications_taken_today=data.medications_taken_today,
                medication_notes=data.medication_notes,
                triggers_identified=data.triggers_identified,
                patient_notes=data.patient_notes
            )
            db.add(check_in)

        db.commit()
        db.refresh(check_in)
        return check_in

    @staticmethod
    def get_patient_check_ins(
        db: Session,
        patient_id: str,
        limit: int = 30
    ) -> List[DailyHealthCheck]:
        """Fetch historical health check-ins ordered by date descending."""
        return db.query(DailyHealthCheck).filter(
            DailyHealthCheck.patient_id == patient_id
        ).order_by(desc(DailyHealthCheck.check_in_date)).limit(limit).all()

    @staticmethod
    def get_symptom_trends(db: Session, patient_id: str) -> SymptomTrendsResponse:
        """Calculate 7-day and 30-day symptom averages and adherence."""
        records = db.query(DailyHealthCheck).filter(
            DailyHealthCheck.patient_id == patient_id
        ).order_by(desc(DailyHealthCheck.check_in_date)).limit(30).all()

        total = len(records)
        if not records:
            return SymptomTrendsResponse(
                total_check_ins=0,
                average_dizziness_7d=0.0,
                average_nausea_7d=0.0,
                average_unsteadiness_7d=0.0,
                average_sleep_7d=8.0,
                adherence_rate_pct=0.0,
                recent_history=[]
            )

        last_7 = records[:7]
        avg_diz = sum(r.dizziness_severity for r in last_7) / len(last_7)
        avg_nau = sum(r.nausea_severity for r in last_7) / len(last_7)
        avg_unst = sum(r.unsteadiness_severity for r in last_7) / len(last_7)
        avg_slp = sum(r.sleep_hours for r in last_7) / len(last_7)
        adherence = (sum(1 for r in last_7 if r.medications_taken_today) / len(last_7)) * 100.0

        history_dtos = [
            DailyHealthCheckResponse.model_validate(r) for r in records
        ]

        return SymptomTrendsResponse(
            total_check_ins=total,
            average_dizziness_7d=round(avg_diz, 1),
            average_nausea_7d=round(avg_nau, 1),
            average_unsteadiness_7d=round(avg_unst, 1),
            average_sleep_7d=round(avg_slp, 1),
            adherence_rate_pct=round(adherence, 1),
            recent_history=history_dtos
        )
