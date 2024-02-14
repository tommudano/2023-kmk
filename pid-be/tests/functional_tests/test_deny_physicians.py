import pytest
import time
from datetime import datetime, timedelta
from firebase_admin import firestore, auth
from app.main import app
from fastapi.testclient import TestClient
import requests
from unittest.mock import patch

client = TestClient(app)

db = firestore.client()

today_date = datetime.fromtimestamp(round(time.time()))
number_of_day_of_week = int(today_date.date().strftime("%w"))

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
    "password": "verySecurePassword123",
    "approved": "approved",
    "agenda": {str(number_of_day_of_week): {"start": 8.0, "finish": 18.5}},
}

another_KMK_physician_information = {
    "role": "physician",
    "first_name": "Physician Test User Register 2",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": specialties[0],
    "email": "testphysicianfordenial2@kmk.com",
    "password": "verySecurePassword123",
    "approved": "pending",
    "agenda": {str(number_of_day_of_week): {"start": 8.0, "finish": 18.5}},
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
        a_KMK_patient_information
    )
    yield
    auth.delete_user(pytest.a_patient_uid)
    db.collection("patients").document(pytest.a_patient_uid).delete()


@pytest.fixture(scope="module", autouse=True)
def login_patient(create_patient_and_then_delete_him):
    response_from_login_endpoint_for_first_user = client.post(
        "/users/login",
        json={
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    )

    pytest.first_bearer = response_from_login_endpoint_for_first_user.json()["token"]


@pytest.fixture(autouse=True)
def create_a_physician_and_then_delete_him():
    created_user = auth.create_user(
        **{
            "email": a_KMK_physician_information["email"],
            "password": a_KMK_physician_information["password"],
        }
    )
    pytest.a_physician_uid = created_user.uid
    db.collection("physicians").document(pytest.a_physician_uid).set(
        a_KMK_physician_information
    )
    yield
    try:
        auth.delete_user(pytest.a_physician_uid)
        db.collection("physicians").document(pytest.a_physician_uid).delete()
    except:
        print("[+] Physisican has not been created")


@pytest.fixture(autouse=True)
def create_another_physician_and_then_delete_him(
    create_a_physician_and_then_delete_him,
):
    created_user = auth.create_user(
        **{
            "email": another_KMK_physician_information["email"],
            "password": another_KMK_physician_information["password"],
        }
    )
    pytest.another_physician_uid = created_user.uid
    db.collection("physicians").document(pytest.another_physician_uid).set(
        another_KMK_physician_information
    )
    yield
    try:
        auth.delete_user(pytest.another_physician_uid)
        db.collection("physicians").document(pytest.another_physician_uid).delete()
    except:
        print("[+] Physisican has not been created")


@pytest.fixture(autouse=True)
def create_test_appointment(create_another_physician_and_then_delete_him):
    next_week_day = today_date + timedelta(days=7)
    next_week_day_first_block = next_week_day.replace(hour=9)
    an_appointment_data = {
        "date": round(next_week_day_first_block.timestamp()),
        "physician_id": pytest.a_physician_uid,
    }
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        appointment_creation_response = client.post(
            "/appointments",
            json=an_appointment_data,
            headers={"Authorization": f"Bearer {pytest.first_bearer}"},
        )

    pytest.appointment_id = appointment_creation_response.json()["appointment_id"]
    yield


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
def delete_denied_physicians(log_in_initial_admin_user):
    yield
    denied_physicians_doc = db.collection("deniedPhysicians").list_documents()
    for denied_physician_doc in denied_physicians_doc:
        denied_physician_doc.delete()


def test_deny_physician_endpoint_returns_a_200_code():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_from_deny_physician_endpoint = client.post(
            f"/admin/deny-physician/{pytest.a_physician_uid}",
            headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
        )

    assert response_from_deny_physician_endpoint.status_code == 200


def test_deny_physician_endpoint_returns_message():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_from_deny_physician_endpoint = client.post(
            f"/admin/deny-physician/{pytest.a_physician_uid}",
            headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
        )

    assert (
        response_from_deny_physician_endpoint.json()["message"]
        == "Physician denied successfully"
    )


def test_deny_physician_endpoint_updates_approved_field_in_firestore():
    assert (
        db.collection("physicians")
        .document(pytest.a_physician_uid)
        .get()
        .to_dict()["approved"]
        == "approved"
    )
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            f"/admin/deny-physician/{pytest.a_physician_uid}",
            headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
        )
    assert (
        db.collection("deniedPhysicians")
        .document(pytest.a_physician_uid)
        .get()
        .to_dict()["approved"]
        == "denied"
    )


def test_deny_physician_endpoint_updates_firestore_collections():
    # Verifica que el médico esté inicialmente en la colección "physicians" con el estado "pending"
    physician_ref = db.collection("physicians").document(pytest.a_physician_uid)
    physician_data = physician_ref.get().to_dict()
    assert physician_data is not None
    assert physician_data["approved"] == "approved"

    # Realiza la solicitud para denegar al médico
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            f"/admin/deny-physician/{pytest.a_physician_uid}",
            headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
        )

    # Verifica que el médico ya no esté en la colección "physicians" y su estado sea "denied"
    physician_data = physician_ref.get().to_dict()
    assert physician_data is None

    # Verifica que el médico haya sido agregado a la colección "deniedPhysicians"
    denied_physician_ref = db.collection("deniedPhysicians").document(
        pytest.a_physician_uid
    )
    denied_physician_data = denied_physician_ref.get().to_dict()
    assert denied_physician_data is not None
    assert denied_physician_data["approved"] == "denied"


def test_deny_physician_endpoint_for_a_non_physician_returns_a_400_code_and_message():
    response_from_deny_physician_endpoint = client.post(
        f"/admin/deny-physician/{pytest.a_patient_uid}",
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert response_from_deny_physician_endpoint.status_code == 400
    assert (
        response_from_deny_physician_endpoint.json()["detail"]
        == "Can only deny physicians"
    )


def test_deny_physician_with_no_authorization_header_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        f"/admin/deny-physician/{pytest.a_physician_uid}"
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_deny_physician_with_empty_authorization_header_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        f"/admin/deny-physician/{pytest.a_physician_uid}",
        headers={"Authorization": ""},
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_deny_physician_with_empty_bearer_token_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        f"/admin/deny-physician/{pytest.a_physician_uid}",
        headers={"Authorization": f"Bearer "},
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_deny_physician_with_non_bearer_token_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        f"/admin/deny-physician/{pytest.a_physician_uid}",
        headers={"Authorization": pytest.initial_admin_bearer},
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_deny_physician_with_invalid_bearer_token_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        f"/admin/deny-physician/{pytest.a_physician_uid}",
        headers={"Authorization": "Bearer smth"},
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_deny_physician_by_non_admin_returns_403_code_and_message():
    non_admin_bearer = client.post(
        "/users/login",
        json={
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    ).json()["token"]

    response_from_admin_registration_endpoint = client.post(
        f"/admin/deny-physician/{pytest.a_physician_uid}",
        headers={"Authorization": f"Bearer {non_admin_bearer}"},
    )

    assert response_from_admin_registration_endpoint.status_code == 403
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be an admin"
    )


def test_deny_physicians_endpoint_cancels_physicians_appointments():
    assert (
        db.collection("appointments").document(pytest.appointment_id).get().exists
        == True
    )
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            f"/admin/deny-physician/{pytest.a_physician_uid}",
            headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
        )
    assert (
        db.collection("appointments").document(pytest.appointment_id).get().exists
        == False
    )


def test_deny_physicians_endpoint_triggers_notification():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            f"/admin/deny-physician/{pytest.a_physician_uid}",
            headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
        )

    assert mocked_request.call_count == 2
