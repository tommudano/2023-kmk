import pytest
from firebase_admin import firestore, auth
from app.main import app
from fastapi.testclient import TestClient
import requests
from unittest.mock import patch

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
    "first_name": "Physician Test User Register 1",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": specialties[0],
    "email": "testphysicianfordenial@kmk.com",
    "approved": "denied",
    "agenda": {"1": {"start": 8, "finish": 18.5}},
}

another_KMK_physician_information = {
    "role": "physician",
    "first_name": "Physician Test User Register 2",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": specialties[0],
    "email": "testphysicianfordenial2@kmk.com",
    "approved": "approved",
    "agenda": {"1": {"start": 8, "finish": 18.5}},
}

a_KMK_patient_information = {
    "role": "patient",
    "first_name": "Patient Test User Register",
    "last_name": "Test Last Name",
    "email": "testpatientfordenial@kmk.com",
    "password": "verySecurePassword123",
    "birth_date": "9/1/2000",
    "gender": "m",
    "blood_type": "a",
}

initial_admin_information = {
    "email": "testinitialadminfordenial@kmk.com",
    "password": "verySecurePassword123",
}


@pytest.fixture(scope="module", autouse=True)
def load_and_delete_specialties():
    for specialty in specialties:
        db.collection("specialties").document().set({"name": specialty})
    yield
    specilaties_doc = db.collection("specialties").list_documents()
    for specialty_doc in specilaties_doc:
        specialty_doc.delete()


@pytest.fixture(scope="module", autouse=True)
def create_patient_and_then_delete_him(load_and_delete_specialties):
    created_user = auth.create_user(
        **{
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        }
    )
    pytest.a_patient_uid = created_user.uid
    db.collection("patients").document(pytest.a_patient_uid).set(
        {**a_KMK_patient_information, "id": pytest.a_patient_uid}
    )
    yield
    auth.delete_user(pytest.a_patient_uid)
    db.collection("patients").document(pytest.a_patient_uid).delete()


@pytest.fixture(autouse=True)
def create_a_denied_physician_and_then_delete_him():
    created_user = auth.create_user(
        **{
            "email": a_KMK_physician_information["email"],
            "password": "verySecurePassword123",
        }
    )
    pytest.a_physician_uid = created_user.uid
    db.collection("deniedPhysicians").document(pytest.a_physician_uid).set(
        {**a_KMK_physician_information, "id": pytest.a_physician_uid}
    )
    yield
    try:
        auth.delete_user(pytest.a_physician_uid)
        db.collection("deniedPhysicians").document(pytest.a_physician_uid).delete()
    except:
        print("[+] Physisican has not been created")


@pytest.fixture(autouse=True)
def create_another_denied_physician_and_then_delete_him():
    created_user = auth.create_user(
        **{
            "email": another_KMK_physician_information["email"],
            "password": "verySecurePassword123",
        }
    )
    pytest.another_physician_uid = created_user.uid
    db.collection("physicians").document(pytest.another_physician_uid).set(
        {**another_KMK_physician_information, "id": pytest.another_physician_uid}
    )
    yield
    try:
        auth.delete_user(pytest.another_physician_uid)
        db.collection("physicians").document(pytest.another_physician_uid).delete()
    except:
        print("[+] Physisican has not been created")


@pytest.fixture(scope="module", autouse=True)
def create_initial_admin_and_then_delete_him(
    create_patient_and_then_delete_him,
):
    pytest.initial_admin_uid = auth.create_user(**initial_admin_information).uid
    db.collection("superusers").document(pytest.initial_admin_uid).set(
        initial_admin_information
    )
    yield
    auth.delete_user(pytest.initial_admin_uid)
    db.collection("superusers").document(pytest.initial_admin_uid).delete()


@pytest.fixture(scope="module", autouse=True)
def log_in_initial_admin_user(create_initial_admin_and_then_delete_him):
    pytest.initial_admin_bearer = client.post(
        "/users/login",
        json={
            "email": initial_admin_information["email"],
            "password": initial_admin_information["password"],
        },
    ).json()["token"]
    yield


@pytest.fixture(scope="module", autouse=True)
def delete_unblocked_physicians(log_in_initial_admin_user):
    yield
    physician_docs = db.collection("physicians").list_documents()
    for physician_doc in physician_docs:
        physician_doc.delete()


def test_unblock_physician_endpoint_returns_a_200_code():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_from_unblock_physician_endpoint = client.post(
            f"/admin/unblock-physician/{pytest.a_physician_uid}",
            headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
        )

    assert response_from_unblock_physician_endpoint.status_code == 200


def test_unblock_physician_endpoint_returns_message():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_from_unblock_physician_endpoint = client.post(
            f"/admin/unblock-physician/{pytest.a_physician_uid}",
            headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
        )

    assert (
        response_from_unblock_physician_endpoint.json()["message"]
        == "Physician unblocked successfully"
    )


def test_unblock_physician_endpoint_removed_dennied_physician_record_from_firestore():
    assert (
        db.collection("deniedPhysicians").document(pytest.a_physician_uid).get().exists
        == True
    )
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            f"/admin/unblock-physician/{pytest.a_physician_uid}",
            headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
        )
    assert (
        db.collection("deniedPhysicians").document(pytest.a_physician_uid).get().exists
        == False
    )


def test_unblock_physician_endpoint_adds_physician_record_to_physicians_collection():
    assert (
        db.collection("physicians").document(pytest.a_physician_uid).get().exists
        == False
    )
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            f"/admin/unblock-physician/{pytest.a_physician_uid}",
            headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
        )

    physician_doc = db.collection("physicians").document(pytest.a_physician_uid).get()
    assert physician_doc.exists == True
    assert physician_doc.to_dict() == {
        **a_KMK_physician_information,
        "id": pytest.a_physician_uid,
        "approved": "approved",
        "appointments": {},
    }


def test_unblock_physician_endpoint_for_a_non_physician_returns_a_400_code_and_message():
    response_from_unblock_physician_endpoint = client.post(
        f"/admin/unblock-physician/{pytest.a_patient_uid}",
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert response_from_unblock_physician_endpoint.status_code == 400
    assert (
        response_from_unblock_physician_endpoint.json()["detail"]
        == "Can only unblock blocked physicians"
    )


def test_unblock_physician_endpoint_for_a_non_blocked_physician_returns_a_400_code_and_message():
    response_from_unblock_physician_endpoint = client.post(
        f"/admin/unblock-physician/{pytest.another_physician_uid}",
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert response_from_unblock_physician_endpoint.status_code == 400
    assert (
        response_from_unblock_physician_endpoint.json()["detail"]
        == "Can only unblock blocked physicians"
    )


def test_unblock_physician_with_no_authorization_header_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        f"/admin/unblock-physician/{pytest.a_physician_uid}"
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_unblock_physician_with_empty_authorization_header_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        f"/admin/unblock-physician/{pytest.a_physician_uid}",
        headers={"Authorization": ""},
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_unblock_physician_with_empty_bearer_token_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        f"/admin/unblock-physician/{pytest.a_physician_uid}",
        headers={"Authorization": f"Bearer "},
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_unblock_physician_with_non_bearer_token_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        f"/admin/unblock-physician/{pytest.a_physician_uid}",
        headers={"Authorization": pytest.initial_admin_bearer},
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_unblock_physician_with_invalid_bearer_token_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        f"/admin/unblock-physician/{pytest.a_physician_uid}",
        headers={"Authorization": "Bearer smth"},
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_unblock_physician_by_non_admin_returns_403_code_and_message():
    non_admin_bearer = client.post(
        "/users/login",
        json={
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    ).json()["token"]

    response_from_admin_registration_endpoint = client.post(
        f"/admin/unblock-physician/{pytest.a_physician_uid}",
        headers={"Authorization": f"Bearer {non_admin_bearer}"},
    )

    assert response_from_admin_registration_endpoint.status_code == 403
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be an admin"
    )


def test_unblock_physicians_endpoint_triggers_notification():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            f"/admin/unblock-physician/{pytest.a_physician_uid}",
            headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
        )

    assert mocked_request.call_count == 1
