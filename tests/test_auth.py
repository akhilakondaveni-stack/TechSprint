import uuid
import pytest
import sqlite3
from database import init_db, get_connection
from auth import register_user, login_user, get_user_by_id, is_rate_limited
from security import verify_password, is_valid_email, is_valid_password

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()

def test_registration_and_password_hashing():
    email = f"test_parent_{uuid.uuid4().hex[:8]}@example.com"
    pw = "SecretPass123!"
    success, msg, user = register_user(
        email=email,
        password=pw,
        full_name="Test Parent",
        role="parent"
    )
    assert success is True
    assert user is not None
    assert user["email"] == email
    assert "password_hash" not in user  # password hash must never leak in user dict

    # Verify password was hashed in database
    conn = get_connection()
    row = conn.execute("SELECT password_hash FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    assert row is not None
    assert row["password_hash"] != pw
    assert verify_password(pw, row["password_hash"]) is True

def test_duplicate_email_prevention():
    email = f"dup_test_{uuid.uuid4().hex[:8]}@example.com"
    register_user(email=email, password="ValidPassword123!", full_name="User One", role="parent")
    # Second attempt with same email
    success, msg, _ = register_user(email=email, password="ValidPassword123!", full_name="User Two", role="parent")
    assert success is False
    assert "already exists" in msg

def test_password_length_validation():
    valid, err = is_valid_password("short")
    assert valid is False
    assert "at least 8 characters" in err

    valid2, err2 = is_valid_password("longenoughpassword")
    assert valid2 is True
    assert err2 == ""

def test_email_validation():
    assert is_valid_email("valid.user@healthbuddy.org") is True
    assert is_valid_email("invalid-email") is False
    assert is_valid_email("@no-domain.com") is False

def test_login_flow_and_rate_limiting():
    email = f"ratelimit_{uuid.uuid4().hex[:8]}@example.com"
    pw = "GoodPassword123!"
    register_user(email=email, password=pw, full_name="RL User", role="parent")

    # Correct login
    ok, msg, u = login_user(email, pw)
    assert ok is True
    assert u["email"] == email

    # 5 Failed login attempts
    for _ in range(5):
        login_user(email, "WrongPassword!")

    # 6th attempt should be rate limited
    limited, wait_sec = is_rate_limited(email)
    assert limited is True
    assert wait_sec > 0

    ok_again, msg_again, _ = login_user(email, pw)
    assert ok_again is False
    assert "Too many failed login attempts" in msg_again
