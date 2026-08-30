def test_patient_registration_success(client):
    payload = {
        "email": "patient.test@verticare.org",
        "password": "Password123!",
        "first_name": "Sarah",
        "last_name": "Connor",
        "date_of_birth": "1985-02-28",
        "gender": "FEMALE",
        "emergency_contact_name": "John Connor",
        "emergency_contact_phone": "+1-555-0199",
        "medical_history": "History of positional dizziness"
    }
    response = client.post("/api/auth/register/patient", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "patient.test@verticare.org"
    assert data["first_name"] == "Sarah"
    assert data["last_name"] == "Connor"
    assert data["role"] == "PATIENT"
    assert data["patient_profile_id"] is not None
    assert "password" not in data
    assert "password_hash" not in data


def test_doctor_registration_success(client):
    payload = {
        "email": "doctor.test@verticare.org",
        "password": "DoctorPass123!",
        "first_name": "Marcus",
        "last_name": "Welby",
        "specialization": "Neurotology",
        "license_identifier": "LIC-VERT-9921"
    }
    response = client.post("/api/auth/register/doctor", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "doctor.test@verticare.org"
    assert data["role"] == "DOCTOR"
    assert data["doctor_profile_id"] is not None
    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_email_registration_fails(client):
    payload = {
        "email": "duplicate@verticare.org",
        "password": "Password123!",
        "first_name": "First",
        "last_name": "User",
        "date_of_birth": "1990-01-01",
        "gender": "MALE"
    }
    res1 = client.post("/api/auth/register/patient", json=payload)
    assert res1.status_code == 201

    # Second registration with same email
    res2 = client.post("/api/auth/register/patient", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_registration_validation_short_password(client):
    payload = {
        "email": "short@verticare.org",
        "password": "short",  # Less than 8 chars
        "first_name": "Short",
        "last_name": "Pass",
        "date_of_birth": "1990-01-01"
    }
    response = client.post("/api/auth/register/patient", json=payload)
    assert response.status_code == 422


def test_registration_validation_invalid_email(client):
    payload = {
        "email": "not-a-valid-email",
        "password": "Password123!",
        "first_name": "Invalid",
        "last_name": "Email",
        "date_of_birth": "1990-01-01"
    }
    response = client.post("/api/auth/register/patient", json=payload)
    assert response.status_code == 422


def test_login_success_and_token_response(client):
    # Register user first
    reg_payload = {
        "email": "login.test@verticare.org",
        "password": "ValidPassword123!",
        "first_name": "Login",
        "last_name": "User",
        "date_of_birth": "1991-05-20"
    }
    client.post("/api/auth/register/patient", json=reg_payload)

    # Login
    login_payload = {
        "email": "login.test@verticare.org",
        "password": "ValidPassword123!"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "login.test@verticare.org"
    assert data["user"]["role"] == "PATIENT"
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]


def test_login_incorrect_password(client):
    # Register user
    reg_payload = {
        "email": "wrongpass@verticare.org",
        "password": "CorrectPassword123!",
        "first_name": "Wrong",
        "last_name": "Pass",
        "date_of_birth": "1990-01-01"
    }
    client.post("/api/auth/register/patient", json=reg_payload)

    # Login with wrong password
    login_payload = {
        "email": "wrongpass@verticare.org",
        "password": "IncorrectPassword!!!"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_nonexistent_email(client):
    login_payload = {
        "email": "nonexistent@verticare.org",
        "password": "Password123!"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401


def test_get_current_user_me_endpoint(client):
    # Register and login
    reg_payload = {
        "email": "me.test@verticare.org",
        "password": "Password123!",
        "first_name": "Current",
        "last_name": "User",
        "date_of_birth": "1993-08-10"
    }
    client.post("/api/auth/register/patient", json=reg_payload)

    login_res = client.post("/api/auth/login", json={"email": "me.test@verticare.org", "password": "Password123!"})
    token = login_res.json()["access_token"]

    # Call /api/auth/me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    user_data = me_res.json()
    assert user_data["email"] == "me.test@verticare.org"
    assert user_data["first_name"] == "Current"
    assert user_data["last_name"] == "User"
    assert user_data["role"] == "PATIENT"
    assert user_data["is_active"] is True

