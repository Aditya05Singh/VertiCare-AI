import pytest


def register_and_login_patient(client, email="patient.eye@verticare.org", password="Password123!"):
    reg_payload = {
        "email": email,
        "password": password,
        "first_name": "Vision",
        "last_name": "Patient",
        "date_of_birth": "1993-03-22",
        "gender": "MALE"
    }
    client.post("/api/auth/register/patient", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    return login_res.json()["access_token"]


def register_and_login_doctor(client, email="doctor.eye@verticare.org", password="DoctorPass123!"):
    reg_payload = {
        "email": email,
        "password": password,
        "first_name": "Doctor",
        "last_name": "Vision",
        "specialization": "Neurotology",
        "license_identifier": f"LIC-{email.split('@')[0]}"
    }
    client.post("/api/auth/register/doctor", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    return login_res.json()["access_token"]


def test_create_eye_analysis_session_success(client):
    token = register_and_login_patient(client, "pat.eye.start@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/eye-analysis/sessions", headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["id"] is not None
    assert data["analysis_status"] == "RUNNING"
    assert "Not a medical diagnosis" in data["notice"]


def test_save_and_retrieve_eye_movement_features_and_screening_interpretation(client):
    token = register_and_login_patient(client, "pat.eye.save@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create session
    session_id = client.post("/api/eye-analysis/sessions", headers=headers).json()["id"]

    # 2. Submit features
    payload = {
        "features": {
            "horizontal_amplitude": 0.035,
            "vertical_amplitude": 0.018,
            "horizontal_velocity_mean": 0.22,
            "vertical_velocity_mean": 0.08,
            "horizontal_velocity_max": 0.55,
            "vertical_velocity_max": 0.18,
            "direction_changes_h": 4,
            "direction_changes_v": 1,
            "blink_count": 3,
            "blink_rate_per_min": 18.0
        },
        "quality_summary": {
            "total_frames": 300,
            "valid_frames": 285,
            "valid_ratio": 0.95,
            "face_detected_ratio": 0.95,
            "is_sufficient": True
        }
    }

    save_res = client.post(f"/api/eye-analysis/sessions/{session_id}/features", json=payload, headers=headers)
    assert save_res.status_code == 200
    saved_data = save_res.json()
    assert saved_data["analysis_status"] == "COMPLETED"
    assert len(saved_data["features"]) == 10

    # Verify evidence-based screening interpretation
    assert saved_data["screening"] is not None
    assert saved_data["screening"]["status"] == "AVAILABLE"
    assert "NORMAL_FIXATION_PATTERN" in saved_data["screening"]["label"]
    assert saved_data["screening"]["confidence"] is not None
    assert "Not a medical diagnosis" in saved_data["screening"]["disclaimer"]
    assert "consumer RGB webcam" in saved_data["screening"]["domain_shift_notice"]

    # 3. Retrieve session details
    get_res = client.get(f"/api/eye-analysis/sessions/{session_id}", headers=headers)
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["id"] == session_id
    assert retrieved["quality_summary"]["valid_ratio"] == 0.95
    assert retrieved["screening"]["status"] == "AVAILABLE"


def test_save_features_insufficient_quality_sets_screening_unavailable(client):
    token = register_and_login_patient(client, "pat.eye.poor@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    session_id = client.post("/api/eye-analysis/sessions", headers=headers).json()["id"]

    payload = {
        "features": {
            "horizontal_amplitude": 0.01,
            "vertical_amplitude": 0.01
        },
        "quality_summary": {
            "total_frames": 300,
            "valid_frames": 90,
            "valid_ratio": 0.30,
            "face_detected_ratio": 0.30,
            "is_sufficient": False
        }
    }

    save_res = client.post(f"/api/eye-analysis/sessions/{session_id}/features", json=payload, headers=headers)
    assert save_res.status_code == 200
    saved = save_res.json()
    assert saved["analysis_status"] == "INSUFFICIENT_QUALITY"
    assert saved["screening"]["status"] == "UNAVAILABLE"
    assert "insufficient" in saved["screening"]["explanation"].lower()


def test_save_features_rejects_unrecognized_feature(client):
    token = register_and_login_patient(client, "pat.eye.invalid@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    session_id = client.post("/api/eye-analysis/sessions", headers=headers).json()["id"]

    payload = {
        "features": {
            "unsupported_medical_diagnosis": 1.0  # Illegal key
        },
        "quality_summary": {
            "total_frames": 100,
            "valid_frames": 100,
            "valid_ratio": 1.0,
            "face_detected_ratio": 1.0,
            "is_sufficient": True
        }
    }

    res = client.post(f"/api/eye-analysis/sessions/{session_id}/features", json=payload, headers=headers)
    assert res.status_code == 422


def test_security_cross_patient_eye_session_idor_blocked(client):
    # Patient A creates session
    token_a = register_and_login_patient(client, "pat.a.vision@verticare.org")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    session_id_a = client.post("/api/eye-analysis/sessions", headers=headers_a).json()["id"]

    # Patient B tries to read Patient A's session
    token_b = register_and_login_patient(client, "pat.b.vision@verticare.org")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    get_idor = client.get(f"/api/eye-analysis/sessions/{session_id_a}", headers=headers_b)
    assert get_idor.status_code == 404

    # Patient B tries to submit features to Patient A's session
    post_idor = client.post(
        f"/api/eye-analysis/sessions/{session_id_a}/features",
        json={
            "features": {"horizontal_amplitude": 0.05},
            "quality_summary": {
                "total_frames": 50,
                "valid_frames": 50,
                "valid_ratio": 1.0,
                "face_detected_ratio": 1.0,
                "is_sufficient": True
            }
        },
        headers=headers_b
    )
    assert post_idor.status_code == 404


def test_doctor_cannot_create_patient_eye_analysis(client):
    token_doc = register_and_login_doctor(client, "doctor.deny.eye@verticare.org")
    headers_doc = {"Authorization": f"Bearer {token_doc}"}

    res = client.post("/api/eye-analysis/sessions", headers=headers_doc)
    assert res.status_code == 403
