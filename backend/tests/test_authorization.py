def test_unauthenticated_request_fails(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_invalid_token_fails(client):
    headers = {"Authorization": "Bearer invalid.token.payload"}
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 401


def test_patient_role_authorization(client):
    # Register patient
    reg = client.post("/api/auth/register/patient", json={
        "email": "auth.patient@test.com",
        "password": "Password123!",
        "first_name": "Pat",
        "last_name": "Test",
        "date_of_birth": "1994-04-12"
    })
    assert reg.status_code == 201

    token = client.post("/api/auth/login", json={
        "email": "auth.patient@test.com",
        "password": "Password123!"
    }).json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Patient can access patient-protected test endpoint
    res_patient = client.get("/api/auth/test-patient", headers=headers)
    assert res_patient.status_code == 200
    assert res_patient.json()["role"] == "PATIENT"

    # Patient CANNOT access doctor-protected test endpoint (403 Forbidden)
    res_doctor = client.get("/api/auth/test-doctor", headers=headers)
    assert res_doctor.status_code == 403
    assert "Doctor account" in res_doctor.json()["detail"]


def test_doctor_role_authorization(client):
    # Register doctor
    reg = client.post("/api/auth/register/doctor", json={
        "email": "auth.doctor@test.com",
        "password": "DoctorPassword123!",
        "first_name": "Doc",
        "last_name": "Test",
        "specialization": "Neurology",
        "license_identifier": "LIC-TEST-004"
    })
    assert reg.status_code == 201

    token = client.post("/api/auth/login", json={
        "email": "auth.doctor@test.com",
        "password": "DoctorPassword123!"
    }).json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Doctor can access doctor-protected test endpoint
    res_doctor = client.get("/api/auth/test-doctor", headers=headers)
    assert res_doctor.status_code == 200
    assert res_doctor.json()["role"] == "DOCTOR"

    # Doctor CANNOT access patient-protected test endpoint (403 Forbidden)
    res_patient = client.get("/api/auth/test-patient", headers=headers)
    assert res_patient.status_code == 403
    assert "Patient account" in res_patient.json()["detail"]

