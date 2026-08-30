from datetime import timedelta
import time
from app.core.security import hash_password, verify_password, create_access_token, verify_token


def test_password_hashing_not_plaintext():
    plain = "SuperSecurePassword123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")  # bcrypt identifier


def test_password_verification():
    plain = "ValidPassword456"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword789", hashed) is False
    assert verify_password("", hashed) is False


def test_jwt_creation_and_verification():
    token = create_access_token(
        user_id="test-uuid-123",
        role="PATIENT",
        email="patient@verticare.test"
    )
    assert isinstance(token, str)
    assert len(token) > 20

    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "test-uuid-123"
    assert payload["role"] == "PATIENT"
    assert payload["email"] == "patient@verticare.test"
    assert "exp" in payload


def test_jwt_expired_token():
    # Create token with -1 minute expiration
    token = create_access_token(
        user_id="expired-user",
        role="DOCTOR",
        email="expired@verticare.test",
        expires_delta=timedelta(seconds=-10)
    )
    payload = verify_token(token)
    assert payload is None


def test_jwt_invalid_token():
    assert verify_token("completely.invalid.token.string") is None
    assert verify_token("") is None

