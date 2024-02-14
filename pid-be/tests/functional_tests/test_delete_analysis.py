import pytest
from firebase_admin import firestore, auth, storage
from fastapi.testclient import TestClient
from app.main import app

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
    files = {"analysis": open("tests/test_files/test_file.txt", "rb")}
    response_from_analysis_creation_endpoint = client.post(
        "/analysis",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
        files=files,
    )
    pytest.analysis_id = response_from_analysis_creation_endpoint.json()[0]["id"]
    yield


@pytest.fixture(scope="module", autouse=True)
def add_another_file_to_storage_and_then_delete_them(log_in_another_patient):
    files = {"analysis": open("tests/test_files/test_file.txt", "rb")}
    response_from_analysis_creation_endpoint = client.post(
        "/analysis",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
        files=files,
    )
    yield


@pytest.fixture(scope="module", autouse=True)
def delete_files_from_storage(log_in_another_patient):
    yield
    bucket = storage.bucket()
    blobs = bucket.list_blobs(prefix=f"analysis/{pytest.a_patient_uid}")
    for blob in blobs:
        blob.delete()
    for file_information_doc in (
        db.collection("analysis")
        .document(pytest.a_patient_uid)
        .collection("uploaded_analysis")
        .list_documents()
    ):
        file_information_doc.delete()
    db.collection("analysis").document(pytest.a_patient_uid).delete()


def test_valid_deletion_of_analysis_returns_200_code():
    response_from_analysis_deletion_endpoint = client.delete(
        f"/analysis/{pytest.analysis_id}",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
    )

    assert response_from_analysis_deletion_endpoint.status_code == 200


def test_valid_deletion_of_analysis_returns_message():
    response_from_analysis_deletion_endpoint = client.delete(
        f"/analysis/{pytest.analysis_id}",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
    )

    assert (
        response_from_analysis_deletion_endpoint.json()["message"]
        == "Analysis has been deleted successfully"
    )


def test_analysis_deletion_endpoint_removes_analysis_from_storage():
    bucket = storage.bucket()
    uploaded_files = list(bucket.list_blobs(prefix=f"analysis/{pytest.a_patient_uid}"))
    assert len(uploaded_files) == 2
    uploaded_file = list(
        bucket.list_blobs(
            prefix=f"analysis/{pytest.a_patient_uid}/{pytest.analysis_id}"
        )
    )
    assert len(uploaded_file) == 1
    client.delete(
        f"/analysis/{pytest.analysis_id}",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
    )
    uploaded_files = list(bucket.list_blobs(prefix=f"analysis/{pytest.a_patient_uid}"))
    assert len(uploaded_files) == 1
    uploaded_file = list(
        bucket.list_blobs(
            prefix=f"analysis/{pytest.a_patient_uid}/{pytest.analysis_id}"
        )
    )
    assert len(uploaded_file) == 0


def test_analysis_deletion_endpoint_removes_analysis_from_firestore():
    assert (
        db.collection("analysis")
        .document(pytest.a_patient_uid)
        .collection("uploaded_analysis")
        .document(pytest.analysis_id)
        .get()
        .exists
        == True
    )
    client.delete(
        f"/analysis/{pytest.analysis_id}",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
    )
    assert (
        db.collection("analysis")
        .document(pytest.a_patient_uid)
        .collection("uploaded_analysis")
        .document(pytest.analysis_id)
        .get()
        .exists
        == False
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
