import pytest
import requests
from .config import *
from firebase_admin import firestore, auth

db = firestore.client()

a_KMK_physician_information = {
    "role": "physician",
    "name": "Physician Test User Register",
    "last_name": "Test Last Name",
    "matricula": "777777",
    "specialty": "cardiolgy",
    "email": "registerPhysicianTestUser@kmk.com",
    "password": "verySecurePassword123",
}


@pytest.fixture(scope="session", autouse=True)
def create_test_user():
    created_user = auth.create_user(**a_KMK_physician_information)
    a_KMK_physician_information["uid"] = created_user.uid
    yield
    auth.delete_user(a_KMK_physician_information["uid"])


def test_approve_physician_endpoint_returns_201_code():
    created_user = auth.create_user(**a_KMK_physician_information)
    a_KMK_physician_information["uid"] = created_user.uid
    response_from_approve_phician_endpoint = requests.post(
        "http://localhost:8080/admins/approve-physician",
        json={
            "physician_id": a_KMK_physician_information["uid"],
        },
    )

    assert response_from_approve_phician_endpoint.status_code == 201


def test_deny_physician_endpoint_returns_201_code():
    created_user = auth.create_user(**a_KMK_physician_information)
    a_KMK_physician_information["uid"] = created_user.uid
    response_from_deny_phician_endpoint = requests.post(
        "http://localhost:8080/admins/deny-physician",
        json={
            "physician_id": a_KMK_physician_information["uid"],
        },
    )

    assert response_from_deny_phician_endpoint.status_code == 201
