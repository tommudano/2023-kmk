import pytest
from firebase_admin import auth, firestore
from app.main import app
from fastapi.testclient import TestClient
import requests
from unittest.mock import patch

client = TestClient(app)

db = firestore.client()

a_KMK_patient_information = {
    "role": "patient",
    "name": "Patient Test User Register",
    "last_name": "Test Last Name",
    "email": "testpatientforisloggedin@kmk.com",
    "password": "verySecurePassword123",
    "birth_date": "9/1/2000",
    "gender": "m",
    "blood_type": "a",
}


@pytest.fixture(autouse=True)
def create_patient_and_then_delete_him():
    created_user = auth.create_user(
        **{
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        }
    )
    pytest.patient_uid = created_user.uid
    db.collection("patients").document(pytest.patient_uid).set(
        a_KMK_patient_information
    )
    yield
    auth.delete_user(pytest.patient_uid)
    db.collection("patients").document(pytest.patient_uid).delete()


@pytest.fixture(autouse=True)
def log_in_patient(create_patient_and_then_delete_him):
    pytest.bearer_token = client.post(
        "/users/login",
        json={
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    ).json()["token"]
    yield


def test_change_password_endpoint_returns_a_200_code():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_from_change_password_endpoint = client.post(
            "/users/change-password",
            json={
                "current_password": a_KMK_patient_information["password"],
                "new_password": "newPassword123456",
            },
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )

    assert response_from_change_password_endpoint.status_code == 200


def test_change_password_endpoint_returns_a_message():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_from_change_password_endpoint = client.post(
            "/users/change-password",
            json={
                "current_password": a_KMK_patient_information["password"],
                "new_password": "newPassword123456",
            },
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )

    assert (
        response_from_change_password_endpoint.json()["message"]
        == "Contraseña cambiada exitosamente"
    )


def test_change_password_endpoint_changes_password_in_authentication():
    new_password = "newPassword123456"
    assert (
        client.post(
            "/users/login",
            json={
                "email": a_KMK_patient_information["email"],
                "password": new_password,
            },
        ).status_code
        == 400
    )
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            "/users/change-password",
            json={
                "current_password": a_KMK_patient_information["password"],
                "new_password": new_password,
            },
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )

    assert (
        client.post(
            "/users/login",
            json={
                "email": a_KMK_patient_information["email"],
                "password": new_password,
            },
        ).status_code
        == 200
    )


def test_change_password_endpoint_throws_a_422_if_new_password_has_less_that_8_characters():
    response_from_change_password_endpoint = client.post(
        "/users/change-password",
        json={
            "current_password": a_KMK_patient_information["password"],
            "new_password": "nePa6",
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    response_from_change_password_endpoint.status_code == 422


def test_change_password_endpoint_throws_a_422_if_new_password_has_no_uppercases():
    response_from_change_password_endpoint = client.post(
        "/users/change-password",
        json={
            "current_password": a_KMK_patient_information["password"],
            "new_password": "password123456",
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    response_from_change_password_endpoint.status_code == 422


def test_change_password_endpoint_throws_a_422_if_new_password_has_no_lowercases():
    response_from_change_password_endpoint = client.post(
        "/users/change-password",
        json={
            "current_password": a_KMK_patient_information["password"],
            "new_password": "PASSWORD123456",
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    response_from_change_password_endpoint.status_code == 422


def test_change_password_endpoint_throws_a_422_if_new_password_has_no_numbers():
    response_from_change_password_endpoint = client.post(
        "/users/change-password",
        json={
            "current_password": a_KMK_patient_information["password"],
            "new_password": "PASSWORDabc",
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    response_from_change_password_endpoint.status_code == 422


def test_change_password_with_no_authorization_header_returns_401_code():
    response_from_change_password_endpoint = client.post("/users/change-password")

    assert response_from_change_password_endpoint.status_code == 401
    assert (
        response_from_change_password_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_change_password_with_empty_authorization_header_returns_401_code():
    response_from_change_password_endpoint = client.post(
        "/users/change-password",
        headers={"Authorization": ""},
    )

    assert response_from_change_password_endpoint.status_code == 401
    assert (
        response_from_change_password_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_change_password_with_empty_bearer_token_returns_401_code():
    response_from_change_password_endpoint = client.post(
        "/users/change-password",
        headers={"Authorization": f"Bearer "},
    )

    assert response_from_change_password_endpoint.status_code == 401
    assert (
        response_from_change_password_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_change_password_with_non_bearer_token_returns_401_code():
    response_from_change_password_endpoint = client.post(
        "/users/change-password",
        headers={"Authorization": pytest.bearer_token},
    )

    assert response_from_change_password_endpoint.status_code == 401
    assert (
        response_from_change_password_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_change_password_with_invalid_bearer_token_returns_401_code():
    response_from_change_password_endpoint = client.post(
        "/users/change-password",
        headers={"Authorization": "Bearer smth"},
    )

    assert response_from_change_password_endpoint.status_code == 401
    assert (
        response_from_change_password_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_change_password_endpoint_returns_a_400_code_and_message_if_current_password_is_invalid():
    response_from_change_password_endpoint = client.post(
        "/users/change-password",
        json={
            "current_password": "notCurrentPassword",
            "new_password": "newPassword123456",
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_from_change_password_endpoint.status_code == 400
    assert (
        response_from_change_password_endpoint.json()["detail"]
        == "Contraseña actual incorrecta"
    )


def test_change_password_endpoint_triggers_notification():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            "/users/change-password",
            json={
                "current_password": a_KMK_patient_information["password"],
                "new_password": "newPassword123456",
            },
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )

    assert mocked_request.call_count == 2
