import pytest
from firebase_admin import firestore, auth, storage
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, Mock


client = TestClient(app)
db = firestore.client()

a_KMK_patient_information = {
    "role": "patient",
    "name": "Patient Test User Register",
    "last_name": "Test Last Name",
    "email": "testpatientforanalysisdeletion@kmk.com",
    "password": "verySecurePassword123",
    "birth_date": "9/1/2000",
    "gender": "m",
    "blood_type": "a",
}


another_KMK_patient_information = {
    "role": "patient",
    "name": "Patient Test User Register",
    "last_name": "Test Last Name",
    "email": "testpatientforanalysisdeletion2@kmk.com",
    "password": "verySecurePassword123",
    "birth_date": "9/1/2000",
    "gender": "m",
    "blood_type": "a",
}


@pytest.fixture(scope="module", autouse=True)
def create_test_patient_and_then_delete_him():
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
def create_another_est_patient_and_then_delete_him(
    create_test_patient_and_then_delete_him,
):
    created_user = auth.create_user(
        **{
            "email": another_KMK_patient_information["email"],
            "password": another_KMK_patient_information["password"],
        }
    )
    pytest.another_patient_uid = created_user.uid
    db.collection("patients").document(pytest.another_patient_uid).set(
        another_KMK_patient_information
    )
    yield
    auth.delete_user(pytest.another_patient_uid)
    db.collection("patients").document(pytest.another_patient_uid).delete()


@pytest.fixture(scope="module", autouse=True)
def log_in_patient(create_another_est_patient_and_then_delete_him):
    pytest.patients_bearer_token = client.post(
        "/users/login",
        json={
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    ).json()["token"]
    yield


@pytest.fixture(scope="module", autouse=True)
def log_in_another_patient(log_in_patient):
    pytest.another_patients_bearer_token = client.post(
        "/users/login",
        json={
            "email": another_KMK_patient_information["email"],
            "password": another_KMK_patient_information["password"],
        },
    ).json()["token"]
    yield


@pytest.fixture(autouse=True)
def add_file_to_storage_and_then_delete_them(log_in_another_patient):
    pytest.analysis_id = "an_analysis_id"
    yield


@patch("app.routers.analysis.Analysis")
def test_valid_deletion_of_analysis_returns_200_code(mock_analysis_delete):
    response_from_analysis_deletion_endpoint = client.delete(
        f"/analysis/{pytest.analysis_id}",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
    )

    assert response_from_analysis_deletion_endpoint.status_code == 200


@patch("app.routers.analysis.Analysis")
def test_valid_deletion_of_analysis_returns_message(mock_analysis_delete):
    response_from_analysis_deletion_endpoint = client.delete(
        f"/analysis/{pytest.analysis_id}",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
    )

    assert (
        response_from_analysis_deletion_endpoint.json()["message"]
        == "Analysis has been deleted successfully"
    )


def test_delete_analysis_with_no_authorization_header_returns_401_code():
    response_from_delete_analysis_endpoint = client.delete(
        f"/analysis/{pytest.analysis_id}"
    )

    assert response_from_delete_analysis_endpoint.status_code == 401
    assert (
        response_from_delete_analysis_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_delete_analysis_with_empty_authorization_header_returns_401_code():
    response_from_delete_analysis_endpoint = client.delete(
        f"/analysis/{pytest.analysis_id}",
        headers={"Authorization": ""},
    )

    assert response_from_delete_analysis_endpoint.status_code == 401
    assert (
        response_from_delete_analysis_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_delete_analysis_with_empty_bearer_token_returns_401_code():
    response_from_delete_analysis_endpoint = client.delete(
        f"/analysis/{pytest.analysis_id}",
        headers={"Authorization": f"Bearer "},
    )

    assert response_from_delete_analysis_endpoint.status_code == 401
    assert (
        response_from_delete_analysis_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_delete_analysis_with_non_bearer_token_returns_401_code():
    response_from_delete_analysis_endpoint = client.delete(
        f"/analysis/{pytest.analysis_id}",
        headers={"Authorization": pytest.patients_bearer_token},
    )

    assert response_from_delete_analysis_endpoint.status_code == 401
    assert (
        response_from_delete_analysis_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_delete_analysis_with_invalid_bearer_token_returns_401_code():
    response_from_delete_analysis_endpoint = client.delete(
        f"/analysis/{pytest.analysis_id}",
        headers={"Authorization": "Bearer smth"},
    )

    assert response_from_delete_analysis_endpoint.status_code == 401
    assert (
        response_from_delete_analysis_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_delete_analysis_endpoint_for_analysis_that_doesnt_belong_to_user_reurns_400_code_and_detail():
    response_from_analysis_deletion_endpoint = client.delete(
        f"/analysis/{pytest.analysis_id}",
        headers={"Authorization": f"Bearer {pytest.another_patients_bearer_token}"},
    )

    assert response_from_analysis_deletion_endpoint.status_code == 400
    assert (
        response_from_analysis_deletion_endpoint.json()["detail"]
        == "The file doesnt exists"
    )


def test_delete_analysis_endpoint_for_analysis_that_doesnt_exist_reurns_400_code_and_detail():
    response_from_analysis_deletion_endpoint = client.delete(
        f"/analysis/inexistantid",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
    )

    assert response_from_analysis_deletion_endpoint.status_code == 400
    assert (
        response_from_analysis_deletion_endpoint.json()["detail"]
        == "The file doesnt exists"
    )
