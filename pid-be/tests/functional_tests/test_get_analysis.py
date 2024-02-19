import pytest
from firebase_admin import firestore, auth
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
    "first_name": "Physician Test User Register 1",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": "surgeon",
    "email": "testphysicianforapproving@kmk.com",
    "approved": "approved",
    "agenda": {"1": {"start": 8, "finish": 18.5}},
}

an_analysis_object = {
    "id": "an_id",
    "file_name": "a_name",
    "uploaded_at": 123456,
    "url": "http://test.test",
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
            "password": "verySecurePassword123",
        }
    )
    pytest.a_phisician_uid = created_user.uid
    db.collection("physicians").document(pytest.a_phisician_uid).set(
        {
            **a_KMK_physician_information,
            "id": pytest.a_phisician_uid,
        }
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
            "password": "verySecurePassword123",
        },
    ).json()["token"]
    yield


@pytest.fixture(scope="module", autouse=True)
def create_document_instance(log_in_patient):
    db.collection("analysis").document(pytest.a_patient_uid).collection(
        "uploaded_analysis"
    ).document(an_analysis_object["id"]).set(an_analysis_object)
    yield
    db.collection("analysis").document(pytest.a_patient_uid).delete()


def test_request_to_get_patients_analysis_returns_a_200_code():

    response_from_get_patients_analysis_endpoint = client.get(
        "/analysis", headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"}
    )

    assert response_from_get_patients_analysis_endpoint.status_code == 200


def test_request_to_get_patients_analysis_returns_a_list():

    response_from_get_patients_analysis_endpoint = client.get(
        "/analysis", headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"}
    )

    assert type(response_from_get_patients_analysis_endpoint.json()) == list


def test_request_to_get_patients_analysis_returns_a_list_of_one_element():

    response_from_get_patients_analysis_endpoint = client.get(
        "/analysis", headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"}
    )

    print("DATA", response_from_get_patients_analysis_endpoint.json())

    assert len(response_from_get_patients_analysis_endpoint.json()) == 1


def test_request_to_get_patients_analysis_returns_a_list_of_one_element():

    response_from_get_patients_analysis_endpoint = client.get(
        "/analysis", headers={"Authorization": f"Bearer {pytest.patients_bearer_token}"}
    )

    assert type(response_from_get_patients_analysis_endpoint.json()[0]["id"]) == str
    assert (
        type(response_from_get_patients_analysis_endpoint.json()[0]["file_name"]) == str
    )
    assert (
        type(response_from_get_patients_analysis_endpoint.json()[0]["uploaded_at"])
        == int
    )
    assert type(response_from_get_patients_analysis_endpoint.json()[0]["url"]) == str


def test_get_analysis_with_no_authorization_header_returns_401_code():
    response_from_get_analysis_endpoint = client.get("/analysis")

    assert response_from_get_analysis_endpoint.status_code == 401
    assert (
        response_from_get_analysis_endpoint.json()["detail"] == "User must be logged in"
    )


def test_get_analysis_with_empty_authorization_header_returns_401_code():
    response_from_get_analysis_endpoint = client.get(
        "/analysis",
        headers={"Authorization": ""},
    )

    assert response_from_get_analysis_endpoint.status_code == 401
    assert (
        response_from_get_analysis_endpoint.json()["detail"] == "User must be logged in"
    )


def test_get_analysis_with_empty_bearer_token_returns_401_code():
    response_from_get_analysis_endpoint = client.get(
        "/analysis",
        headers={"Authorization": f"Bearer "},
    )

    assert response_from_get_analysis_endpoint.status_code == 401
    assert (
        response_from_get_analysis_endpoint.json()["detail"] == "User must be logged in"
    )


def test_get_analysis_with_non_bearer_token_returns_401_code():
    response_from_get_analysis_endpoint = client.get(
        "/analysis",
        headers={"Authorization": pytest.patients_bearer_token},
    )

    assert response_from_get_analysis_endpoint.status_code == 401
    assert (
        response_from_get_analysis_endpoint.json()["detail"] == "User must be logged in"
    )


def test_get_analysis_with_invalid_bearer_token_returns_401_code():
    response_from_get_analysis_endpoint = client.get(
        "/analysis",
        headers={"Authorization": "Bearer smth"},
    )

    assert response_from_get_analysis_endpoint.status_code == 401
    assert (
        response_from_get_analysis_endpoint.json()["detail"] == "User must be logged in"
    )


def test_request_to_get_patients_as_physician_returns_a_403_code_and_detail():
    response_from_get_patients_analysis_endpoint = client.get(
        "/analysis",
        headers={"Authorization": f"Bearer { pytest.physicians_bearer_token}"},
    )

    assert response_from_get_patients_analysis_endpoint.status_code == 403
    assert (
        response_from_get_patients_analysis_endpoint.json()["detail"]
        == "Only patients can view their analysis"
    )


def test_request_to_get_patients_analysis_as_physician_returns_a_200_code():

    response_from_get_patients_analysis_endpoint = client.get(
        f"/analysis/{pytest.a_patient_uid}",
        headers={"Authorization": f"Bearer {pytest.physicians_bearer_token}"},
    )

    assert response_from_get_patients_analysis_endpoint.status_code == 200


def test_request_to_get_patients_analysis_as_physician_returns_a_list():

    response_from_get_patients_analysis_endpoint = client.get(
        f"/analysis/{pytest.a_patient_uid}",
        headers={"Authorization": f"Bearer {pytest.physicians_bearer_token}"},
    )

    assert type(response_from_get_patients_analysis_endpoint.json()) == list


def test_request_to_get_patients_analysis_as_physician_returns_a_list_of_one_element():

    response_from_get_patients_analysis_endpoint = client.get(
        f"/analysis/{pytest.a_patient_uid}",
        headers={"Authorization": f"Bearer {pytest.physicians_bearer_token}"},
    )

    assert len(response_from_get_patients_analysis_endpoint.json()) == 1


def test_request_to_get_patients_analysis_as_physician_returns_a_list_of_one_element():

    response_from_get_patients_analysis_endpoint = client.get(
        f"/analysis/{pytest.a_patient_uid}",
        headers={"Authorization": f"Bearer {pytest.physicians_bearer_token}"},
    )

    print(response_from_get_patients_analysis_endpoint.json())

    assert type(response_from_get_patients_analysis_endpoint.json()[0]["id"]) == str
    assert (
        type(response_from_get_patients_analysis_endpoint.json()[0]["file_name"]) == str
    )
    assert (
        type(response_from_get_patients_analysis_endpoint.json()[0]["uploaded_at"])
        == int
    )
    assert type(response_from_get_patients_analysis_endpoint.json()[0]["url"]) == str


def test_get_analysis_with_no_authorization_header_returns_401_code():
    response_from_get_analysis_endpoint = client.get(
        f"/analysis/{pytest.a_patient_uid}"
    )

    assert response_from_get_analysis_endpoint.status_code == 401
    assert (
        response_from_get_analysis_endpoint.json()["detail"] == "User must be logged in"
    )


def test_get_analysis_with_empty_authorization_header_returns_401_code():
    response_from_get_analysis_endpoint = client.get(
        f"/analysis/{pytest.a_patient_uid}",
        headers={"Authorization": ""},
    )

    assert response_from_get_analysis_endpoint.status_code == 401
    assert (
        response_from_get_analysis_endpoint.json()["detail"] == "User must be logged in"
    )


def test_get_analysis_with_empty_bearer_token_returns_401_code():
    response_from_get_analysis_endpoint = client.get(
        f"/analysis/{pytest.a_patient_uid}",
        headers={"Authorization": f"Bearer "},
    )

    assert response_from_get_analysis_endpoint.status_code == 401
    assert (
        response_from_get_analysis_endpoint.json()["detail"] == "User must be logged in"
    )


def test_get_analysis_with_non_bearer_token_returns_401_code():
    response_from_get_analysis_endpoint = client.get(
        f"/analysis/{pytest.a_patient_uid}",
        headers={"Authorization": pytest.patients_bearer_token},
    )

    assert response_from_get_analysis_endpoint.status_code == 401
    assert (
        response_from_get_analysis_endpoint.json()["detail"] == "User must be logged in"
    )


def test_get_analysis_with_invalid_bearer_token_returns_401_code():
    response_from_get_analysis_endpoint = client.get(
        f"/analysis/{pytest.a_patient_uid}",
        headers={"Authorization": "Bearer smth"},
    )

    assert response_from_get_analysis_endpoint.status_code == 401
    assert (
        response_from_get_analysis_endpoint.json()["detail"] == "User must be logged in"
    )


def test_request_to_get_a_specific_patients_analysis_as_patient_returns_a_403_code_and_detail():
    response_from_get_patients_analysis_endpoint = client.get(
        f"/analysis/{pytest.a_patient_uid}",
        headers={"Authorization": f"Bearer { pytest.patients_bearer_token}"},
    )

    assert response_from_get_patients_analysis_endpoint.status_code == 403
    assert (
        response_from_get_patients_analysis_endpoint.json()["detail"]
        == "Only physicians can view their analysis"
    )
