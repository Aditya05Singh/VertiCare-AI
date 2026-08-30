import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.profile import PatientProfile, DoctorProfile, DoctorPatient, Gender
from app.models.emergency import EmergencyEvent, EmergencySeverity, EmergencyStatus
from app.models.risk import RiskAssessment, RiskLevel


def create_test_users_and_assignment(db: Session, client: TestClient):
    """Helper to setup Doctor 1, Patient 1 (assigned to Doc 1), and Patient 2 (unassigned)."""
    # Register Doctor 1
    doc1_reg = {
        "email": "doc1.emergency@verticare.org",
        "password": "Password123!",
        "first_name": "Doctor",
        "last_name": "One",
        "specialization": "Vestibular Neurology",
        "license_identifier": "LIC-EMERG-001"
    }
    r = client.post("/api/auth/register/doctor", json=doc1_reg)
    assert r.status_code == 201
    doc1_login = client.post(
        "/api/auth/login",
        json={"email": "doc1.emergency@verticare.org", "password": "Password123!"}
    )
    doc1_token = doc1_login.json()["access_token"]
    doc1_headers = {"Authorization": f"Bearer {doc1_token}"}

    # Register Doctor 2 (for cross-doctor IDOR tests)
    doc2_reg = {
        "email": "doc2.emergency@verticare.org",
        "password": "Password123!",
        "first_name": "Doctor",
        "last_name": "Two",
        "specialization": "ENT",
        "license_identifier": "LIC-EMERG-002"
    }
    r = client.post("/api/auth/register/doctor", json=doc2_reg)
    assert r.status_code == 201
    doc2_login = client.post(
        "/api/auth/login",
        json={"email": "doc2.emergency@verticare.org", "password": "Password123!"}
    )
    doc2_token = doc2_login.json()["access_token"]
    doc2_headers = {"Authorization": f"Bearer {doc2_token}"}

    # Register Patient 1
    pat1_reg = {
        "email": "pat1.emergency@verticare.org",
        "password": "Password123!",
        "first_name": "Patient",
        "last_name": "One",
        "date_of_birth": "1990-05-15",
        "gender": "FEMALE",
        "emergency_contact_name": "Family Member",
        "emergency_contact_phone": "+1-555-0101"
    }
    r = client.post("/api/auth/register/patient", json=pat1_reg)
    assert r.status_code == 201
    pat1_login = client.post(
        "/api/auth/login",
        json={"email": "pat1.emergency@verticare.org", "password": "Password123!"}
    )
    pat1_token = pat1_login.json()["access_token"]
    pat1_headers = {"Authorization": f"Bearer {pat1_token}"}

    # Register Patient 2 (Not assigned to Doctor 1)
    pat2_reg = {
        "email": "pat2.emergency@verticare.org",
        "password": "Password123!",
        "first_name": "Patient",
        "last_name": "Two",
        "date_of_birth": "1995-10-20",
        "gender": "MALE",
        "emergency_contact_name": "Friend",
        "emergency_contact_phone": "+1-555-0202"
    }
    r = client.post("/api/auth/register/patient", json=pat2_reg)
    assert r.status_code == 201
    pat2_login = client.post(
        "/api/auth/login",
        json={"email": "pat2.emergency@verticare.org", "password": "Password123!"}
    )
    pat2_token = pat2_login.json()["access_token"]
    pat2_headers = {"Authorization": f"Bearer {pat2_token}"}

    # Query DB entities
    doc1 = db.query(DoctorProfile).filter(DoctorProfile.license_identifier == "LIC-EMERG-001").first()
    pat1 = db.query(PatientProfile).filter(PatientProfile.emergency_contact_name == "Family Member").first()
    pat2 = db.query(PatientProfile).filter(PatientProfile.emergency_contact_name == "Friend").first()

    # Assign Patient 1 to Doctor 1
    assignment = DoctorPatient(doctor_id=doc1.id, patient_id=pat1.id)
    db.add(assignment)
    db.commit()

    return {
        "doc1_headers": doc1_headers,
        "doc2_headers": doc2_headers,
        "pat1_headers": pat1_headers,
        "pat2_headers": pat2_headers,
        "doc1_id": doc1.id,
        "pat1_id": pat1.id,
        "pat2_id": pat2.id,
    }


def test_patient_emergency_event_creation_and_actions(client: TestClient, db_session: Session):
    data = create_test_users_and_assignment(db_session, client)
    pat1_headers = data["pat1_headers"]

    # 1. Check guidance endpoint
    g_res = client.get("/api/emergency-events/guidance")
    assert g_res.status_code == 200
    assert len(g_res.json()["guidance"]) > 0

    # 2. Check context endpoint
    c_res = client.get("/api/emergency-events/context", headers=pat1_headers)
    assert c_res.status_code == 200
    c_json = c_res.json()
    assert c_json["has_emergency_contact"] is True
    assert c_json["emergency_contact_name"] == "Family Member"
    assert c_json["has_assigned_doctor"] is True
    assert "Doctor One" in c_json["assigned_doctor_name"]

    # 3. Create Emergency Event
    create_res = client.post(
        "/api/emergency-events",
        headers=pat1_headers,
        json={
            "severity": "HIGH",
            "notes": "Sudden severe room spinning while seated.",
            "initiate_doctor_contact": False,
            "initiate_emergency_contact": False
        }
    )
    assert create_res.status_code == 201
    event = create_res.json()
    assert event["status"] == "PENDING"
    assert event["severity"] == "HIGH"
    assert event["contacted_doctor"] is False
    assert event["contacted_emergency_contact"] is False
    event_id = event["id"]

    # 4. Patient executes action: CONTACT_DOCTOR
    doc_action_res = client.post(
        f"/api/emergency-events/{event_id}/patient-action",
        headers=pat1_headers,
        json={"action": "CONTACT_DOCTOR", "notes": "Requesting urgent phone review."}
    )
    assert doc_action_res.status_code == 200
    updated = doc_action_res.json()
    assert updated["contacted_doctor"] is True
    assert updated["status"] == "CONTACT_INITIATED"
    assert updated["contacted_at"] is not None

    # 5. Patient executes action: CONTACT_EMERGENCY_CONTACT
    ec_action_res = client.post(
        f"/api/emergency-events/{event_id}/patient-action",
        headers=pat1_headers,
        json={"action": "CONTACT_EMERGENCY_CONTACT", "notes": "Called family member."}
    )
    assert ec_action_res.status_code == 200
    updated_ec = ec_action_res.json()
    assert updated_ec["contacted_emergency_contact"] is True

    # 6. Patient reads own event and list
    list_res = client.get("/api/emergency-events", headers=pat1_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 1
    assert list_res.json()["items"][0]["id"] == event_id

    detail_res = client.get(f"/api/emergency-events/{event_id}", headers=pat1_headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == event_id


def test_doctor_emergency_review_and_resolution_flow(client: TestClient, db_session: Session):
    data = create_test_users_and_assignment(db_session, client)
    pat1_headers = data["pat1_headers"]
    doc1_headers = data["doc1_headers"]

    # Patient 1 creates an event with immediate doctor contact
    create_res = client.post(
        "/api/emergency-events",
        headers=pat1_headers,
        json={
            "severity": "CRITICAL",
            "notes": "Patient unable to stand.",
            "initiate_doctor_contact": True
        }
    )
    assert create_res.status_code == 201
    event_id = create_res.json()["id"]
    assert create_res.json()["status"] == "CONTACT_INITIATED"

    # Doctor 1 reads assigned patient emergency events
    doc_list_res = client.get("/api/emergency-events", headers=doc1_headers)
    assert doc_list_res.status_code == 200
    assert doc_list_res.json()["total"] >= 1
    assert any(e["id"] == event_id for e in doc_list_res.json()["items"])

    # Doctor 1 reads event detail
    doc_detail_res = client.get(f"/api/emergency-events/{event_id}", headers=doc1_headers)
    assert doc_detail_res.status_code == 200
    assert doc_detail_res.json()["severity"] == "CRITICAL"

    # Doctor 1 Acknowledges event
    ack_res = client.post(
        f"/api/emergency-events/{event_id}/doctor-action",
        headers=doc1_headers,
        json={"action": "ACKNOWLEDGE", "notes": "Contacted patient by phone; resting in clinic."}
    )
    assert ack_res.status_code == 200
    assert ack_res.json()["status"] == "ACKNOWLEDGED"

    # Doctor 1 Resolves event
    resolve_res = client.post(
        f"/api/emergency-events/{event_id}/doctor-action",
        headers=doc1_headers,
        json={"action": "RESOLVE", "notes": "Symptoms subsided; scheduled for routine clinic visit."}
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"


def test_security_anti_idor_and_role_protection(client: TestClient, db_session: Session):
    data = create_test_users_and_assignment(db_session, client)
    pat1_headers = data["pat1_headers"]
    pat2_headers = data["pat2_headers"]
    doc1_headers = data["doc1_headers"]
    doc2_headers = data["doc2_headers"]

    # Patient 2 creates an emergency event
    p2_event_res = client.post(
        "/api/emergency-events",
        headers=pat2_headers,
        json={"severity": "HIGH", "notes": "Patient 2 event."}
    )
    assert p2_event_res.status_code == 201
    p2_event_id = p2_event_res.json()["id"]

    # 1. Cross-Patient IDOR: Patient 1 cannot view Patient 2's event
    p1_read_p2 = client.get(f"/api/emergency-events/{p2_event_id}", headers=pat1_headers)
    assert p1_read_p2.status_code == 404

    # 2. Cross-Patient IDOR: Patient 1 cannot perform action on Patient 2's event
    p1_act_p2 = client.post(
        f"/api/emergency-events/{p2_event_id}/patient-action",
        headers=pat1_headers,
        json={"action": "CANCEL"}
    )
    assert p1_act_p2.status_code == 404

    # 3. Unassigned Doctor IDOR: Doctor 1 cannot view unassigned Patient 2's event
    doc1_read_p2 = client.get(f"/api/emergency-events/{p2_event_id}", headers=doc1_headers)
    assert doc1_read_p2.status_code == 404

    # 4. Unassigned Doctor IDOR: Doctor 1 cannot acknowledge/resolve unassigned Patient 2's event
    doc1_act_p2 = client.post(
        f"/api/emergency-events/{p2_event_id}/doctor-action",
        headers=doc1_headers,
        json={"action": "ACKNOWLEDGE"}
    )
    assert doc1_act_p2.status_code == 404

    # 5. Role Protection: Patient cannot call doctor action
    pat_doc_act = client.post(
        f"/api/emergency-events/{p2_event_id}/doctor-action",
        headers=pat2_headers,
        json={"action": "ACKNOWLEDGE"}
    )
    assert pat_doc_act.status_code == 403

    # 6. Role Protection: Doctor cannot call patient action
    doc_pat_act = client.post(
        f"/api/emergency-events/{p2_event_id}/patient-action",
        headers=doc1_headers,
        json={"action": "CONTACT_DOCTOR"}
    )
    assert doc_pat_act.status_code == 403

    # 7. Unauthenticated blocked
    unauth = client.get("/api/emergency-events")
    assert unauth.status_code == 401


def test_emergency_state_machine_invalid_transitions(client: TestClient, db_session: Session):
    data = create_test_users_and_assignment(db_session, client)
    pat1_headers = data["pat1_headers"]
    doc1_headers = data["doc1_headers"]

    # Patient creates and cancels event
    create_res = client.post(
        "/api/emergency-events",
        headers=pat1_headers,
        json={"severity": "MEDIUM", "notes": "Mild spell, self-resolved."}
    )
    event_id = create_res.json()["id"]

    cancel_res = client.post(
        f"/api/emergency-events/{event_id}/patient-action",
        headers=pat1_headers,
        json={"action": "CANCEL", "notes": "False alarm."}
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "CANCELLED"

    # Cannot initiate contact on a cancelled event
    bad_contact = client.post(
        f"/api/emergency-events/{event_id}/patient-action",
        headers=pat1_headers,
        json={"action": "CONTACT_DOCTOR"}
    )
    assert bad_contact.status_code == 400

    # Doctor cannot resolve a cancelled event
    bad_resolve = client.post(
        f"/api/emergency-events/{event_id}/doctor-action",
        headers=doc1_headers,
        json={"action": "RESOLVE"}
    )
    assert bad_resolve.status_code == 400

