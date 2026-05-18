import pytest
import uuid
import requests

BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture(scope="module")
def unique_business():
    """Fixture to register a unique business for barber tests."""
    negocio_name = f"Barber Negocio {uuid.uuid4().hex[:6]}"
    res = requests.post(f"{BASE_URL}/register/negocio/", json={"name": negocio_name})
    assert res.status_code == 201
    return res.json()

@pytest.fixture(scope="module")
def unique_admin_user(unique_business):
    """Fixture to register an admin user under the test business."""
    negocio_id = unique_business["id"]
    email = f"admin_barber_{uuid.uuid4().hex[:6]}@example.com"
    password = "adminpassword123"
    payload = {
        "name": "Barber Admin User",
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
    """Fixture to login the admin and return JWT authorization headers."""
    login_data = {
        "username": unique_admin_user["email"],
        "password": unique_admin_user["password"]
    }
    res = requests.post(f"{BASE_URL}/login/", data=login_data)
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def temp_barber(unique_business):
    """Fixture to register a temporary barber for isolated tests."""
    email = f"barber_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "name": "Temp Barber",
        "email": email,
        "password": "barberpassword123",
        "negocio_id": unique_business["id"]
    }
    res = requests.post(f"{BASE_URL}/barbers/", json=payload)
    assert res.status_code == 201
    return res.json()


def test_create_barber(unique_business):
    """Test successful barber creation."""
    email = f"barber_{uuid.uuid4().hex[:6]}@example.com"
    payload = {
        "name": "New Barber",
        "email": email,
        "password": "barberpassword123",
        "negocio_id": unique_business["id"]
    }
    res = requests.post(f"{BASE_URL}/barbers/", json=payload)
    assert res.status_code == 201
    json_data = res.json()
    assert "id" in json_data
    assert json_data["name"] == "New Barber"
    assert json_data["email"] == email

def test_create_barber_duplicate_email(temp_barber, unique_business):
    """Test that creating a barber with an already registered email fails."""
    payload = {
        "name": "Another Barber",
        "email": temp_barber["email"],
        "password": "password123",
        "negocio_id": unique_business["id"]
    }
    res = requests.post(f"{BASE_URL}/barbers/", json=payload)
    assert res.status_code == 400
    assert res.json()["detail"] == "Email already registered"

def test_get_all_barbers(temp_barber):
    """Test retrieving all barbers."""
    res = requests.get(f"{BASE_URL}/barbers/")
    assert res.status_code == 200
    barbers = res.json()
    assert len(barbers) > 0
    emails = [b["email"] for b in barbers]
    assert temp_barber["email"] in emails

def test_get_all_barbers_filtered(temp_barber, unique_business):
    """Test retrieving barbers filtered by negocio_id."""
    res = requests.get(f"{BASE_URL}/barbers/", params={"negocio_id": unique_business["id"]})
    assert res.status_code == 200
    barbers = res.json()
    assert len(barbers) > 0
    for b in barbers:
        assert b["negocio_id"] == unique_business["id"]

def test_get_single_barber(temp_barber):
    """Test retrieving a specific barber by ID."""
    res = requests.get(f"{BASE_URL}/barbers/{temp_barber['id']}")
    assert res.status_code == 200
    assert res.json()["email"] == temp_barber["email"]

def test_get_non_existent_barber():
    """Test that retrieving a non-existent barber returns 404."""
    res = requests.get(f"{BASE_URL}/barbers/999999")
    assert res.status_code == 404
    assert res.json()["detail"] == "Barbero no encontrado"

def test_update_barber_authorized(temp_barber, admin_headers):
    """Test updating barber details with correct authorization."""
    update_payload = {
        "name": "Updated Barber Name",
        "email": f"updated_email_{uuid.uuid4().hex[:6]}@example.com"
    }
    res = requests.put(f"{BASE_URL}/barbers/{temp_barber['id']}", json=update_payload, headers=admin_headers)
    assert res.status_code == 200
    updated_data = res.json()
    assert updated_data["name"] == "Updated Barber Name"
    assert updated_data["email"] == update_payload["email"]

def test_update_barber_unauthorized(temp_barber):
    """Test that updating a barber without auth headers fails with 401."""
    update_payload = {"name": "Unauthorized"}
    res = requests.put(f"{BASE_URL}/barbers/{temp_barber['id']}", json=update_payload)
    assert res.status_code == 401

def test_update_barber_forbidden(temp_barber):
    """Test that updating a barber under a different business is forbidden (403)."""
    # 1. Create another business
    another_biz = requests.post(f"{BASE_URL}/register/negocio/", json={"name": f"Other Biz {uuid.uuid4().hex[:6]}"}).json()
    # 2. Register an admin in that other business
    other_email = f"other_admin_{uuid.uuid4().hex[:6]}@example.com"
    requests.post(f"{BASE_URL}/register/usuario/", json={
        "name": "Other Admin",
        "email": other_email,
        "role": "admin",
        "negocio_id": another_biz["id"],
        "password": "password123"
    })
    # 3. Log in as other admin
    token = requests.post(f"{BASE_URL}/login/", data={"username": other_email, "password": "password123"}).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {token}"}
    
    # 4. Attempt to update the first business's barber
    res = requests.put(f"{BASE_URL}/barbers/{temp_barber['id']}", json={"name": "Hacker Name"}, headers=other_headers)
    assert res.status_code == 403
    assert res.json()["detail"] == "No tienes permisos para modificar este barbero"

def test_delete_barber_authorized(temp_barber, admin_headers):
    """Test deleting a barber with correct authorization."""
    res = requests.delete(f"{BASE_URL}/barbers/{temp_barber['id']}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["detail"] == "Barber deleted"

    # Verify that requesting the deleted barber returns 404
    res_check = requests.get(f"{BASE_URL}/barbers/{temp_barber['id']}")
    assert res_check.status_code == 404

def test_delete_barber_unauthorized(temp_barber):
    """Test that deleting a barber without auth headers fails with 401."""
    res = requests.delete(f"{BASE_URL}/barbers/{temp_barber['id']}")
    assert res.status_code == 401

def test_delete_barber_forbidden(temp_barber):
    """Test that deleting a barber under a different business is forbidden (403)."""
    another_biz = requests.post(f"{BASE_URL}/register/negocio/", json={"name": f"Other Biz {uuid.uuid4().hex[:6]}"}).json()
    other_email = f"other_admin_{uuid.uuid4().hex[:6]}@example.com"
    requests.post(f"{BASE_URL}/register/usuario/", json={
        "name": "Other Admin",
        "email": other_email,
        "role": "admin",
        "negocio_id": another_biz["id"],
        "password": "password123"
    })
    token = requests.post(f"{BASE_URL}/login/", data={"username": other_email, "password": "password123"}).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {token}"}

    res = requests.delete(f"{BASE_URL}/barbers/{temp_barber['id']}", headers=other_headers)
    assert res.status_code == 403
    assert res.json()["detail"] == "No tienes permisos para eliminar este barbero"
