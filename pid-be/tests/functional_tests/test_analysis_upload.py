import pytest
from firebase_admin import firestore, auth
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock


client = TestClient(app)
db = firestore.client()

a_KMK_patient_information = {
    "role": "patient",
    "name": "Patient Test User Register",
    "last_name": "Test Last Name",
    "email": "testpatientforapproving@kmk.com",
    "password": "verySecurePassword123",
    "birth_date": "9/1/2000",
    "gender": "m",
    "blood_type": "a",
}

a_KMK_physician_information = {
    "role": "physician",
    "first_name": "Physician Test User Register 1",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": "surgeon",
    "email": "testphysicianforapproving@kmk.com",
    "approved": "pending",
    "agenda": {"1": {"start": 8, "finish": 18.5}},
}

an_analysis_response_mock = {
    "id": "an_id",
    "file_name": "a_name",
    "uploaded_at": 123456,
    "url": "http://test.test",
}

another_analysis_response_mock = {
    "id": "another_id",
    "file_name": "another_name",
    "uploaded_at": 123456,
    "url": "http://test.test",
}


@pytest.fixture(scope="module", autouse=True)
def load_and_delete_specialties():
    id = db.collection("specialties").document().id
    db.collection("specialties").document(id).set(
        {"id": id, "name": "surgeon", "value": 3500}
    )
    yield
    specilaties_doc = db.collection("specialties").list_documents()
    for specialty_doc in specilaties_doc:
        specialty_doc.delete()


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
def log_in_patient(create_test_patient_and_then_delete_him):
    pytest.patients_bearer_token = client.post(
        "/users/login",
        json={
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    ).json()["token"]
    yield


@pytest.fixture(scope="module", autouse=True)
def create_test_physician_and_then_delete_him():
    created_user = auth.create_user(
        **{
            "email": a_KMK_physician_information["email"],
            "password": "verySecurePassword123",
        }
    )
    pytest.a_physician_uid = created_user.uid
    db.collection("physicians").document(pytest.a_physician_uid).set(
        {
            **a_KMK_physician_information,
            "approved": "approved",
            "id": pytest.a_physician_uid,
        }
    )
    yield
    auth.delete_user(pytest.a_physician_uid)
    db.collection("physicians").document(pytest.a_physician_uid).delete()


@pytest.fixture(scope="module", autouse=True)
def log_in_physician(create_test_physician_and_then_delete_him):
    pytest.physicians_bearer_token = client.post(
        "/users/login",
        json={
            "email": a_KMK_physician_information["email"],
            "password": "verySecurePassword123",
        },
    ).json()["token"]
    yield


@patch("app.routers.analysis.Analysis")
def test_uploading_analysis_returns_201_code(mock_analysis_save):
    response_mock = AsyncMock()
    response_mock.save.return_value = [an_analysis_response_mock]
    mock_analysis_save.return_value = response_mock

    files = {"analysis": open("tests/functional_tests/test_files/test_file.txt", "rb")}
    response_from_analysis_upload_endpoint = client.post(
        "/analysis",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
        files=files,
    )
    assert response_from_analysis_upload_endpoint.status_code == 201


@patch("app.routers.analysis.Analysis")
def test_uploading_analysis_returns_list_with_upload_info(mock_analysis_save):
    response_mock = AsyncMock()
    response_mock.save.return_value = [an_analysis_response_mock]
    mock_analysis_save.return_value = response_mock

    files = {"analysis": open("tests/functional_tests/test_files/test_file.txt", "rb")}
    response_from_analysis_upload_endpoint = client.post(
        "/analysis",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
        files=files,
    )

    assert type(response_from_analysis_upload_endpoint.json()) == list
    assert len(response_from_analysis_upload_endpoint.json()) == 1
    analysis_information = response_from_analysis_upload_endpoint.json()[0]
    assert type(analysis_information["id"]) == str
    assert type(analysis_information["file_name"]) == str
    assert type(analysis_information["uploaded_at"]) == int
    assert type(analysis_information["url"]) == str


@patch("app.routers.analysis.Analysis")
def test_multiple_upload_returns_many_response_elements(mock_analysis_save):
    response_mock = AsyncMock()
    response_mock.save.return_value = [
        an_analysis_response_mock,
        another_analysis_response_mock,
    ]
    mock_analysis_save.return_value = response_mock

    a_file = (
        "analysis",
        open("tests/functional_tests/test_files/test_file.txt", "rb"),
    )

    another_file = (
        "analysis",
        open("tests/functional_tests/test_files/another_test_file.txt", "rb"),
    )
    response_from_analysis_upload_endpoint = client.post(
        "/analysis",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
        files=[a_file, another_file],
    )

    assert len(response_from_analysis_upload_endpoint.json()) == 2


def test_sending_no_files_to_upload_analysis_returns_422_code():
    response_from_analysis_upload_endpoint = client.post(
        "/analysis",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
    )
    assert response_from_analysis_upload_endpoint.status_code == 422


def test_upload_analysis_with_no_authorization_header_returns_401_code():
    response_from_analysis_upload_endpoint = client.post("/analysis")

    assert response_from_analysis_upload_endpoint.status_code == 401
    assert (
        response_from_analysis_upload_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_upload_analysis_with_empty_authorization_header_returns_401_code():
    response_from_analysis_upload_endpoint = client.post(
        "/analysis",
        headers={"Authorization": ""},
    )

    assert response_from_analysis_upload_endpoint.status_code == 401
    assert (
        response_from_analysis_upload_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_upload_analysis_with_empty_bearer_token_returns_401_code():
    response_from_analysis_upload_endpoint = client.post(
        "/analysis",
        headers={"Authorization": f"Bearer "},
    )

    assert response_from_analysis_upload_endpoint.status_code == 401
    assert (
        response_from_analysis_upload_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_upload_analysis_with_non_bearer_token_returns_401_code():
    response_from_analysis_upload_endpoint = client.post(
        "/analysis",
        headers={"Authorization": pytest.patients_bearer_token},
    )

    assert response_from_analysis_upload_endpoint.status_code == 401
    assert (
        response_from_analysis_upload_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_upload_analysis_with_invalid_bearer_token_returns_401_code():
    response_from_analysis_upload_endpoint = client.post(
        "/analysis",
        headers={"Authorization": "Bearer smth"},
    )

    assert response_from_analysis_upload_endpoint.status_code == 401
    assert (
        response_from_analysis_upload_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_physician_uploading_file_returns_403_code_with_detail():
    files = {"analysis": open("tests/functional_tests/test_files/test_file.txt", "rb")}
    response_from_analysis_upload_endpoint = client.post(
        "/analysis",
        headers={"Authorization": f"Bearer {pytest.physicians_bearer_token}"},
        files=files,
    )
    assert response_from_analysis_upload_endpoint.status_code == 403
    assert (
        response_from_analysis_upload_endpoint.json()["detail"]
        == "User must be a patient to upload analysis"
    )
