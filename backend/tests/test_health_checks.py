from datetime import date, timedelta
import pytest
from app.models.monitoring import DailyHealthCheck


def register_and_login_patient(client, email="pat.test@verticare.org", password="Password123!"):
    reg_payload = {
        "email": email,
        "password": password,
        "first_name": "Test",
        "last_name": "Patient",
        "date_of_birth": "1990-01-01",
        "gender": "FEMALE"
    }
    reg_res = client.post("/api/auth/register/patient", json=reg_payload)
    assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    return login_res.json()["access_token"]


def register_and_login_doctor(client, email="doc.test@verticare.org", password="DoctorPass123!"):
    reg_payload = {
        "email": email,
        "password": password,
        "first_name": "Marcus",
        "last_name": "Doctor",
        "specialization": "Neurology",
        "license_identifier": f"LIC-{email.split('@')[0]}"
    }
    reg_res = client.post("/api/auth/register/doctor", json=reg_payload)
    assert reg_res.status_code == 201, f"Doctor reg failed: {reg_res.text}"
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert login_res.status_code == 200, f"Doctor login failed: {login_res.text}"
    return login_res.json()["access_token"]


def test_create_daily_health_check_success(client):
    token = register_and_login_patient(client, "patient1@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "check_date": str(date.today()),
        "dizziness_severity": 6,
        "episode_duration": "1-20 minutes",
        "imbalance_severity": 5,
        "nausea": True,
        "headache": False,
        "sleep_hours": 6.5,
        "hydration_level": "Moderate (1-2L)",
        "stress_level": 7,
        "medication_adherence": "Taken as prescribed",
        "triggers": ["Sudden head movement", "Fatigue"],
        "notes": "Felt unsteadiness when standing quickly in the morning."
    }

    res = client.post("/api/health-checks", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["dizziness_severity"] == 6
    assert data["imbalance_severity"] == 5
    assert data["nausea"] is True
    assert data["sleep_hours"] == 6.5
    assert "Sudden head movement" in data["triggers"]
    assert data["notes"] == "Felt unsteadiness when standing quickly in the morning."
    assert "patient_id" in data
    assert "id" in data


def test_duplicate_check_same_day_updates_existing(client):
    token = register_and_login_patient(client, "patient.dup@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    today_str = str(date.today())
    payload1 = {
        "check_date": today_str,
        "dizziness_severity": 3,
        "imbalance_severity": 2,
        "sleep_hours": 8.0,
        "stress_level": 3
    }
    res1 = client.post("/api/health-checks", json=payload1, headers=headers)
    assert res1.status_code == 201
    id1 = res1.json()["id"]

    # Post updated values for same day
    payload2 = {
        "check_date": today_str,
        "dizziness_severity": 7,
        "imbalance_severity": 6,
        "sleep_hours": 5.0,
        "stress_level": 8,
        "notes": "Condition worsened in afternoon."
    }
    res2 = client.post("/api/health-checks", json=payload2, headers=headers)
    assert res2.status_code == 201
    data2 = res2.json()
    assert data2["id"] == id1  # Same record updated
    assert data2["dizziness_severity"] == 7
    assert data2["notes"] == "Condition worsened in afternoon."

    # Verify history list contains only 1 entry for this patient
    history_res = client.get("/api/health-checks", headers=headers)
    assert history_res.status_code == 200
    assert history_res.json()["total"] == 1


def test_health_check_validation_rules(client):
    token = register_and_login_patient(client, "patient.val@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    # Invalid severity (>10)
    res_bad_severity = client.post("/api/health-checks", json={
        "dizziness_severity": 15,
        "imbalance_severity": 3,
        "sleep_hours": 7.0,
        "stress_level": 2
    }, headers=headers)
    assert res_bad_severity.status_code == 422

    # Invalid sleep hours (>24)
    res_bad_sleep = client.post("/api/health-checks", json={
        "dizziness_severity": 4,
        "imbalance_severity": 3,
        "sleep_hours": 28.0,
        "stress_level": 2
    }, headers=headers)
    assert res_bad_sleep.status_code == 422


def test_list_health_check_history_and_pagination(client):
    token = register_and_login_patient(client, "patient.history@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    # Create 3 records across 3 days
    for i in range(3):
        day = str(date.today() - timedelta(days=i))
        client.post("/api/health-checks", json={
            "check_date": day,
            "dizziness_severity": i + 2,
            "imbalance_severity": i + 1,
            "sleep_hours": 7.0,
            "stress_level": 4
        }, headers=headers)

    res = client.get("/api/health-checks?limit=2&offset=0", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    # Ensure newest is first
    assert data["items"][0]["check_date"] > data["items"][1]["check_date"]


def test_get_single_health_check_by_id(client):
    token = register_and_login_patient(client, "patient.single@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post("/api/health-checks", json={
        "dizziness_severity": 4,
        "imbalance_severity": 3,
        "sleep_hours": 7.5,
        "stress_level": 2
    }, headers=headers)
    record_id = create_res.json()["id"]

    get_res = client.get(f"/api/health-checks/{record_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == record_id


def test_get_trends_calculation(client):
    token = register_and_login_patient(client, "patient.trends@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    # Add 2 records
    client.post("/api/health-checks", json={
        "check_date": str(date.today() - timedelta(days=1)),
        "dizziness_severity": 4,
        "imbalance_severity": 2,
        "sleep_hours": 8.0,
        "stress_level": 4
    }, headers=headers)

    client.post("/api/health-checks", json={
        "check_date": str(date.today()),
        "dizziness_severity": 6,
        "imbalance_severity": 4,
        "sleep_hours": 6.0,
        "stress_level": 6
    }, headers=headers)

    trend_res = client.get("/api/health-checks/trends?days=7", headers=headers)
    assert trend_res.status_code == 200
    trends = trend_res.json()
    assert trends["total_records"] == 2
    assert trends["average_dizziness"] == 5.0  # (4 + 6) / 2
    assert trends["average_imbalance"] == 3.0  # (2 + 4) / 2
    assert trends["average_sleep"] == 7.0      # (8 + 6) / 2
    assert trends["average_stress"] == 5.0     # (4 + 6) / 2
    assert len(trends["data_points"]) == 2


def test_security_cross_patient_isolation_idor_blocked(client):
    # Patient A creates a record
    token_a = register_and_login_patient(client, "patient.a@verticare.org")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    res_a = client.post("/api/health-checks", json={
        "dizziness_severity": 9,
        "imbalance_severity": 8,
        "sleep_hours": 4.0,
        "stress_level": 9,
        "notes": "Patient A private note"
    }, headers=headers_a)
    record_id_a = res_a.json()["id"]

    # Patient B tries to read Patient A's record by ID
    token_b = register_and_login_patient(client, "patient.b@verticare.org")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    res_idor = client.get(f"/api/health-checks/{record_id_a}", headers=headers_b)
    assert res_idor.status_code == 404  # 404 without leaking existence

    # Patient B's trends should not contain Patient A's data
    res_b_trends = client.get("/api/health-checks/trends", headers=headers_b)
    assert res_b_trends.status_code == 200
    assert res_b_trends.json()["total_records"] == 0


def test_security_doctor_cannot_create_patient_health_check(client):
    token_doc = register_and_login_doctor(client, "doctor.deny@verticare.org")
    headers_doc = {"Authorization": f"Bearer {token_doc}"}

    res = client.post("/api/health-checks", json={
        "dizziness_severity": 5,
        "imbalance_severity": 5,
        "sleep_hours": 7.0,
        "stress_level": 5
    }, headers=headers_doc)
    # Doctor is denied access to patient health check creation
    assert res.status_code == 403

