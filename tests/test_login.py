import pytest
import uuid
import requests

BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture(scope="module")
def unique_business():
    """Fixture to register a unique business for login tests."""
    negocio_name = f"Test Negocio {uuid.uuid4().hex[:6]}"
    res = requests.post(f"{BASE_URL}/register/negocio/", json={"name": negocio_name})
    assert res.status_code == 201
    return res.json()

@pytest.fixture(scope="module")
def registered_user(unique_business):
    """Fixture to register a unique user under the test business."""
    email = f"user_{uuid.uuid4().hex[:6]}@example.com"
    password = "securepassword123"
    payload = {
        "name": "Login Test User",
        "email": email,
        "role": "admin",
        "negocio_id": unique_business["id"],
        "password": password
    }
    res = requests.post(f"{BASE_URL}/register/usuario/", json=payload)
    assert res.status_code == 201
    user_data = res.json()
    user_data["password"] = password
    return user_data

def test_successful_login(registered_user):
    """Test login with valid credentials."""
    login_data = {
        "username": registered_user["email"],
        "password": registered_user["password"]
    }
    res = requests.post(f"{BASE_URL}/login/", data=login_data)
    assert res.status_code == 200
    json_data = res.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"

def test_login_invalid_password(registered_user):
    """Test login with incorrect password."""
    login_data = {
        "username": registered_user["email"],
        "password": "wrong_password_here"
    }
    res = requests.post(f"{BASE_URL}/login/", data=login_data)
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid credentials"

def test_login_non_existent_user():
    """Test login with an email that is not registered."""
    login_data = {
        "username": f"nonexistent_{uuid.uuid4().hex[:6]}@example.com",
        "password": "some_password"
    }
    res = requests.post(f"{BASE_URL}/login/", data=login_data)
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid credentials"
