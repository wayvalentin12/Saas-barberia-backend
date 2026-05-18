import requests
import datetime


def test_create_appoiment():
    response = requests.post("http://localhost:8000/appointments/crear-citas/", json={
        "username": "Juan",
        "date_time": "2026-05-18T04:11:31.675Z",
        "service": "fade bajito",
        "barber_id": 1 
    })
    assert response.status_code == 200
    
def test_read_appointments():
    response = requests.get("http://localhost:8000/appointments/todas-las-citas/")
    assert response.status_code == 200
    