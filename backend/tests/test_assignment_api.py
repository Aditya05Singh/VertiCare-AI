import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.profile import PatientProfile, DoctorProfile, DoctorPatient


def register_user(client: TestClient, role: str, email: str, identifier: str = ""):
    if role == "DOCTOR":
        reg = client.post(
            "/api/auth/register/doctor",
            json={
                "email": email,
                "password": "Password123!",
                "first_name": "Doctor",
                "last_name": "Marcus",
                "specialization": "Vestibular Neurology",
                "license_identifier": identifier or f"LIC-{email}"
            }
        )
    else:
        reg = client.post(
            "/api/auth/register/patient",
            json={
                "email": email,
                "password": "Password123!",
                "first_name": "Patient",
                "last_name": "Alice",
                "date_of_birth": "1992-03-15",
                "gender": "FEMALE",
                "emergency_contact_name": "Family",
                "emergency_contact_phone": "+1-555-0199"
            }
        )
    assert reg.status_code == 201
    user_info = reg.json()

    login = client.post(
        "/api/auth/login",
        json={"email": email, "password": "Password123!"}
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return user_info, headers


def test_doctor_initiated_assignment_flow(client: TestClient, db_session: Session):
    doc_info, doc_headers = register_user(client, "DOCTOR", "doc.assign1@verticare.org", "LIC-A1")
    pat_info, pat_headers = register_user(client, "PATIENT", "pat.assign1@verticare.org")

    patient_id = pat_info["patient_profile_id"]
    doctor_id = doc_info["doctor_profile_id"]

    # 1. Doctor assigns patient using patient_id
    assign_res = client.post(
        "/api/assignments",
        headers=doc_headers,
        json={"patient_id": patient_id}
    )
    assert assign_res.status_code == 201
    assignment = assign_res.json()
    assert assignment["doctor_id"] == doctor_id
    assert assignment["patient_id"] == patient_id
    assert "Doctor Marcus" in assignment["doctor_name"]
    assert "Patient Alice" in assignment["patient_name"]

    # 2. Duplicate assignment is rejected with 409
    dup_res = client.post(
        "/api/assignments",
        headers=doc_headers,
        json={"patient_id": patient_id}
    )
    assert dup_res.status_code == 409
    assert "already assigned" in dup_res.json()["detail"].lower()

    # 3. Mutual visibility: Doctor sees patient in assigned list
    doc_list_res = client.get("/api/doctor/assigned-patients", headers=doc_headers)
    assert doc_list_res.status_code == 200
    doc_patients = doc_list_res.json()["items"]
    assert len(doc_patients) >= 1
    assert any(p["patient_id"] == patient_id for p in doc_patients)

    # 4. Mutual visibility: Patient sees doctor in assigned doctor endpoint
    pat_doc_res = client.get("/api/patient/assigned-doctor", headers=pat_headers)
    assert pat_doc_res.status_code == 200
    pat_doc_json = pat_doc_res.json()
    assert pat_doc_json["has_assigned_doctor"] is True
    assert pat_doc_json["doctor_id"] == doctor_id
    assert "Doctor Marcus" in pat_doc_json["doctor_name"]

    # 5. Patient can view doctor's public profile
    prof_res = client.get(f"/api/patient/doctor-profile/{doctor_id}", headers=pat_headers)
    assert prof_res.status_code == 200
    assert prof_res.json()["specialization"] == "Vestibular Neurology"


def test_patient_initiated_assignment_flow(client: TestClient, db_session: Session):
    doc_info, doc_headers = register_user(client, "DOCTOR", "doc.assign2@verticare.org", "LIC-A2")
    pat_info, pat_headers = register_user(client, "PATIENT", "pat.assign2@verticare.org")

    doctor_id = doc_info["doctor_profile_id"]
    patient_id = pat_info["patient_profile_id"]

    # 1. Patient assigns doctor using doctor_id
    assign_res = client.post(
        "/api/assignments",
        headers=pat_headers,
        json={"doctor_id": doctor_id}
    )
    assert assign_res.status_code == 201
    assignment = assign_res.json()
    assert assignment["doctor_id"] == doctor_id
    assert assignment["patient_id"] == patient_id

    # 2. Patient duplicate assignment rejected with 409
    dup_res = client.post(
        "/api/assignments",
        headers=pat_headers,
        json={"doctor_id": doctor_id}
    )
    assert dup_res.status_code == 409

    # 3. Doctor can immediately access assigned patient dossier
    dossier_res = client.get(f"/api/doctor/patients/{patient_id}", headers=doc_headers)
    assert dossier_res.status_code == 200
    assert dossier_res.json()["patient_id"] == patient_id

    # 4. Unassign relationship
    assignment_id = assignment["id"]
    del_res = client.delete(f"/api/assignments/{assignment_id}", headers=pat_headers)
    assert del_res.status_code == 200

    # 5. Verify relationship removed from both sides
    check_pat = client.get("/api/patient/assigned-doctor", headers=pat_headers)
    assert check_pat.json()["has_assigned_doctor"] is False

    check_doc = client.get(f"/api/doctor/patients/{patient_id}", headers=doc_headers)
    assert check_doc.status_code == 404  # Anti-IDOR unassigned patient access blocked


def test_assignment_validation_and_security(client: TestClient, db_session: Session):
    doc_info, doc_headers = register_user(client, "DOCTOR", "doc.sec@verticare.org", "LIC-SEC")
    pat1_info, pat1_headers = register_user(client, "PATIENT", "pat1.sec@verticare.org")
    pat2_info, pat2_headers = register_user(client, "PATIENT", "pat2.sec@verticare.org")

    # 1. Nonexistent patient ID
    bad_pat = client.post(
        "/api/assignments",
        headers=doc_headers,
        json={"patient_id": "nonexistent-id-000"}
    )
    assert bad_pat.status_code == 404

    # 2. Doctor enters another Doctor's ID as patient
    doc2_info, _ = register_user(client, "DOCTOR", "doc2.sec@verticare.org", "LIC-SEC2")
    bad_role = client.post(
        "/api/assignments",
        headers=doc_headers,
        json={"patient_id": doc2_info["doctor_profile_id"]}
    )
    assert bad_role.status_code in (400, 404)

    # 3. Patient enters another Patient's ID as doctor
    bad_doc_role = client.post(
        "/api/assignments",
        headers=pat1_headers,
        json={"doctor_id": pat2_info["patient_profile_id"]}
    )
    assert bad_doc_role.status_code in (400, 404)

    # 4. Unauthenticated assignment rejected
    unauth = client.post("/api/assignments", json={"patient_id": "xyz"})
    assert unauth.status_code == 401
