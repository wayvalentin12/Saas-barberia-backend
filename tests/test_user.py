import pytest
import uuid
import requests

BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture(scope="module")
def unique_business():
    """Fixture to register a unique business for user tests."""
    negocio_name = f"Test Negocio {uuid.uuid4().hex[:6]}"
    res = requests.post(f"{BASE_URL}/register/negocio/", json={"name": negocio_name})
    assert res.status_code == 201
    return res.json()

@pytest.fixture(scope="module")
def unique_admin_user(unique_business):
    """Fixture to register a unique admin user under the test business."""
    negocio_id = unique_business["id"]
    email = f"admin_{uuid.uuid4().hex[:6]}@example.com"
    password = "adminpassword123"
    payload = {
        "name": "Admin User",
        "email": email,
        "role": "admin",
        "negocio_id": negocio_id,
        "password": password
    }
    res = requests.post(f"{BASE_URL}/register/usuario/", json=payload)
    assert res.status_code == 201
    user_data = res.json()
    user_data["password"] = password
    return user_data

@pytest.fixture(scope="module")
def admin_headers(unique_admin_user):
    """Fixture to login the admin user and return JWT auth headers."""
    login_data = {
        "username": unique_admin_user["email"],
        "password": unique_admin_user["password"]
    }
    res = requests.post(f"{BASE_URL}/login/", data=login_data)
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def temp_user(unique_business):
    """Fixture to register a temporary user for isolated modification/deletion tests."""
    email = f"temp_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "name": "Temp User",
        "email": email,
        "role": "client",
        "negocio_id": unique_business["id"],
        "password": "temppassword123"
    }
    res = requests.post(f"{BASE_URL}/register/usuario/", json=payload)
    assert res.status_code == 201
    return res.json()


def test_register_business():
    """Test successful business registration."""
    name = f"Test Negocio {uuid.uuid4().hex[:6]}"
    res = requests.post(f"{BASE_URL}/register/negocio/", json={"name": name})
    assert res.status_code == 201
    json_data = res.json()
    assert "id" in json_data
    assert json_data["name"] == name

def test_register_duplicate_business(unique_business):
    """Test that registering an already existing business name fails."""
    res = requests.post(f"{BASE_URL}/register/negocio/", json={"name": unique_business["name"]})
    assert res.status_code == 400
    assert res.json()["detail"] == "El negocio ya existe"

def test_register_user_duplicate_email(unique_admin_user, unique_business):
    """Test that registering a user with an already registered email fails."""
    payload = {
        "name": "Duplicate User",
        "email": unique_admin_user["email"],
        "role": "client",
        "negocio_id": unique_business["id"],
        "password": "somepassword"
    }
    res = requests.post(f"{BASE_URL}/register/usuario/", json=payload)
    assert res.status_code == 400
    assert res.json()["detail"] == "Email already registered"

def test_read_all_users(unique_admin_user):
    """Test reading all users."""
    res = requests.get(f"{BASE_URL}/users/")
    assert res.status_code == 200
    users = res.json()
    assert len(users) > 0
    emails = [u["email"] for u in users]
    assert unique_admin_user["email"] in emails

def test_read_single_user(unique_admin_user):
    """Test reading a single user specifically by their ID."""
    user_id = unique_admin_user["id"]
    res = requests.get(f"{BASE_URL}/users/{user_id}")
    assert res.status_code == 200
    assert res.json()["email"] == unique_admin_user["email"]

def test_read_non_existent_user():
    """Test that reading a non-existent user returns 404."""
    res = requests.get(f"{BASE_URL}/users/999999")
    assert res.status_code == 404
    assert res.json()["detail"] == "User not found"

def test_update_user_authorized(temp_user, admin_headers):
    """Test updating user details with authorization."""
    user_id = temp_user["id"]
    update_payload = {
        "name": "Updated Temp User",
        "role": "barbero"
    }
    res = requests.put(f"{BASE_URL}/users/{user_id}", json=update_payload, headers=admin_headers)
    assert res.status_code == 200
    updated_data = res.json()
    assert updated_data["name"] == "Updated Temp User"
    assert updated_data["role"] == "barbero"

def test_update_user_unauthorized(temp_user):
    """Test that updating a user without auth headers fails with 401."""
    user_id = temp_user["id"]
    update_payload = {
        "name": "Unauthorized Update"
    }
    res = requests.put(f"{BASE_URL}/users/{user_id}", json=update_payload)
    assert res.status_code == 401

def test_delete_user_authorized(temp_user, admin_headers):
    """Test deleting a user with authorization."""
    user_id = temp_user["id"]
    res = requests.delete(f"{BASE_URL}/users/{user_id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["detail"] == "User deleted"

    # Verify that requesting the deleted user returns 404
    res_check = requests.get(f"{BASE_URL}/users/{user_id}")
    assert res_check.status_code == 404

def test_delete_user_unauthorized(temp_user):
    """Test that deleting a user without auth headers fails with 401."""
    user_id = temp_user["id"]
    res = requests.delete(f"{BASE_URL}/users/{user_id}")
    assert res.status_code == 401

def test_get_all_negocios(unique_business):
    """Test retrieving all registered businesses."""
    res = requests.get(f"{BASE_URL}/negocios/")
    assert res.status_code == 200
    negocios = res.json()
    assert len(negocios) > 0
    names = [n["name"] for n in negocios]
    assert unique_business["name"] in names

def test_get_single_negocio(unique_business):
    """Test retrieving a specific business by ID."""
    negocio_id = unique_business["id"]
    res = requests.get(f"{BASE_URL}/negocios/{negocio_id}")
    assert res.status_code == 200
    assert res.json()["name"] == unique_business["name"]

def test_get_non_existent_negocio():
    """Test retrieving a non-existent business by ID returns 404."""
    res = requests.get(f"{BASE_URL}/negocios/999999")
    assert res.status_code == 404
    assert res.json()["detail"] == "Negocio no encontrado"

