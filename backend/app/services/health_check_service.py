from datetime import date, datetime, timedelta, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from fastapi import HTTPException, status

from app.models.monitoring import DailyHealthCheck
from app.models.profile import PatientProfile
from app.schemas.monitoring import (
    DailyHealthCheckCreate,
    DailyHealthCheckResponse,
    DailyHealthCheckListResponse,
    DailyHealthTrendPoint,
    DailyHealthTrendResponse
)


class HealthCheckService:
    @staticmethod
    def create_or_update_health_check(
        db: Session,
        patient_id: str,
        data: DailyHealthCheckCreate
    ) -> DailyHealthCheck:
        """
        Record a daily health check for the authenticated patient.
        If a record already exists for the target date, updates it cleanly (one record per patient per day).
        """
        target_date = data.check_date or date.today()

        # Check for existing record on target_date
        existing = db.query(DailyHealthCheck).filter(
            DailyHealthCheck.patient_id == patient_id,
            DailyHealthCheck.check_date == target_date
        ).first()

        if existing:
            existing.dizziness_severity = data.dizziness_severity
            existing.episode_duration = data.episode_duration
            existing.imbalance_severity = data.imbalance_severity
            existing.nausea = data.nausea
            existing.headache = data.headache
            existing.sleep_hours = data.sleep_hours
            existing.hydration_level = data.hydration_level
            existing.stress_level = data.stress_level
            existing.medication_adherence = data.medication_adherence
            existing.triggers = data.triggers
            existing.notes = data.notes
            existing.updated_at = datetime.now(timezone.utc)
            record = existing
        else:
            record = DailyHealthCheck(
                patient_id=patient_id,
                check_date=target_date,
                dizziness_severity=data.dizziness_severity,
                episode_duration=data.episode_duration,
                imbalance_severity=data.imbalance_severity,
                nausea=data.nausea,
                headache=data.headache,
                sleep_hours=data.sleep_hours,
                hydration_level=data.hydration_level,
                stress_level=data.stress_level,
                medication_adherence=data.medication_adherence,
                triggers=data.triggers,
                notes=data.notes
            )
            db.add(record)

        try:
            db.commit()
            db.refresh(record)
            return record
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to record daily health check: {str(e)}"
            )

    @staticmethod
    def get_patient_history(
        db: Session,
        patient_id: str,
        limit: int = 30,
        offset: int = 0
    ) -> Tuple[List[DailyHealthCheck], int]:
        """Fetch historical health checks belonging to the authenticated patient, ordered newest first."""
        query = db.query(DailyHealthCheck).filter(
            DailyHealthCheck.patient_id == patient_id
        )
        total = query.count()
        items = query.order_by(desc(DailyHealthCheck.check_date)).offset(offset).limit(limit).all()
        return items, total

    @staticmethod
    def get_patient_health_check_by_id(
        db: Session,
        patient_id: str,
        health_check_id: str
    ) -> DailyHealthCheck:
        """
        Fetch a single health check by ID with strict ownership validation.
        Returns 404 if not found or belongs to another patient (prevents IDOR leaks).
        """
        record = db.query(DailyHealthCheck).filter(
            DailyHealthCheck.id == health_check_id,
            DailyHealthCheck.patient_id == patient_id
        ).first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health check record not found."
            )
        return record

    @staticmethod
    def get_patient_trends(
        db: Session,
        patient_id: str,
        days: int = 30
    ) -> DailyHealthTrendResponse:
        """
        Calculate longitudinal symptom and lifestyle trends for the authenticated patient.
        No ML or AI risk predictions are performed in this step.
        """
        cutoff_date = date.today() - timedelta(days=days)
        records = db.query(DailyHealthCheck).filter(
            DailyHealthCheck.patient_id == patient_id,
            DailyHealthCheck.check_date >= cutoff_date
        ).order_by(asc(DailyHealthCheck.check_date)).all()

        total = len(records)
        if total == 0:
            return DailyHealthTrendResponse(
                patient_id=patient_id,
                days_range=days,
                total_records=0,
                average_dizziness=0.0,
                average_imbalance=0.0,
                average_sleep=0.0,
                average_stress=0.0,
                data_points=[]
            )

        avg_diz = sum(r.dizziness_severity for r in records) / total
        avg_imb = sum(r.imbalance_severity for r in records) / total
        avg_slp = sum(r.sleep_hours for r in records) / total
        avg_str = sum(r.stress_level for r in records) / total

        points: List[DailyHealthTrendPoint] = [
            DailyHealthTrendPoint(
                date=r.check_date.isoformat(),
                dizziness_severity=r.dizziness_severity,
                imbalance_severity=r.imbalance_severity,
                sleep_hours=r.sleep_hours,
                stress_level=r.stress_level,
                hydration_level=r.hydration_level,
                nausea=r.nausea,
                headache=r.headache,
                episode_duration=r.episode_duration
            )
            for r in records
        ]

        return DailyHealthTrendResponse(
            patient_id=patient_id,
            days_range=days,
            total_records=total,
            average_dizziness=round(avg_diz, 1),
            average_imbalance=round(avg_imb, 1),
            average_sleep=round(avg_slp, 1),
            average_stress=round(avg_str, 1),
            data_points=points
        )

