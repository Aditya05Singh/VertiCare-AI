import pytest


def register_and_login_patient(client, email="patient.risk@verticare.org", password="Password123!"):
    reg_payload = {
        "email": email,
        "password": password,
        "first_name": "Risk",
        "last_name": "Patient",
        "date_of_birth": "1991-07-10",
        "gender": "FEMALE"
    }
    client.post("/api/auth/register/patient", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    return login_res.json()["access_token"]


def register_and_login_doctor(client, email="doctor.risk@verticare.org", password="DoctorPass123!"):
    reg_payload = {
        "email": email,
        "password": password,
        "first_name": "Doctor",
        "last_name": "Risk",
        "specialization": "Neurology",
        "license_identifier": f"LIC-{email.split('@')[0]}"
    }
    client.post("/api/auth/register/doctor", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    return login_res.json()["access_token"]


def test_risk_assessment_multimodal_success(client):
    token = register_and_login_patient(client, "pat.risk.full@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Log Daily Health Check
    client.post(
        "/api/health-checks",
        json={
            "check_date": "2026-08-31",
            "dizziness_severity": 7,
            "imbalance_severity": 6,
            "stress_level": 5,
            "sleep_hours": 6.5,
            "episode_duration": "minutes",
            "hydration_level": "moderate",
            "medication_adherence": "full",
            "nausea": True,
            "headache": False,
            "triggers": ["head_movement"]
        },
        headers=headers
    )

    # 2. Complete Questionnaire Session
    start_q = client.get("/api/questionnaire/start", headers=headers).json()
    q_sess_id = start_q["session_id"]
    client.post(f"/api/questionnaire/session/{q_sess_id}/answer", json={"question_code": "Q_SPINNING", "answer": True}, headers=headers)
    client.post(f"/api/questionnaire/session/{q_sess_id}/answer", json={"question_code": "Q_POSITIONAL", "answer": True}, headers=headers)
    client.post(f"/api/questionnaire/session/{q_sess_id}/answer", json={"question_code": "Q_EPISODE_DURATION_POS", "answer": "seconds"}, headers=headers)
    client.post(f"/api/questionnaire/session/{q_sess_id}/answer", json={"question_code": "Q_HEAD_TURNS", "answer": "right"}, headers=headers)
    client.post(f"/api/questionnaire/session/{q_sess_id}/answer", json={"question_code": "Q_ASSOCIATED_SYMPTOMS", "answer": ["nausea"]}, headers=headers)
    client.post(f"/api/questionnaire/session/{q_sess_id}/answer", json={"question_code": "Q_FUNCTIONAL_IMPACT", "answer": "moderate"}, headers=headers)

    # 3. Complete Eye Analysis Session
    eye_sess_id = client.post("/api/eye-analysis/sessions", headers=headers).json()["id"]
    client.post(
        f"/api/eye-analysis/sessions/{eye_sess_id}/features",
        json={
            "features": {
                "horizontal_amplitude": 0.065,
                "horizontal_velocity_mean": 0.35,
                "direction_changes_h": 6,
                "blink_rate_per_min": 18.0
            },
            "quality_summary": {
                "total_frames": 300,
                "valid_frames": 290,
                "valid_ratio": 0.96,
                "face_detected_ratio": 0.96,
                "is_sufficient": True
            }
        },
        headers=headers
    )

    # 4. Trigger Risk Assessment
    risk_res = client.post("/api/risk-assessment", json={}, headers=headers)
    assert risk_res.status_code == 200
    risk_data = risk_res.json()
    assert risk_data["id"] is not None
    assert risk_data["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert 0.0 <= risk_data["risk_score"] <= 1.0
    assert risk_data["model_version"] == "verticare-risk-v1"
    assert len(risk_data["contributing_factors"]) > 0
    assert "Not a medical diagnosis" in risk_data["notice"]


def test_risk_assessment_single_modality_health_check_only(client):
    token = register_and_login_patient(client, "pat.risk.single@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    # Only create a health check
    client.post(
        "/api/health-checks",
        json={
            "check_date": "2026-08-31",
            "dizziness_severity": 2,
            "imbalance_severity": 1,
            "stress_level": 2,
            "sleep_hours": 8.0,
            "episode_duration": "none",
            "hydration_level": "good",
            "medication_adherence": "full",
            "nausea": False,
            "headache": False,
            "triggers": []
        },
        headers=headers
    )

    risk_res = client.post("/api/risk-assessment", json={}, headers=headers)
    assert risk_res.status_code == 200
    assert risk_res.json()["risk_level"] in ("LOW", "MEDIUM", "HIGH")


def test_risk_assessment_insufficient_input_error(client):
    token = register_and_login_patient(client, "pat.risk.empty@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    # Brand new patient with zero records
    risk_res = client.post("/api/risk-assessment", json={}, headers=headers)
    assert risk_res.status_code == 400
    assert "Insufficient clinical input data" in risk_res.json()["detail"]


def test_risk_assessment_get_and_history(client):
    token = register_and_login_patient(client, "pat.risk.hist@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    # Log health check and create 2 assessments
    client.post(
        "/api/health-checks",
        json={
            "check_date": "2026-08-31",
            "dizziness_severity": 4,
            "imbalance_severity": 3,
            "stress_level": 3,
            "sleep_hours": 7.0,
            "episode_duration": "seconds",
            "hydration_level": "moderate",
            "medication_adherence": "full",
            "nausea": False,
            "headache": False,
            "triggers": []
        },
        headers=headers
    )

    r1 = client.post("/api/risk-assessment", json={}, headers=headers).json()
    r2 = client.post("/api/risk-assessment", json={}, headers=headers).json()

    # Get single assessment
    get_res = client.get(f"/api/risk-assessment/{r1['id']}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == r1["id"]

    # Get history list
    hist_res = client.get("/api/risk-assessment/history?limit=10", headers=headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert hist_data["total"] >= 2
    assert len(hist_data["items"]) >= 2
    assert hist_data["items"][0]["id"] == r2["id"]  # Newest first


def test_security_cross_patient_risk_idor_blocked(client):
    # Patient A creates assessment
    token_a = register_and_login_patient(client, "pat.a.risk@verticare.org")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    client.post(
        "/api/health-checks",
        json={
            "check_date": "2026-08-31",
            "dizziness_severity": 5,
            "imbalance_severity": 4,
            "stress_level": 4,
            "sleep_hours": 7.0,
            "episode_duration": "minutes",
            "hydration_level": "moderate",
            "medication_adherence": "full",
            "nausea": False,
            "headache": False,
            "triggers": []
        },
        headers=headers_a
    )
    assessment_id_a = client.post("/api/risk-assessment", json={}, headers=headers_a).json()["id"]

    # Patient B tries to access Patient A's assessment
    token_b = register_and_login_patient(client, "pat.b.risk@verticare.org")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    get_idor = client.get(f"/api/risk-assessment/{assessment_id_a}", headers=headers_b)
    assert get_idor.status_code == 404


def test_doctor_cannot_create_patient_risk_assessment(client):
    token_doc = register_and_login_doctor(client, "doctor.deny.risk@verticare.org")
    headers_doc = {"Authorization": f"Bearer {token_doc}"}

    res = client.post("/api/risk-assessment", json={}, headers=headers_doc)
    assert res.status_code == 403

