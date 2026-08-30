import pytest
from app.models.profile import DoctorPatient, PatientProfile, DoctorProfile
from app.models.user import User


def register_and_login_doctor(client, email="doctor.primary@verticare.org", password="DoctorPass123!"):
    reg_payload = {
        "email": email,
        "password": password,
        "first_name": "Marcus",
        "last_name": "Welby",
        "specialization": "Neurotology",
        "license_identifier": f"LIC-{email.split('@')[0]}"
    }
    client.post("/api/auth/register/doctor", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    return login_res.json()["access_token"]


def register_and_login_patient(client, email="patient.one@verticare.org", password="Password123!"):
    reg_payload = {
        "email": email,
        "password": password,
        "first_name": "Alice",
        "last_name": "Smith",
        "date_of_birth": "1988-04-12",
        "gender": "FEMALE"
    }
    client.post("/api/auth/register/patient", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    return login_res.json()["access_token"]


def assign_patient_to_doctor(db_session, doctor_email: str, patient_email: str):
    doc_user = db_session.query(User).filter(User.email == doctor_email).first()
    pat_user = db_session.query(User).filter(User.email == patient_email).first()

    assignment = DoctorPatient(
        doctor_id=doc_user.doctor_profile.id,
        patient_id=pat_user.patient_profile.id
    )
    db_session.add(assignment)
    db_session.commit()
    return pat_user.patient_profile.id, doc_user.doctor_profile.id


def test_doctor_dashboard_and_assigned_patient_flow(client, db_session):
    doc_token = register_and_login_doctor(client, "dr.lead@verticare.org")
    pat_token = register_and_login_patient(client, "pat.lead@verticare.org")

    pat_id, doc_id = assign_patient_to_doctor(db_session, "dr.lead@verticare.org", "pat.lead@verticare.org")

    doc_headers = {"Authorization": f"Bearer {doc_token}"}
    pat_headers = {"Authorization": f"Bearer {pat_token}"}

    # 1. Patient logs Health Check
    client.post(
        "/api/health-checks",
        json={
            "check_date": "2026-08-31",
            "dizziness_severity": 6,
            "imbalance_severity": 5,
            "stress_level": 4,
            "sleep_hours": 7.5,
            "episode_duration": "minutes",
            "hydration_level": "good",
            "medication_adherence": "full",
            "nausea": True,
            "headache": False,
            "triggers": ["stress"]
        },
        headers=pat_headers
    )

    # 2. Patient computes Risk Assessment
    client.post("/api/risk-assessment", json={}, headers=pat_headers)

    # 3. Doctor views Dashboard
    dash_res = client.get("/api/doctor/dashboard", headers=doc_headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["total_assigned_patients"] == 1
    assert len(dash_data["recent_activity"]) >= 1

    # 4. Doctor views Patients List
    list_res = client.get("/api/doctor/patients", headers=doc_headers)
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] == 1
    assert list_data["items"][0]["patient_id"] == pat_id
    assert list_data["items"][0]["latest_risk_level"] in ("LOW", "MEDIUM", "HIGH")

    # 5. Doctor views Patient Dossier
    dossier_res = client.get(f"/api/doctor/patients/{pat_id}", headers=doc_headers)
    assert dossier_res.status_code == 200
    dossier = dossier_res.json()
    assert dossier["patient_id"] == pat_id
    assert dossier["latest_health_check"] is not None

    # 6. Doctor views Health History & Trends
    health_res = client.get(f"/api/doctor/patients/{pat_id}/health", headers=doc_headers)
    assert health_res.status_code == 200
    assert health_res.json()["total"] == 1

    trends_res = client.get(f"/api/doctor/patients/{pat_id}/health/trends?days=14", headers=doc_headers)
    assert trends_res.status_code == 200
    assert trends_res.json()["total_records"] == 1

    # 7. Doctor views Risk History
    risk_res = client.get(f"/api/doctor/patients/{pat_id}/risk", headers=doc_headers)
    assert risk_res.status_code == 200
    assert risk_res.json()["total"] >= 1

    # 8. Doctor views Report Summary
    report_res = client.get(f"/api/doctor/patients/{pat_id}/reports", headers=doc_headers)
    assert report_res.status_code == 200
    report = report_res.json()
    assert report["patient_id"] == pat_id
    assert "not a medical diagnosis" in report["disclaimer"]


def test_doctor_clinical_notes_lifecycle(client, db_session):
    doc_token_a = register_and_login_doctor(client, "dr.notes.a@verticare.org")
    doc_token_b = register_and_login_doctor(client, "dr.notes.b@verticare.org")
    pat_token = register_and_login_patient(client, "pat.notes@verticare.org")

    pat_id, doc_id_a = assign_patient_to_doctor(db_session, "dr.notes.a@verticare.org", "pat.notes@verticare.org")
    # Also assign to doctor B for cross-note test
    doc_b_user = db_session.query(User).filter(User.email == "dr.notes.b@verticare.org").first()
    db_session.add(DoctorPatient(doctor_id=doc_b_user.doctor_profile.id, patient_id=pat_id))
    db_session.commit()

    headers_a = {"Authorization": f"Bearer {doc_token_a}"}
    headers_b = {"Authorization": f"Bearer {doc_token_b}"}

    # 1. Doctor A creates note
    create_res = client.post(
        f"/api/doctor/patients/{pat_id}/notes",
        json={
            "content": "Patient reports noticeable improvement after vestibular rehabilitation exercises.",
            "note_type": "ROUTINE_REVIEW",
            "is_shared_with_patient": True
        },
        headers=headers_a
    )
    assert create_res.status_code == 201
    note_data = create_res.json()
    note_id = note_data["id"]
    assert note_data["doctor_name"] is not None

    # 2. Doctor A views notes
    notes_list_res = client.get(f"/api/doctor/patients/{pat_id}/notes", headers=headers_a)
    assert notes_list_res.status_code == 200
    assert len(notes_list_res.json()) == 1

    # 3. Doctor A edits own note
    update_res = client.patch(
        f"/api/doctor/notes/{note_id}",
        json={"content": "Updated: Patient shows stable vestibular compensation."},
        headers=headers_a
    )
    assert update_res.status_code == 200
    assert "Updated: Patient shows" in update_res.json()["content"]

    # 4. Doctor B attempts to edit Doctor A's note -> Forbidden (403)
    update_b_res = client.patch(
        f"/api/doctor/notes/{note_id}",
        json={"content": "Doctor B tampering attempt."},
        headers=headers_b
    )
    assert update_b_res.status_code == 403

    # 5. Note validation: Content too short
    invalid_res = client.post(
        f"/api/doctor/patients/{pat_id}/notes",
        json={"content": "ab"},
        headers=headers_a
    )
    assert invalid_res.status_code == 422


def test_security_idor_unassigned_patient_access_rejected(client, db_session):
    doc_token = register_and_login_doctor(client, "dr.secure@verticare.org")
    pat_token = register_and_login_patient(client, "pat.unassigned@verticare.org")

    pat_user = db_session.query(User).filter(User.email == "pat.unassigned@verticare.org").first()
    unassigned_pat_id = pat_user.patient_profile.id

    headers = {"Authorization": f"Bearer {doc_token}"}

    # Doctor tries to access unassigned patient across all endpoints -> 404 (does NOT leak existence)
    assert client.get(f"/api/doctor/patients/{unassigned_pat_id}", headers=headers).status_code == 404
    assert client.get(f"/api/doctor/patients/{unassigned_pat_id}/health", headers=headers).status_code == 404
    assert client.get(f"/api/doctor/patients/{unassigned_pat_id}/health/trends", headers=headers).status_code == 404
    assert client.get(f"/api/doctor/patients/{unassigned_pat_id}/questionnaire", headers=headers).status_code == 404
    assert client.get(f"/api/doctor/patients/{unassigned_pat_id}/eye-analysis", headers=headers).status_code == 404
    assert client.get(f"/api/doctor/patients/{unassigned_pat_id}/risk", headers=headers).status_code == 404
    assert client.get(f"/api/doctor/patients/{unassigned_pat_id}/notes", headers=headers).status_code == 404
    assert client.post(f"/api/doctor/patients/{unassigned_pat_id}/notes", json={"content": "Test note"}, headers=headers).status_code == 404
    assert client.get(f"/api/doctor/patients/{unassigned_pat_id}/reports", headers=headers).status_code == 404


def test_security_role_protection_patient_and_unauth_blocked(client):
    pat_token = register_and_login_patient(client, "pat.attacker@verticare.org")
    pat_headers = {"Authorization": f"Bearer {pat_token}"}

    # Patient role attempts doctor endpoint -> 403 Forbidden
    assert client.get("/api/doctor/dashboard", headers=pat_headers).status_code == 403
    assert client.get("/api/doctor/patients", headers=pat_headers).status_code == 403

    # Unauthenticated request -> 401 Unauthorized
    assert client.get("/api/doctor/dashboard").status_code == 401
    assert client.get("/api/doctor/patients").status_code == 401

