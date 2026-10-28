import os
import io
import tempfile
import pytest
from cv.src.capture import SyntheticFrameGenerator


def register_and_login_patient(
    client,
    email="pat.integration@verticare.org",
    password="Password123!",
    dob="1992-06-15",
    gender="FEMALE"
):
    reg_payload = {
        "email": email,
        "password": password,
        "first_name": "Integration",
        "last_name": "Patient",
        "date_of_birth": dob,
        "gender": gender
    }
    client.post("/api/auth/register/patient", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    return login_res.json()["access_token"]


def register_and_login_doctor(
    client,
    email="doc.integration@verticare.org",
    password="DoctorPass123!"
):
    reg_payload = {
        "email": email,
        "password": password,
        "first_name": "Doctor",
        "last_name": "Integration",
        "specialization": "Neurotology",
        "license_identifier": f"LIC-{email.split('@')[0]}"
    }
    client.post("/api/auth/register/doctor", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    return login_res.json()["access_token"]


# ==============================================================================
# 1. Computer Vision Video Pipeline Integration Tests
# ==============================================================================

def test_video_screening_endpoint_valid_video(client):
    """Verifies that an uploaded video is processed end-to-end via /api/eye-analysis/video-screening."""
    token = register_and_login_patient(client, "pat.video.screening@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    # Generate a lightweight synthetic test video
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        video_path = tmp.name

    try:
        SyntheticFrameGenerator.create_synthetic_test_video(
            video_path,
            duration_sec=1.0,
            fps=25.0,
            freq_hz=2.0,
            width=320,
            height=240
        )

        with open(video_path, "rb") as vf:
            files = {"file": ("test_eye.mp4", vf, "video/mp4")}
            res = client.post(
                "/api/eye-analysis/video-screening?max_frames=30",
                files=files,
                headers=headers
            )

        assert res.status_code == 201
        data = res.json()
        assert data["id"] is not None
        assert data["analysis_status"] in ("COMPLETED", "INSUFFICIENT_QUALITY")
        assert len(data["features"]) > 0
        assert data["video_metadata"] is not None
        assert data["video_metadata"]["width"] == 320
        assert data["video_metadata"]["height"] == 240
        assert data["screening"] is not None
        assert "Not a medical diagnosis" in data["screening"]["disclaimer"]
        assert "consumer RGB webcam" in data["screening"]["domain_shift_notice"]

    finally:
        if os.path.exists(video_path):
            os.unlink(video_path)


def test_process_video_for_existing_session(client):
    """Verifies that /api/eye-analysis/sessions/{session_id}/video attaches video features to an existing session."""
    token = register_and_login_patient(client, "pat.video.session@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create session
    sess_res = client.post("/api/eye-analysis/sessions", headers=headers)
    assert sess_res.status_code == 201
    session_id = sess_res.json()["id"]

    # 2. Upload video
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        video_path = tmp.name

    try:
        SyntheticFrameGenerator.create_synthetic_test_video(
            video_path,
            duration_sec=1.0,
            fps=25.0,
            freq_hz=1.5,
            width=320,
            height=240
        )

        with open(video_path, "rb") as vf:
            files = {"file": ("vert_eye.mp4", vf, "video/mp4")}
            res = client.post(
                f"/api/eye-analysis/sessions/{session_id}/video?max_frames=25",
                files=files,
                headers=headers
            )

        assert res.status_code == 200
        data = res.json()
        assert data["id"] == session_id
        assert len(data["features"]) > 0
        assert data["video_metadata"]["fps"] == 25.0

    finally:
        if os.path.exists(video_path):
            os.unlink(video_path)


def test_video_screening_unsupported_format_rejected(client):
    """Verifies that non-video file formats (.txt) are rejected with 400 Bad Request."""
    token = register_and_login_patient(client, "pat.video.badfmt@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("notes.txt", io.BytesIO(b"Hello world invalid video"), "text/plain")}
    res = client.post("/api/eye-analysis/video-screening", files=files, headers=headers)
    assert res.status_code == 400
    assert "Unsupported video file format" in res.json()["detail"]


def test_video_screening_corrupted_file_rejected(client):
    """Verifies that corrupted video container headers are caught and rejected."""
    token = register_and_login_patient(client, "pat.video.corrupt@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    files = {"file": ("corrupt.mp4", io.BytesIO(b"\x00\x00\x00\x18ftypmp42corrupted_bytes_here"), "video/mp4")}
    res = client.post("/api/eye-analysis/video-screening", files=files, headers=headers)
    assert res.status_code == 400
    assert "Video processing failed" in res.json()["detail"]


def test_video_screening_idor_protection(client):
    """Verifies cross-patient isolation: Patient B cannot upload video to Patient A's session."""
    token_a = register_and_login_patient(client, "pat.a.video@verticare.org")
    token_b = register_and_login_patient(client, "pat.b.video@verticare.org")

    sess_res = client.post("/api/eye-analysis/sessions", headers={"Authorization": f"Bearer {token_a}"})
    assert sess_res.status_code == 201
    session_id_a = sess_res.json()["id"]

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        video_path = tmp.name

    try:
        SyntheticFrameGenerator.create_synthetic_test_video(
            video_path,
            duration_sec=0.5,
            fps=20.0,
            freq_hz=1.5,
            width=320,
            height=240
        )
        with open(video_path, "rb") as vf:
            files = {"file": ("test.mp4", vf, "video/mp4")}
            res = client.post(
                f"/api/eye-analysis/sessions/{session_id_a}/video",
                files=files,
                headers={"Authorization": f"Bearer {token_b}"}
            )
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()
    finally:
        if os.path.exists(video_path):
            os.unlink(video_path)


# ==============================================================================
# 2. General Symptom Engine & Risk Integration Tests
# ==============================================================================

def test_general_symptom_assessment_endpoint_explicit_input(client):
    """Verifies that /api/risk-assessment/general-symptoms executes inference with explicit symptoms."""
    token = register_and_login_patient(client, "pat.sym.explicit@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "fever": True,
        "cough": True,
        "fatigue": True,
        "difficulty_breathing": False,
        "age": 42,
        "gender": "Male",
        "blood_pressure": "High",
        "cholesterol_level": "Normal"
    }

    res = client.post("/api/risk-assessment/general-symptoms", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["assessment_type"] == "EXPERIMENTAL_GENERAL_SYMPTOM_ASSESSMENT"
    assert data["status"] == "COMPLETED"
    assert data["prediction"] in ("Positive", "Negative")
    assert 0.0 <= data["probability_positive"] <= 1.0
    assert data["confidence_tier"] in ("HIGH", "MODERATE", "LOW")
    assert len(data["relevant_limitations"]) >= 2
    assert "DOES NOT evaluate vertigo" in data["notice"]


def test_general_symptom_assessment_auto_populates_demographics(client):
    """Verifies that missing age/gender are automatically extracted from patient profile."""
    token = register_and_login_patient(
        client,
        email="pat.sym.auto@verticare.org",
        dob="1985-04-12",
        gender="FEMALE"
    )
    headers = {"Authorization": f"Bearer {token}"}

    # Only pass symptom flags, omit age and gender
    payload = {
        "fever": True,
        "cough": False,
        "fatigue": True,
        "difficulty_breathing": False
    }

    res = client.post("/api/risk-assessment/general-symptoms", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert data["prediction"] in ("Positive", "Negative")
    assert "fever" in [s.lower() for s in data["contributing_symptoms"]]


def test_general_symptom_assessment_role_protection(client):
    """Verifies that doctors cannot invoke patient general-symptoms assessment directly."""
    doc_token = register_and_login_doctor(client, "doc.sym.role@verticare.org")
    headers = {"Authorization": f"Bearer {doc_token}"}

    res = client.post(
        "/api/risk-assessment/general-symptoms",
        json={"fever": True},
        headers=headers
    )
    assert res.status_code == 403


# ==============================================================================
# 3. Multimodal Fusion Integration (Video CV + Health Check -> Risk Assessment)
# ==============================================================================

def test_multimodal_risk_assessment_with_video_features(client):
    """
    End-to-end multimodal flow:
    1. Patient records daily health check.
    2. Patient uploads eye video for automated screening.
    3. Patient requests composite risk assessment fusing both modalities.
    """
    token = register_and_login_patient(client, "pat.fusion.e2e@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Health check
    hc_res = client.post(
        "/api/health-checks",
        json={
            "check_date": "2026-10-12",
            "dizziness_severity": 7,
            "imbalance_severity": 6,
            "stress_level": 5,
            "sleep_hours": 6.0,
            "episode_duration": "minutes",
            "hydration_level": "moderate",
            "medication_adherence": "full",
            "nausea": True,
            "headache": True,
            "triggers": ["head_turn"]
        },
        headers=headers
    )
    assert hc_res.status_code == 201
    hc_id = hc_res.json()["id"]

    # 2. Video screening
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        video_path = tmp.name

    try:
        SyntheticFrameGenerator.create_synthetic_test_video(
            video_path,
            duration_sec=1.0,
            fps=25.0,
            freq_hz=2.0,
            width=320,
            height=240
        )

        with open(video_path, "rb") as vf:
            files = {"file": ("fusion_eye.mp4", vf, "video/mp4")}
            video_res = client.post(
                "/api/eye-analysis/video-screening?max_frames=25",
                files=files,
                headers=headers
            )
        assert video_res.status_code == 201
        eye_session_id = video_res.json()["id"]

        # 3. Compute Risk Assessment fusing both modalities
        risk_res = client.post(
            "/api/risk-assessment",
            json={
                "health_check_id": hc_id,
                "eye_analysis_session_id": eye_session_id
            },
            headers=headers
        )
        assert risk_res.status_code == 200
        risk_data = risk_res.json()

        assert risk_data["patient_id"] is not None
        assert risk_data["health_check_id"] == hc_id
        assert risk_data["eye_analysis_session_id"] == eye_session_id
        assert risk_data["risk_level"] in ("LOW", "MEDIUM", "HIGH")
        assert 0.0 <= risk_data["risk_score"] <= 100.0
        assert len(risk_data["contributing_factors"]) > 0

    finally:
        if os.path.exists(video_path):
            os.unlink(video_path)


def test_sample_video_screening_endpoint_and_calibrated_confidence(client):
    """Verifies that /api/eye-analysis/sample-video-screening runs CV pipeline and returns calibrated probability."""
    token = register_and_login_patient(client, "pat.sample.screen@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Test normal fixation pattern
    res_norm = client.post(
        "/api/eye-analysis/sample-video-screening?pattern=normal",
        headers=headers
    )
    assert res_norm.status_code == 201
    data_norm = res_norm.json()
    assert data_norm["screening"]["status"] == "AVAILABLE"
    assert "NORMAL_FIXATION_PATTERN" in data_norm["screening"]["label"]
    # Normal person calibrated probability is around 20-30%
    assert 0.20 <= data_norm["screening"]["confidence"] <= 0.30

    # 2. Test horizontal nystagmus pattern
    res_horiz = client.post(
        "/api/eye-analysis/sample-video-screening?pattern=horizontal_nystagmus",
        headers=headers
    )
    assert res_horiz.status_code == 201
    data_horiz = res_horiz.json()
    assert data_horiz["screening"]["status"] == "AVAILABLE"
    assert "HORIZONTAL_NYSTAGMUS" in data_horiz["screening"]["label"]
    # Dancing / moving eyes calibrated probability is around 60-70%
    assert 0.60 <= data_horiz["screening"]["confidence"] <= 0.70
    assert data_horiz["screening"]["nystagmus_analysis"] is not None
    assert data_horiz["screening"]["nystagmus_analysis"]["dominant_frequency_hz"] > 0.0
