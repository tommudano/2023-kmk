import pytest
from firebase_admin import auth, firestore
from app.main import app
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import os
from dotenv import load_dotenv

load_dotenv()

initial_value = 3500

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

a_KMK_user_information = {
    "display_name": "KMK Test User",
    "email": "getPhysiciansBySpecialtyTestUser@kmk.com",
    "email_verified": True,
    "password": "verySecurePassword123",
}

initial_admin_information = {
    "email": "testinitialadminfordenial@kmk.com",
    "password": "verySecurePassword123",
}

a_KMK_physician_information = {
    "role": "physician",
    "first_name": "Physician Test User Register 1",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": specialties[0],
    "email": "testphysicianfordenial@kmk.com",
    "approved": "approved",
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


@pytest.fixture(scope="module", autouse=True)
def load_and_delete_specialties():
    for specialty in specialties:
        id = db.collection("specialties").document().id
        db.collection("specialties").document(id).set(
            {"id": id, "name": specialty, "value": initial_value}
        )
    yield
    specilaties_doc = db.collection("specialties").list_documents()
    for specialty_doc in specilaties_doc:
        specialty_doc.delete()


@pytest.fixture(scope="module", autouse=True)
def create_initial_admin_and_then_delete_him():
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
def create_test_user(log_in_initial_admin_user):
    pytest.user_id = auth.create_user(**a_KMK_user_information).uid
    yield
    auth.delete_user(pytest.user_id)


@pytest.fixture(scope="module", autouse=True)
def login_test_user(create_test_user):
    pytest.user_bearer = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    ).json()["token"]
    yield


@pytest.fixture(autouse=True)
def create_a_physician_and_then_delete_him():
    created_user = auth.create_user(
        **{
            "email": a_KMK_physician_information["email"],
            "password": "verySecurePassword123",
        }
    )
    pytest.a_physician_uid = created_user.uid
    db.collection("physicians").document(pytest.a_physician_uid).set(
        {**a_KMK_physician_information, "id": pytest.a_physician_uid}
    )
    yield
    try:
        auth.delete_user(pytest.a_physician_uid)
        db.collection("physicians").document(pytest.a_physician_uid).delete()
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


@patch("app.routers.admin.requests.post")
def test_put_to_update_value_endpoint_returns_200_code(mock_notifications_api):
    response_from_specialty_value_update_endpoint = client.put(
        f"/admin/specialties/value/{specialties[0]}",
        json={"value": 4000},
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert response_from_specialty_value_update_endpoint.status_code == 200


@patch("app.routers.admin.requests.post")
def test_put_to_update_value_endpoint_returns_successfull_message(
    mock_notifications_api,
):
    response_from_specialty_value_update_endpoint = client.put(
        f"/admin/specialties/value/{specialties[0]}",
        json={"value": 4000},
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert (
        response_from_specialty_value_update_endpoint.json()["message"]
        == "Valor actualizado correctamente"
    )


@patch("app.routers.admin.requests.post")
def test_put_to_updates_value_in_firestore(mock_notifications_api):
    specialty_doc = (
        db.collection("specialties")
        .where("name", "==", specialties[1])
        .get()[0]
        .to_dict()
    )
    specialty_id = specialty_doc["id"]
    assert specialty_doc["value"] == initial_value

    client.put(
        f"/admin/specialties/value/{specialties[1]}",
        json={"value": 4000},
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    updated_specialty_doc = (
        db.collection("specialties").document(specialty_id).get().to_dict()
    )
    assert updated_specialty_doc["value"] == 4000


def test_put_to_update_value_endpoint_with_negative_value_returns_422_code():
    response_from_specialty_value_update_endpoint = client.put(
        f"/admin/specialties/value/{specialties[0]}",
        json={"value": -4000},
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert response_from_specialty_value_update_endpoint.status_code == 422


def test_put_to_update_value_endpoint_with_float_value_returns_422_code():
    response_from_specialty_value_update_endpoint = client.put(
        f"/admin/specialties/value/{specialties[0]}",
        json={"value": 4000.1},
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert response_from_specialty_value_update_endpoint.status_code == 422


def test_put_to_update_value_endpoint_with_no_authorization_header_returns_401_code():
    response_from_specialty_value_update_endpoint = client.put(
        f"/admin/specialties/value/{specialties[0]}", json={"value": 4000}
    )

    assert response_from_specialty_value_update_endpoint.status_code == 401
    assert (
        response_from_specialty_value_update_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_put_to_update_value_endpoint_with_empty_authorization_header_returns_401_code():
    response_from_specialty_value_update_endpoint = client.put(
        f"/admin/specialties/value/{specialties[0]}",
        json={"value": 4000},
        headers={"Authorization": ""},
    )

    assert response_from_specialty_value_update_endpoint.status_code == 401
    assert (
        response_from_specialty_value_update_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_put_to_update_value_endpoint_with_empty_bearer_token_returns_401_code():
    response_from_specialty_value_update_endpoint = client.put(
        f"/admin/specialties/value/{specialties[0]}",
        json={"value": 4000},
        headers={"Authorization": f"Bearer "},
    )

    assert response_from_specialty_value_update_endpoint.status_code == 401
    assert (
        response_from_specialty_value_update_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_put_to_update_value_endpoint_with_non_bearer_token_returns_401_code():
    response_from_specialty_value_update_endpoint = client.put(
        f"/admin/specialties/value/{specialties[0]}",
        json={"value": 4000},
        headers={"Authorization": pytest.initial_admin_bearer},
    )

    assert response_from_specialty_value_update_endpoint.status_code == 401
    assert (
        response_from_specialty_value_update_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_put_to_update_value_endpoint_with_invalid_bearer_token_returns_401_code():
    response_from_specialty_value_update_endpoint = client.put(
        f"/admin/specialties/value/{specialties[0]}",
        json={"value": 4000},
        headers={"Authorization": "Bearer smth"},
    )

    assert response_from_specialty_value_update_endpoint.status_code == 401
    assert (
        response_from_specialty_value_update_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_put_to_update_value_endpoint_by_non_admin_returns_403_code():
    response_from_specialty_value_update_endpoint = client.put(
        f"/admin/specialties/value/{specialties[0]}",
        json={"value": 4000},
        headers={"Authorization": f"Bearer {pytest.user_bearer}"},
    )

    assert response_from_specialty_value_update_endpoint.status_code == 403


@patch("app.routers.admin.requests.post")
def test_put_to_update_value_endpoint_for_first_specialty_triggers_two_emails(
    mock_notifications_api,
):
    client.put(
        f"/admin/specialties/value/{specialties[0]}",
        json={"value": 4000},
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert mock_notifications_api.call_count == 2


@patch("app.routers.admin.requests.post")
def test_put_to_update_value_endpoint_for_second_specialty_triggers_no_emails(
    mock_notifications_api,
):
    client.put(
        f"/admin/specialties/value/{specialties[1]}",
        json={"value": 4000},
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert mock_notifications_api.call_count == 0
