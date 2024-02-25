import pytest
from firebase_admin import auth, firestore
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
    "first_name": "Physician Test User Register",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": specialties[0],
    "email": "testphysicianforregister@kmk.com",
    "password": "verySecurePassword123",
}


another_KMK_physician_information = {
    "role": "physician",
    "first_name": "Physician Test User Register",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": specialties[0],
    "email": "userforphysicianandpatient@kmk.com",
    "password": "verySecurePassword123",
}


a_KMK_patient_information = {
    "role": "patient",
    "first_name": "Patient Test User Register",
    "last_name": "Test Last Name",
    "email": "testpatientforregister@kmk.com",
    "password": "verySecurePassword123",
    "birth_date": "9/1/2000",
    "gender": "m",
    "blood_type": "a",
}

another_KMK_patient_information = {
    "role": "patient",
    "first_name": "Patient Test User Register",
    "last_name": "Test Last Name",
    "email": "userforphysicianandpatient@kmk.com",
    "password": "verySecurePassword123",
    "birth_date": "9/1/2000",
    "gender": "m",
    "blood_type": "a",
}


@pytest.fixture(autouse=True)
def delete_test_patients():
    yield
    try:
        created_test_user_uid = auth.get_user_by_email(
            a_KMK_patient_information["email"]
        ).uid
        auth.delete_user(created_test_user_uid)
        db.collection("patients").document(created_test_user_uid).delete()
    except:
        print("[+] Patient doesnt exist")


@pytest.fixture(autouse=True)
def delete_test_physicians():
    yield
    try:
        created_test_user_uid = auth.get_user_by_email(
            a_KMK_physician_information["email"]
        ).uid
        auth.delete_user(created_test_user_uid)
        db.collection("physicians").document(created_test_user_uid).delete()
    except:
        print("[+] Physician doesnt exist")


@pytest.fixture(scope="module", autouse=True)
def load_and_delete_specialties():
    for specialty in specialties:
        id = db.collection("specialties").document().id
        db.collection("specialties").document(id).set(
            {"id": id, "name": specialty, "value": 3500}
        )
    yield
    specilaties_doc = db.collection("specialties").list_documents()
    for specialty_doc in specilaties_doc:
        specialty_doc.delete()


def test_register_patient_returns_a_201_code():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_to_register_endpoint = client.post(
            "/users/register",
            json=a_KMK_patient_information,
        )

    assert response_to_register_endpoint.status_code == 201


def test_register_patient_returns_a_message():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_to_register_endpoint = client.post(
            "/users/register",
            json=a_KMK_patient_information,
        )

    assert response_to_register_endpoint.json()["message"] == "Successfull registration"


def test_register_patient_creates_record_in_authentication():
    with pytest.raises(Exception):
        auth.get_user_by_email(a_KMK_patient_information["email"])
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            "/users/register",
            json=a_KMK_patient_information,
        )
    assert auth.get_user_by_email(a_KMK_patient_information["email"]) != None


def test_register_patient_creates_record_in_firestore():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            "/users/register",
            json=a_KMK_patient_information,
        )
    created_users_uid = auth.get_user_by_email(a_KMK_patient_information["email"]).uid
    assert db.collection("patients").document(created_users_uid).get().exists == True


def test_register_patient_sets_information_object_in_firestore():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            "/users/register",
            json=a_KMK_patient_information,
        )
    created_users_uid = auth.get_user_by_email(a_KMK_patient_information["email"]).uid
    patient_object_from_firestore = (
        db.collection("patients").document(created_users_uid).get().to_dict()
    )
    assert type(patient_object_from_firestore["id"]) == str
    assert (
        patient_object_from_firestore["first_name"]
        == a_KMK_patient_information["first_name"]
    )
    assert (
        patient_object_from_firestore["last_name"]
        == a_KMK_patient_information["last_name"]
    )
    assert patient_object_from_firestore["email"] == a_KMK_patient_information["email"]


def test_register_patient_twice_returns_a_400_code():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        first_register_patient = client.post(
            "/users/register",
            json=a_KMK_patient_information,
        )

    second_register_patient = client.post(
        "/users/register",
        json=a_KMK_patient_information,
    )

    assert first_register_patient.status_code == 201
    assert second_register_patient.status_code == 400
    assert second_register_patient.json()["detail"] == "Esta cuenta ya fue registrada"


def test_register_patient_with_empty_name_returns_a_422_code():
    register_patient_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_patient_information["role"],
            "first_name": "",
            "last_name": a_KMK_patient_information["last_name"],
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    )

    assert register_patient_response.status_code == 422


def test_register_patient_with_non_string_name_returns_a_422_code():
    register_patient_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_patient_information["role"],
            "first_name": 123456,
            "last_name": a_KMK_patient_information["last_name"],
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    )

    assert register_patient_response.status_code == 422


def test_register_patient_with_empty_last_name_returns_a_422_code():
    register_patient_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_patient_information["role"],
            "first_name": a_KMK_patient_information["first_name"],
            "last_name": "",
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    )

    assert register_patient_response.status_code == 422


def test_register_patient_with_non_string_last_name_returns_a_422_code():
    register_patient_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_patient_information["role"],
            "first_name": a_KMK_patient_information["first_name"],
            "last_name": 123456,
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    )

    assert register_patient_response.status_code == 422


def test_register_patient_with_invalid_email_returns_a_422_code():
    register_patient_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_patient_information["role"],
            "first_name": a_KMK_patient_information["first_name"],
            "last_name": a_KMK_patient_information["last_name"],
            "email": "notanemail",
            "password": a_KMK_patient_information["password"],
        },
    )

    assert register_patient_response.status_code == 422


def test_register_patient_with_password_of_less_than_8_characters_returns_a_422_code():
    register_patient_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_patient_information["role"],
            "first_name": a_KMK_patient_information["first_name"],
            "last_name": a_KMK_patient_information["last_name"],
            "email": a_KMK_patient_information["email"],
            "password": "lT8",
            "birth_date": a_KMK_patient_information["birth_date"],
            "gender": a_KMK_patient_information["gender"],
            "blood_type": a_KMK_patient_information["blood_type"],
        },
    )

    assert register_patient_response.status_code == 422


def test_register_patient_with_password_with_no_uppercase_returns_a_422_code():
    register_patient_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_patient_information["role"],
            "first_name": a_KMK_patient_information["first_name"],
            "last_name": a_KMK_patient_information["last_name"],
            "email": a_KMK_patient_information["email"],
            "password": "nouppercase33",
            "birth_date": a_KMK_patient_information["birth_date"],
            "gender": a_KMK_patient_information["gender"],
            "blood_type": a_KMK_patient_information["blood_type"],
        },
    )

    assert register_patient_response.status_code == 422


def test_register_patient_with_password_with_no_lowercase_returns_a_422_code():
    register_patient_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_patient_information["role"],
            "first_name": a_KMK_patient_information["first_name"],
            "last_name": a_KMK_patient_information["last_name"],
            "email": a_KMK_patient_information["email"],
            "password": "NOLOWERCASE33",
            "birth_date": a_KMK_patient_information["birth_date"],
            "gender": a_KMK_patient_information["gender"],
            "blood_type": a_KMK_patient_information["blood_type"],
        },
    )

    assert register_patient_response.status_code == 422


def test_register_patient_with_password_with_no_numbers_returns_a_422_code():
    register_patient_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_patient_information["role"],
            "first_name": a_KMK_patient_information["first_name"],
            "last_name": a_KMK_patient_information["last_name"],
            "email": a_KMK_patient_information["email"],
            "password": "noNUMBERS",
            "birth_date": a_KMK_patient_information["birth_date"],
            "gender": a_KMK_patient_information["gender"],
            "blood_type": a_KMK_patient_information["blood_type"],
        },
    )

    assert register_patient_response.status_code == 422


def test_register_physician_returns_a_201_code():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_to_register_endpoint = client.post(
            "/users/register",
            json=a_KMK_physician_information,
        )

    assert response_to_register_endpoint.status_code == 201


def test_register_physician_returns_a_message():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_to_register_endpoint = client.post(
            "/users/register",
            json=a_KMK_physician_information,
        )

    assert response_to_register_endpoint.json()["message"] == "Successfull registration"


def test_register_physician_creates_record_in_authentication():
    with pytest.raises(Exception):
        auth.get_user_by_email(a_KMK_physician_information["email"])
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            "/users/register",
            json=a_KMK_physician_information,
        )
    assert auth.get_user_by_email(a_KMK_physician_information["email"]) != None


def test_register_physician_creates_record_in_firestore():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            "/users/register",
            json=a_KMK_physician_information,
        )
    created_users_uid = auth.get_user_by_email(a_KMK_physician_information["email"]).uid
    assert db.collection("physicians").document(created_users_uid).get().exists == True


def test_register_physician_sets_information_object_in_firestore():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            "/users/register",
            json=a_KMK_physician_information,
        )
    created_users_uid = auth.get_user_by_email(a_KMK_physician_information["email"]).uid
    physician_object_from_firestore = (
        db.collection("physicians").document(created_users_uid).get().to_dict()
    )
    assert (
        physician_object_from_firestore["first_name"]
        == a_KMK_physician_information["first_name"]
    )
    assert (
        physician_object_from_firestore["last_name"]
        == a_KMK_physician_information["last_name"]
    )
    assert (
        physician_object_from_firestore["email"] == a_KMK_physician_information["email"]
    )
    assert (
        physician_object_from_firestore["tuition"]
        == a_KMK_physician_information["tuition"]
    )
    assert (
        physician_object_from_firestore["specialty"]
        == a_KMK_physician_information["specialty"]
    )
    assert physician_object_from_firestore["approved"] == "pending"
    assert physician_object_from_firestore["appointment_value"] == 3500
    assert physician_object_from_firestore["google_meet_conference_enabled"] == False


def test_register_physician_with_invalid_specialty_returns_a_422_code():
    register_physician_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_physician_information["role"],
            "first_name": a_KMK_physician_information["first_name"],
            "last_name": a_KMK_physician_information["last_name"],
            "email": a_KMK_physician_information["email"],
            "password": a_KMK_physician_information["password"],
            "tuition": a_KMK_physician_information["tuition"],
            "specialty": "invalidspecialty",
        },
    )

    assert register_physician_response.status_code == 422


def test_register_physician_with_missing_tuition_returns_a_422_code():
    register_physician_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_physician_information["role"],
            "first_name": a_KMK_physician_information["first_name"],
            "last_name": a_KMK_physician_information["last_name"],
            "email": a_KMK_physician_information["email"],
            "password": a_KMK_physician_information["password"],
            "specialty": a_KMK_physician_information["specialty"],
        },
    )

    assert register_physician_response.status_code == 422


def test_register_physician_twice_returns_a_400_code():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        first_register_patient = client.post(
            "/users/register",
            json=a_KMK_physician_information,
        )

    second_register_patient = client.post(
        "/users/register",
        json=a_KMK_physician_information,
    )

    assert first_register_patient.status_code == 201
    assert second_register_patient.status_code == 400
    assert second_register_patient.json()["detail"] == "Esta cuenta ya fue registrada"


def test_register_user_as_physician_and_as_patient_is_invalid():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_to_register_endpoint_as_physician = client.post(
            "/users/register",
            json=another_KMK_physician_information,
        )

        response_to_register_endpoint_as_patient = client.post(
            "/users/register",
            json=another_KMK_patient_information,
        )

    print("DATA TO REVIEW", response_to_register_endpoint_as_physician.json())
    assert response_to_register_endpoint_as_physician.status_code == 201
    assert response_to_register_endpoint_as_patient.status_code == 400
    assert (
        response_to_register_endpoint_as_patient.json()["detail"]
        == "Esta cuenta ya fue registrada"
    )

    another_created_test_user_uid = auth.get_user_by_email(
        another_KMK_patient_information["email"]
    ).uid
    db.collection("physicians").document(another_created_test_user_uid).delete()
    auth.delete_user(another_created_test_user_uid)


def test_registration_with_invalid_role_returns_a_422_code():
    response_to_register_endpoint_with_invalid_role = client.post(
        "/users/register",
        json={
            "role": "invalidrole",
            "first_name": a_KMK_patient_information["first_name"],
            "last_name": a_KMK_patient_information["last_name"],
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    )

    assert response_to_register_endpoint_with_invalid_role.status_code == 422


def test_register_physician_with_password_of_less_than_8_characters_returns_a_422_code():
    register_physician_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_physician_information["role"],
            "first_name": a_KMK_physician_information["first_name"],
            "last_name": a_KMK_physician_information["last_name"],
            "email": a_KMK_physician_information["email"],
            "password": "lT8",
            "tuition": a_KMK_physician_information["tuition"],
            "specialty": a_KMK_physician_information["specialty"],
        },
    )

    assert register_physician_response.status_code == 422


def test_register_physician_with_password_with_no_uppercase_returns_a_422_code():
    register_physician_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_physician_information["role"],
            "first_name": a_KMK_physician_information["first_name"],
            "last_name": a_KMK_physician_information["last_name"],
            "email": a_KMK_physician_information["email"],
            "password": "nouppercase33",
            "tuition": a_KMK_physician_information["tuition"],
            "specialty": a_KMK_physician_information["specialty"],
        },
    )

    assert register_physician_response.status_code == 422


def test_register_physician_with_password_with_no_lowercase_returns_a_422_code():
    register_physician_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_physician_information["role"],
            "first_name": a_KMK_physician_information["first_name"],
            "last_name": a_KMK_physician_information["last_name"],
            "email": a_KMK_physician_information["email"],
            "password": "NOLOWERCASE33",
            "tuition": a_KMK_physician_information["tuition"],
            "specialty": a_KMK_physician_information["specialty"],
        },
    )

    assert register_physician_response.status_code == 422


def test_register_physician_with_password_with_no_numbers_returns_a_422_code():
    register_physician_response = client.post(
        "/users/register",
        json={
            "role": a_KMK_physician_information["role"],
            "first_name": a_KMK_physician_information["first_name"],
            "last_name": a_KMK_physician_information["last_name"],
            "email": a_KMK_physician_information["email"],
            "password": "noNUMBERS",
            "tuition": a_KMK_physician_information["tuition"],
            "specialty": a_KMK_physician_information["specialty"],
        },
    )

    assert register_physician_response.status_code == 422


def test_register_endpoint_triggers_notification():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            "/users/register",
            json=a_KMK_physician_information,
        )

    assert mocked_request.call_count == 1
