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
    "email": "testpatientforapproving@kmk.com",
    "password": "verySecurePassword123",
    "birth_date": "9/1/2000",
    "gender": "m",
    "blood_type": "a",
}

a_KMK_physician_information = {
    "role": "physician",
    "name": "Physician Test User Register 1",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": "surgeon",
    "email": "testphysicianforapproving@kmk.com",
    "password": "verySecurePassword123",
    "approved": "pending",
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
            "password": a_KMK_physician_information["password"],
        }
    )
    pytest.a_phisician_uid = created_user.uid
    db.collection("physicians").document(pytest.a_phisician_uid).set(
        {**a_KMK_physician_information, "approved": "approved"}
    )
    yield
    auth.delete_user(pytest.a_phisician_uid)
    db.collection("physicians").document(pytest.a_phisician_uid).delete()


@pytest.fixture(scope="module", autouse=True)
def log_in_physician(create_test_physician_and_then_delete_him):
    pytest.physicians_bearer_token = client.post(
        "/users/login",
        json={
            "email": a_KMK_physician_information["email"],
            "password": a_KMK_physician_information["password"],
        },
    ).json()["token"]
    yield


@pytest.fixture(autouse=True)
def delete_storage_documents():
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


def test_uploading_analysis_returns_201_code():
    files = {"analysis": open("tests/test_files/test_file.txt", "rb")}
    response_from_analysis_upload_endpoint = client.post(
        "/analysis",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
        files=files,
    )
    assert response_from_analysis_upload_endpoint.status_code == 201


def test_uploading_analysis_returns_list_with_upload_info():
    files = {"analysis": open("tests/test_files/test_file.txt", "rb")}
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


def test_uploading_analysis_saves_file_in_storage():
    bucket = storage.bucket()
    uploaded_files = list(bucket.list_blobs(prefix=f"analysis/{pytest.a_patient_uid}"))
    assert len(uploaded_files) == 0
    files = {"analysis": open("tests/test_files/test_file.txt", "rb")}
    client.post(
        "/analysis",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
        files=files,
    )
    uploaded_files = list(bucket.list_blobs(prefix=f"analysis/{pytest.a_patient_uid}"))
    assert len(uploaded_files) == 1


def test_uploading_analysis_saves_file_in_firestore():
    assert (
        len(
            db.collection("analysis")
            .document(pytest.a_patient_uid)
            .collection("uploaded_analysis")
            .get()
        )
        == 0
    )
    files = {"analysis": open("tests/test_files/test_file.txt", "rb")}
    response_from_analysis_upload_endpoint = client.post(
        "/analysis",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
        files=files,
    )
    file_collection = (
        db.collection("analysis")
        .document(pytest.a_patient_uid)
        .collection("uploaded_analysis")
        .get()
    )
    assert len(file_collection) == 1
    file_doc = file_collection[0].to_dict()
    assert file_doc["id"] == response_from_analysis_upload_endpoint.json()[0]["id"]
    assert (
        file_doc["file_name"]
        == response_from_analysis_upload_endpoint.json()[0]["file_name"]
    )
    assert (
        file_doc["uploaded_at"]
        == response_from_analysis_upload_endpoint.json()[0]["uploaded_at"]
    )
    assert file_doc["url"] == response_from_analysis_upload_endpoint.json()[0]["url"]


def test_multiple_upload_returns_many_response_elements():
    a_file = (
        "analysis",
        open("tests/test_files/test_file.txt", "rb"),
    )

    another_file = (
        "analysis",
        open("tests/test_files/another_test_file.txt", "rb"),
    )
    response_from_analysis_upload_endpoint = client.post(
        "/analysis",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
        files=[a_file, another_file],
    )

    assert len(response_from_analysis_upload_endpoint.json()) == 2


def test_uploading_files_with_same_name_doesnt_override():
    a_file = (
        "analysis",
        open("tests/test_files/test_file.txt", "rb"),
    )

    another_file = (
        "analysis",
        open("tests/test_files/test_file.txt", "rb"),
    )
    client.post(
        "/analysis",
        headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"},
        files=[a_file, another_file],
    )

    bucket = storage.bucket()
    uploaded_files = list(bucket.list_blobs(prefix=f"analysis/{pytest.a_patient_uid}"))
    assert len(uploaded_files) == 2


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
    files = {"analysis": open("tests/test_files/test_file.txt", "rb")}
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
