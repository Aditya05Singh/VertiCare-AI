import pytest
from app.models.questionnaire import QuestionType, SessionStatus


def register_and_login_patient(client, email="patient.quiz@verticare.org", password="Password123!"):
    reg_payload = {
        "email": email,
        "password": password,
        "first_name": "Quiz",
        "last_name": "Patient",
        "date_of_birth": "1992-06-15",
        "gender": "FEMALE"
    }
    client.post("/api/auth/register/patient", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    return login_res.json()["access_token"]


def register_and_login_doctor(client, email="doctor.quiz@verticare.org", password="DoctorPass123!"):
    reg_payload = {
        "email": email,
        "password": password,
        "first_name": "Doctor",
        "last_name": "Quiz",
        "specialization": "ENT",
        "license_identifier": f"LIC-{email.split('@')[0]}"
    }
    client.post("/api/auth/register/doctor", json=reg_payload)
    login_res = client.post("/api/auth/login", json={"email": email, "password": password})
    return login_res.json()["access_token"]


def test_start_questionnaire_session(client):
    token = register_and_login_patient(client, "pat.start@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/questionnaire/start", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "IN_PROGRESS"
    assert data["session_id"] is not None
    assert data["current_question"] is not None
    assert data["current_question"]["question_code"] == "Q_SPINNING"
    assert data["current_question"]["question_type"] == "BOOLEAN"
    assert data["progress"]["answered_count"] == 0


def test_adaptive_branching_yes_path(client):
    token = register_and_login_patient(client, "pat.branch.yes@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    # Start session
    start_res = client.get("/api/questionnaire/start", headers=headers)
    session_id = start_res.json()["session_id"]

    # Answer YES (true) to Q_SPINNING -> should transition to Q_POSITIONAL
    ans1_res = client.post(
        f"/api/questionnaire/session/{session_id}/answer",
        json={"question_code": "Q_SPINNING", "answer": True},
        headers=headers
    )
    assert ans1_res.status_code == 200
    data1 = ans1_res.json()
    assert data1["current_question"]["question_code"] == "Q_POSITIONAL"
    assert data1["progress"]["answered_count"] == 1

    # Answer YES (true) to Q_POSITIONAL -> should transition to Q_EPISODE_DURATION_POS
    ans2_res = client.post(
        f"/api/questionnaire/session/{session_id}/answer",
        json={"question_code": "Q_POSITIONAL", "answer": True},
        headers=headers
    )
    assert ans2_res.status_code == 200
    data2 = ans2_res.json()
    assert data2["current_question"]["question_code"] == "Q_EPISODE_DURATION_POS"


def test_adaptive_branching_no_path(client):
    token = register_and_login_patient(client, "pat.branch.no@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    start_res = client.get("/api/questionnaire/start", headers=headers)
    session_id = start_res.json()["session_id"]

    # Answer NO (false) to Q_SPINNING -> should transition to Q_NON_SPIN_TYPE
    ans1_res = client.post(
        f"/api/questionnaire/session/{session_id}/answer",
        json={"question_code": "Q_SPINNING", "answer": False},
        headers=headers
    )
    assert ans1_res.status_code == 200
    data1 = ans1_res.json()
    assert data1["current_question"]["question_code"] == "Q_NON_SPIN_TYPE"
    assert data1["current_question"]["question_type"] == "SINGLE_CHOICE"


def test_single_choice_branching_and_validation(client):
    token = register_and_login_patient(client, "pat.choice@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    start_res = client.get("/api/questionnaire/start", headers=headers)
    session_id = start_res.json()["session_id"]

    # Go to Q_NON_SPIN_TYPE
    client.post(
        f"/api/questionnaire/session/{session_id}/answer",
        json={"question_code": "Q_SPINNING", "answer": False},
        headers=headers
    )

    # Submit illegal choice value -> 422
    bad_choice_res = client.post(
        f"/api/questionnaire/session/{session_id}/answer",
        json={"question_code": "Q_NON_SPIN_TYPE", "answer": "non_existent_option"},
        headers=headers
    )
    assert bad_choice_res.status_code == 422

    # Submit valid choice "unsteadiness" -> should branch to Q_GAIT_DIFFICULTY
    valid_choice_res = client.post(
        f"/api/questionnaire/session/{session_id}/answer",
        json={"question_code": "Q_NON_SPIN_TYPE", "answer": "unsteadiness"},
        headers=headers
    )
    assert valid_choice_res.status_code == 200
    assert valid_choice_res.json()["current_question"]["question_code"] == "Q_GAIT_DIFFICULTY"


def test_flow_security_rejects_out_of_order_question(client):
    token = register_and_login_patient(client, "pat.order.sec@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    start_res = client.get("/api/questionnaire/start", headers=headers)
    session_id = start_res.json()["session_id"]

    # Current question is Q_SPINNING. Attacker tries to submit answer for Q_FUNCTIONAL_IMPACT directly:
    malicious_res = client.post(
        f"/api/questionnaire/session/{session_id}/answer",
        json={"question_code": "Q_FUNCTIONAL_IMPACT", "answer": "mild"},
        headers=headers
    )
    assert malicious_res.status_code == 400
    assert "Question order mismatch" in malicious_res.json()["detail"]


def test_full_questionnaire_traversal_and_summary(client):
    token = register_and_login_patient(client, "pat.full.flow@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    session_id = client.get("/api/questionnaire/start", headers=headers).json()["session_id"]

    # Step 1: Q_SPINNING -> True
    client.post(f"/api/questionnaire/session/{session_id}/answer", json={"question_code": "Q_SPINNING", "answer": True}, headers=headers)
    # Step 2: Q_POSITIONAL -> True
    client.post(f"/api/questionnaire/session/{session_id}/answer", json={"question_code": "Q_POSITIONAL", "answer": True}, headers=headers)
    # Step 3: Q_EPISODE_DURATION_POS -> "seconds"
    client.post(f"/api/questionnaire/session/{session_id}/answer", json={"question_code": "Q_EPISODE_DURATION_POS", "answer": "seconds"}, headers=headers)
    # Step 4: Q_HEAD_TURNS -> "right"
    client.post(f"/api/questionnaire/session/{session_id}/answer", json={"question_code": "Q_HEAD_TURNS", "answer": "right"}, headers=headers)
    # Step 5: Q_ASSOCIATED_SYMPTOMS -> ["nausea", "headache"]
    client.post(f"/api/questionnaire/session/{session_id}/answer", json={"question_code": "Q_ASSOCIATED_SYMPTOMS", "answer": ["nausea", "headache"]}, headers=headers)
    # Step 6: Q_FUNCTIONAL_IMPACT (Terminal) -> "moderate"
    last_res = client.post(f"/api/questionnaire/session/{session_id}/answer", json={"question_code": "Q_FUNCTIONAL_IMPACT", "answer": "moderate"}, headers=headers)

    assert last_res.status_code == 200
    data = last_res.json()
    assert data["status"] == "COMPLETED"
    assert data["current_question"] is None
    assert data["message"] == "Questionnaire completed."

    # Get non-diagnostic summary
    summary_res = client.get(f"/api/questionnaire/session/{session_id}/summary", headers=headers)
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["status"] == "COMPLETED"
    assert summary["total_questions_answered"] == 6
    assert "does not represent a medical diagnosis" in summary["notice"]
    assert "BPPV" not in summary["notice"]


def test_session_resume_behavior(client):
    token = register_and_login_patient(client, "pat.resume@verticare.org")
    headers = {"Authorization": f"Bearer {token}"}

    # Start session and answer 1 question
    s1 = client.get("/api/questionnaire/start", headers=headers).json()
    session_id = s1["session_id"]
    client.post(f"/api/questionnaire/session/{session_id}/answer", json={"question_code": "Q_SPINNING", "answer": True}, headers=headers)

    # Calling start again should resume the active in-progress session
    s2 = client.get("/api/questionnaire/start", headers=headers).json()
    assert s2["session_id"] == session_id
    assert s2["current_question"]["question_code"] == "Q_POSITIONAL"
    assert s2["progress"]["answered_count"] == 1


def test_security_cross_patient_idor_blocked(client):
    # Patient A starts session
    token_a = register_and_login_patient(client, "patient.a.quiz@verticare.org")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    session_a_id = client.get("/api/questionnaire/start", headers=headers_a).json()["session_id"]

    # Patient B attempts to access Patient A's session
    token_b = register_and_login_patient(client, "patient.b.quiz@verticare.org")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    get_idor = client.get(f"/api/questionnaire/session/{session_a_id}", headers=headers_b)
    assert get_idor.status_code == 404

    # Patient B attempts to submit answer into Patient A's session
    post_idor = client.post(
        f"/api/questionnaire/session/{session_a_id}/answer",
        json={"question_code": "Q_SPINNING", "answer": True},
        headers=headers_b
    )
    assert post_idor.status_code == 404


def test_doctor_cannot_start_questionnaire(client):
    token_doc = register_and_login_doctor(client, "doctor.deny.quiz@verticare.org")
    headers_doc = {"Authorization": f"Bearer {token_doc}"}

    res = client.get("/api/questionnaire/start", headers=headers_doc)
    assert res.status_code == 403

