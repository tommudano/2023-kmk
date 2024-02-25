import pytest
from app.main import app
from firebase_admin import firestore, auth
from fastapi.testclient import TestClient
from unittest.mock import patch
import requests

client = TestClient(app)
db = firestore.client()

specialties = [
    "pediatrics",
    "dermatology",
    "gastroenterology",
    "radiology",
    "urology",
    "ophtalmology",
    "endocrynology",
    "neurology",
    "cardiology",
    "family medicine",
    "psychiatry",
]

a_KMK_physician_information = {
    "role": "physician",
    "first_name": "Physician Test User Register",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": specialties[0],
    "email": "testphysicianforregister@kmk.com",
    "password": "verySecurePassword123",
}

a_KMK_patient_information = {
    "role": "patient",
    "first_name": "Patient Test User Register",
    "last_name": "Test Last Name",
    "email": "testpatientforregister@kmk.com",
    "password": "verySecurePassword123",
    "birth_date": "9/1/2000",
    "gender": "m",
    "blood_type": "a",
}


@pytest.fixture(scope="module", autouse=True)
def load_and_delete_specialties():
    for specialty in specialties:
        id = db.collection("specialties").document().id
        db.collection("specialties").document(id).set(
            {"id": id, "name": specialty, "value": 3500}
        )
    yield
    specilaties_doc = db.collection("specialties").list_documents()
    for specialty_doc in specilaties_doc:
        specialty_doc.delete()


@pytest.fixture(scope="module", autouse=True)
def register_physician(load_and_delete_specialties):
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        r = client.post(
            "/users/register",
            json=a_KMK_physician_information,
        )
    uid = auth.get_user_by_email(a_KMK_physician_information["email"]).uid
    db.collection("physicians").document(uid).update({"approved": "approved"})
    yield
    uid = auth.get_user_by_email(a_KMK_physician_information["email"]).uid
    auth.delete_user(uid)
    db.collection("physicians").document(uid).delete()


@pytest.fixture(scope="module", autouse=True)
def register_patient(register_physician):
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        r = client.post(
            "/users/register",
            json=a_KMK_patient_information,
        )
    yield
    uid = auth.get_user_by_email(a_KMK_patient_information["email"]).uid
    auth.delete_user(uid)
    db.collection("patients").document(uid).delete()


@pytest.fixture(scope="module", autouse=True)
def log_in_physician(register_patient):
    pytest.physician_bearer = client.post(
        "/users/login",
        json={
            "email": a_KMK_physician_information["email"],
            "password": a_KMK_physician_information["password"],
        },
    ).json()["token"]
    yield


@pytest.fixture(scope="module", autouse=True)
def log_in_patient(log_in_physician):
    pytest.patient_bearer = client.post(
        "/users/login",
        json={
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    ).json()["token"]
    yield


def test_user_info_endpoint_returns_physician_information():
    user_info_response = client.get(
        "/users/user-info",
        headers={"Authorization": f"Bearer {pytest.physician_bearer}"},
    )

    assert user_info_response.status_code == 200
    user_info = user_info_response.json()
    assert type(user_info["id"]) == str
    assert type(user_info["agenda"]) == dict
    assert type(user_info["specialty"]) == dict
    user_info.pop("id")
    user_info.pop("agenda")
    user_info.pop("specialty")
    assert user_info == {
        "first_name": "Physician Test User Register",
        "last_name": "Test Last Name",
        "tuition": "777777",
        "email": "testphysicianforregister@kmk.com",
        "appointment_value": 3500,
        "google_meet_conference_enabled": False,
    }


def test_user_info_endpoint_returns_patient_information():
    user_info_response = client.get(
        "/users/user-info",
        headers={"Authorization": f"Bearer {pytest.patient_bearer}"},
    )

    assert user_info_response.status_code == 200
    user_info = user_info_response.json()
    assert type(user_info["id"]) == str
    user_info.pop("id")
    assert user_info == {
        "first_name": "Patient Test User Register",
        "last_name": "Test Last Name",
        "email": "testpatientforregister@kmk.com",
    }
