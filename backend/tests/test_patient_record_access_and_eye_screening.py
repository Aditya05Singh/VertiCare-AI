import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.profile import PatientProfile, DoctorProfile, DoctorPatient
from app.services.eye_screening_engine import EyeScreeningEngine


def register_user(client: TestClient, role: str, email: str, identifier: str = ""):
    if role == "DOCTOR":
        reg = client.post(
            "/api/auth/register/doctor",
            json={
                "email": email,
                "password": "DoctorPassword123!",
                "first_name": "Marcus",
                "last_name": "Einthoven",
                "specialization": "Vestibular Neurology",
                "license_identifier": identifier or f"LIC-{email}"
            }
        )
    else:
        reg = client.post(
            "/api/auth/register/patient",
            json={
                "email": email,
                "password": "PatientPassword123!",
                "first_name": "Krishna",
                "last_name": "Gupta",
                "date_of_birth": "1990-07-20",
                "gender": "MALE",
                "emergency_contact_name": "Family",
                "emergency_contact_phone": "+1-555-0123"
            }
        )
    assert reg.status_code == 201
    user_info = reg.json()

    login = client.post(
        "/api/auth/login",
        json={"email": email, "password": "DoctorPassword123!" if role == "DOCTOR" else "PatientPassword123!"}
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return user_info, headers


def test_doctor_patient_record_access_flow_and_sub_endpoints(client: TestClient, db_session: Session):
    """
    Verifies that:
    1. Doctor assigned to patient can open patient record via PatientProfile.id.
    2. Doctor assigned to patient can open patient record via User.id.
    3. Doctor can access health, trends, questionnaire, eye-analysis, risk, notes, and report sub-endpoints.
    4. Data privacy is preserved (no password hashes or secrets exposed).
    """
    doc_info, doc_headers = register_user(client, "DOCTOR", "doc.rec.test@verticare.org", "LIC-REC-1")
    pat_info, pat_headers = register_user(client, "PATIENT", "pat.rec.test@verticare.org")

    pat_profile_id = pat_info["patient_profile_id"]
    pat_user_id = pat_info["id"]

    # 1. Doctor assigns patient
    assign_res = client.post("/api/assignments", headers=doc_headers, json={"patient_id": pat_profile_id})
    assert assign_res.status_code == 201

    # 2. Patient creates some records
    # 2a. Daily Health Check
    client.post(
        "/api/health-checks",
        headers=pat_headers,
        json={
            "check_date": "2026-08-31",
            "dizziness_severity": 4,
            "imbalance_severity": 3,
            "stress_level": 2,
            "sleep_hours": 8.0,
            "episode_duration": "minutes",
            "hydration_level": "good",
            "medication_adherence": "full",
            "nausea": False,
            "headache": False,
            "triggers": ["fatigue"]
        }
    )

    # 2b. Eye Analysis with Screening Features
    eye_start = client.post("/api/eye-analysis/sessions", headers=pat_headers).json()
    client.post(
        f"/api/eye-analysis/sessions/{eye_start['id']}/features",
        headers=pat_headers,
        json={
            "features": {
                "horizontal_amplitude": 0.032,
                "vertical_amplitude": 0.015,
                "horizontal_velocity_mean": 0.18,
                "vertical_velocity_mean": 0.07,
                "horizontal_velocity_max": 0.42,
                "vertical_velocity_max": 0.15,
                "direction_changes_h": 4,
                "direction_changes_v": 1,
                "blink_count": 3,
                "blink_rate_per_min": 18.0
            },
            "quality_summary": {
                "total_frames": 300,
                "valid_frames": 290,
                "valid_ratio": 0.967,
                "face_detected_ratio": 0.98,
                "is_sufficient": True
            }
        }
    )

    # 2c. Completed Questionnaire
    q_start = client.get("/api/questionnaire/start", headers=pat_headers).json()
    q_sess_id = q_start["session_id"]
    # Answer root question
    client.post(
        f"/api/questionnaire/sessions/{q_sess_id}/answer",
        headers=pat_headers,
        json={"question_code": "Q_SPINNING", "answer": True}
    )
    # Complete session
    client.post(f"/api/questionnaire/sessions/{q_sess_id}/complete", headers=pat_headers)

    # 3. Test Doctor Dossier Access via PatientProfile.id
    dossier_by_profile_id = client.get(f"/api/doctor/patients/{pat_profile_id}", headers=doc_headers)
    assert dossier_by_profile_id.status_code == 200
    data_p = dossier_by_profile_id.json()
    assert data_p["patient_id"] == pat_profile_id
    assert "Krishna Gupta" in data_p["full_name"]
    assert data_p["latest_health_check"] is not None
    assert data_p["latest_eye_analysis"] is not None
    assert data_p["latest_eye_analysis"]["screening"] is not None
    assert "NORMAL_FIXATION_PATTERN" in data_p["latest_eye_analysis"]["screening"]["label"]
    # Privacy check: No password or hash in response
    assert "password" not in str(data_p).lower()
    assert "hash" not in str(data_p).lower()

    # 4. Test Doctor Dossier Access via User.id
    dossier_by_user_id = client.get(f"/api/doctor/patients/{pat_user_id}", headers=doc_headers)
    assert dossier_by_user_id.status_code == 200
    assert dossier_by_user_id.json()["patient_id"] == pat_profile_id

    # 5. Test Doctor Accessing Sub-Endpoints via Profile ID and User ID
    for target_id in [pat_profile_id, pat_user_id]:
        # Health history
        h_res = client.get(f"/api/doctor/patients/{target_id}/health", headers=doc_headers)
        assert h_res.status_code == 200
        assert len(h_res.json()["items"]) >= 1

        # Health trends
        t_res = client.get(f"/api/doctor/patients/{target_id}/health/trends", headers=doc_headers)
        assert t_res.status_code == 200

        # Eye analysis history
        eye_res = client.get(f"/api/doctor/patients/{target_id}/eye-analysis", headers=doc_headers)
        assert eye_res.status_code == 200
        assert len(eye_res.json()) >= 1
        assert eye_res.json()[0]["screening"]["status"] == "AVAILABLE"

        # Questionnaire history
        q_res = client.get(f"/api/doctor/patients/{target_id}/questionnaire", headers=doc_headers)
        assert q_res.status_code == 200

        # Risk history
        r_res = client.get(f"/api/doctor/patients/{target_id}/risk", headers=doc_headers)
        assert r_res.status_code == 200

        # Reports summary
        rep_res = client.get(f"/api/doctor/patients/{target_id}/reports", headers=doc_headers)
        assert rep_res.status_code == 200


def test_security_idor_and_unauthorized_access_strictly_enforced(client: TestClient, db_session: Session):
    """
    Mandatory security test:
    - Doctor A assigned to Patient A.
    - Doctor B assigned to Patient B.
    - Doctor A trying to access Patient B is DENIED with 404 (preventing leakage).
    - Unauthenticated request is DENIED with 401.
    - Patient trying to access doctor endpoint is DENIED with 403.
    """
    doc_a_info, doc_a_headers = register_user(client, "DOCTOR", "doc.a@verticare.org", "LIC-A")
    doc_b_info, doc_b_headers = register_user(client, "DOCTOR", "doc.b@verticare.org", "LIC-B")
    pat_a_info, pat_a_headers = register_user(client, "PATIENT", "pat.a@verticare.org")
    pat_b_info, pat_b_headers = register_user(client, "PATIENT", "pat.b@verticare.org")

    # Assign Doctor A ↔ Patient A
    client.post("/api/assignments", headers=doc_a_headers, json={"patient_id": pat_a_info["patient_profile_id"]})
    # Assign Doctor B ↔ Patient B
    client.post("/api/assignments", headers=doc_b_headers, json={"patient_id": pat_b_info["patient_profile_id"]})

    # 1. Doctor A accessing Patient A -> 200
    res_aa = client.get(f"/api/doctor/patients/{pat_a_info['patient_profile_id']}", headers=doc_a_headers)
    assert res_aa.status_code == 200

    # 2. Doctor A accessing Patient B -> 404
    res_ab = client.get(f"/api/doctor/patients/{pat_b_info['patient_profile_id']}", headers=doc_a_headers)
    assert res_ab.status_code == 404
    assert "not assigned" in res_ab.json()["detail"].lower()

    # 3. Doctor A accessing arbitrary nonexistent ID -> 404
    res_bad = client.get("/api/doctor/patients/nonexistent-uuid-12345", headers=doc_a_headers)
    assert res_bad.status_code == 404

    # 4. Patient A trying to access Doctor patient-dossier endpoint -> 403
    res_pat = client.get(f"/api/doctor/patients/{pat_a_info['patient_profile_id']}", headers=pat_a_headers)
    assert res_pat.status_code == 403

    # 5. Unauthenticated request -> 401
    res_unauth = client.get(f"/api/doctor/patients/{pat_a_info['patient_profile_id']}")
    assert res_unauth.status_code == 401


def test_eye_screening_engine_patterns_and_disclaimers():
    """Unit tests for the evidence-based eye screening interpretation engine."""
    # 1. Normal Fixation Input
    normal_feats = {
        "horizontal_amplitude": 0.025,
        "vertical_amplitude": 0.015,
        "horizontal_velocity_mean": 0.15,
        "vertical_velocity_mean": 0.08,
        "horizontal_velocity_max": 0.35,
        "vertical_velocity_max": 0.16,
        "direction_changes_h": 4,
        "direction_changes_v": 2,
        "blink_count": 3,
        "blink_rate_per_min": 18.0,
    }
    good_quality = {"is_sufficient": True, "valid_ratio": 0.98, "total_frames": 300, "valid_frames": 294}
    res_norm = EyeScreeningEngine.interpret_screening(normal_feats, good_quality)
    assert res_norm.status == "AVAILABLE"
    assert "NORMAL_FIXATION_PATTERN" in res_norm.label
    assert res_norm.confidence is not None
    assert "Not a medical diagnosis" in res_norm.disclaimer
    assert "RGB webcam" in res_norm.domain_shift_notice

    # 2. Horizontal Nystagmus Pattern Input
    nystagmus_feats = {
        "horizontal_amplitude": 0.125,
        "vertical_amplitude": 0.020,
        "horizontal_velocity_mean": 0.62,
        "vertical_velocity_mean": 0.09,
        "horizontal_velocity_max": 1.45,
        "vertical_velocity_max": 0.20,
        "direction_changes_h": 18,
        "direction_changes_v": 2,
        "blink_count": 2,
        "blink_rate_per_min": 12.0,
    }
    res_nyst = EyeScreeningEngine.interpret_screening(nystagmus_feats, good_quality)
    assert res_nyst.status == "AVAILABLE"
    assert "HORIZONTAL_NYSTAGMUS" in res_nyst.label
    assert len(res_nyst.contributing_factors) >= 3

    # 3. Insufficient Quality Cutoff
    poor_quality = {"is_sufficient": False, "valid_ratio": 0.40, "total_frames": 300, "valid_frames": 120}
    res_poor = EyeScreeningEngine.interpret_screening(normal_feats, poor_quality)
    assert res_poor.status == "UNAVAILABLE"
    assert res_poor.confidence is None
    assert "insufficient" in res_poor.explanation.lower()

