import pytest
from firebase_admin import auth, firestore
from app.main import app
from fastapi.testclient import TestClient

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


@pytest.fixture(scope="module", autouse=True)
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


@pytest.fixture(scope="module", autouse=True)
def log_in_patient(create_patient_and_then_delete_him):
    pytest.bearer_token = client.post(
        "/users/login",
        json={
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    ).json()["token"]
    yield


def test_is_logged_in_endpoint_returns_a_200_code():
    response_from_is_logged_in_endpoint = client.get(
        "/users/is-logged-in",
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_from_is_logged_in_endpoint.status_code == 200


def test_user_with_valid_bearer_is_logged_in():
    response_from_is_logged_in_endpoint = client.get(
        "/users/is-logged-in",
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_from_is_logged_in_endpoint.json()["is_logged_in"] == True


def test_user_with_no_bearer_is_not_logged_in():
    response_from_is_logged_in_endpoint = client.get("/users/is-logged-in")

    assert response_from_is_logged_in_endpoint.json()["is_logged_in"] == False


def test_user_with_invalid_bearer_is_logged_in():
    response_from_is_logged_in_endpoint = client.get(
        "/users/is-logged-in",
        headers={"Authorization": f"Bearer invalid"},
    )

    assert response_from_is_logged_in_endpoint.json()["is_logged_in"] == False
