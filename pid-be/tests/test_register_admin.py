import pytest
from firebase_admin import auth, firestore
from app.main import app
from fastapi.testclient import TestClient

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
    "name": "Physician Test User Register",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": specialties[0],
    "email": "testphysicianforregisteradmin@kmk.com",
    "password": "verySecurePassword123",
}

a_KMK_patient_information = {
    "role": "patient",
    "name": "Patient Test User Register",
    "last_name": "Test Last Name",
    "email": "testpatientforregisteradmin@kmk.com",
    "password": "verySecurePassword123",
}

initial_admin_information = {
    "email": "testinitialadminforregisteradmin@kmk.com",
    "password": "verySecurePassword123",
}

a_KMK_admin_information = {
    "name": "Admin to Register",
    "last_name": "Test Last Name",
    "email": "testadminforregisteradmin@kmk.com",
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
    pytest.patient_uid = created_user.uid
    db.collection("patients").document(pytest.patient_uid).set(
        a_KMK_patient_information
    )
    yield
    auth.delete_user(pytest.patient_uid)
    db.collection("patients").document(pytest.patient_uid).delete()


@pytest.fixture(scope="module", autouse=True)
def delete_physician(create_patient_and_then_delete_him):
    yield
    try:
        created_test_physician_uid = auth.get_user_by_email(
            a_KMK_physician_information["email"]
        ).uid
        auth.delete_user(created_test_physician_uid)
        db.collection("physicians").document(created_test_physician_uid).delete()
        db.collection("superusers").document(created_test_physician_uid).delete()
    except:
        print("[+] Physisican has not been created")


@pytest.fixture(scope="module", autouse=True)
def create_initial_admin_and_then_delete_him(delete_physician):
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


@pytest.fixture(autouse=True)
def delete_test_admin():
    try:
        created_test_admin_uid = auth.get_user_by_email(
            a_KMK_admin_information["email"]
        ).uid
        auth.delete_user(created_test_admin_uid)
        db.collection("superusers").document(created_test_admin_uid).delete()
    except:
        print("[+] No user found to delete")


def test_register_admin_endpoint_returns_a_201_if_valid():
    response_from_register_admin_endpoint = client.post(
        "/admin/register",
        json=a_KMK_admin_information,
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert response_from_register_admin_endpoint.status_code == 201


def test_register_admin_returns_a_message():
    response_from_register_admin_endpoint = client.post(
        "/admin/register",
        json=a_KMK_admin_information,
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert response_from_register_admin_endpoint.json()["message"] == "Registro exitoso"


def test_register_admin_creates_record_in_authentication():
    with pytest.raises(Exception):
        auth.get_user_by_email(a_KMK_admin_information["email"])
    client.post(
        "/admin/register",
        json=a_KMK_admin_information,
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )
    assert auth.get_user_by_email(a_KMK_admin_information["email"]) != None


def test_register_admin_creates_record_in_firestore():
    client.post(
        "/admin/register",
        json=a_KMK_admin_information,
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )
    created_users_uid = auth.get_user_by_email(a_KMK_admin_information["email"]).uid
    assert db.collection("superusers").document(created_users_uid).get().exists == True


def test_register_admin_sets_information_object_in_firestore():
    client.post(
        "/admin/register",
        json=a_KMK_admin_information,
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )
    created_users_uid = auth.get_user_by_email(a_KMK_admin_information["email"]).uid
    admin_object_from_firestore = (
        db.collection("superusers").document(created_users_uid).get().to_dict()
    )
    assert type(admin_object_from_firestore["id"]) == str
    assert admin_object_from_firestore["first_name"] == a_KMK_admin_information["name"]
    assert (
        admin_object_from_firestore["last_name"] == a_KMK_admin_information["last_name"]
    )
    assert admin_object_from_firestore["email"] == a_KMK_admin_information["email"]
    assert admin_object_from_firestore["registered_by"] == pytest.initial_admin_uid


def test_register_admin_twice_returns_a_400_code():
    first_register_admin = client.post(
        "/admin/register",
        json=a_KMK_admin_information,
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    second_register_admin = client.post(
        "/admin/register",
        json=a_KMK_admin_information,
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert first_register_admin.status_code == 201
    assert second_register_admin.status_code == 400
    assert second_register_admin.json()["detail"] == "Esta cuenta ya fue registrada"


def test_register_admin_with_empty_name_returns_a_422_code():
    register_admin_response = client.post(
        "/admin/register",
        json={
            "name": "",
            "last_name": a_KMK_admin_information["last_name"],
            "email": a_KMK_admin_information["email"],
            "password": a_KMK_admin_information["password"],
        },
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert register_admin_response.status_code == 422


def test_register_admin_with_invalid_name_format_returns_a_422_code():
    register_admin_response = client.post(
        "/admin/register",
        json={
            "name": 123456879,
            "last_name": a_KMK_admin_information["last_name"],
            "email": a_KMK_admin_information["email"],
            "password": a_KMK_admin_information["password"],
        },
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert register_admin_response.status_code == 422


def test_register_admin_with_empty_last_name_returns_a_422_code():
    register_admin_response = client.post(
        "/admin/register",
        json={
            "name": a_KMK_admin_information["name"],
            "last_name": "",
            "email": a_KMK_admin_information["email"],
            "password": a_KMK_admin_information["password"],
        },
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert register_admin_response.status_code == 422


def test_register_admin_with_invalid_last_name_format_returns_a_422_code():
    register_admin_response = client.post(
        "/admin/register",
        json={
            "name": a_KMK_admin_information["name"],
            "last_name": 123456789,
            "email": a_KMK_admin_information["email"],
            "password": a_KMK_admin_information["password"],
        },
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert register_admin_response.status_code == 422


def test_register_admin_with_invalid_email_returns_a_422_code():
    register_admin_response = client.post(
        "/admin/register",
        json={
            "name": a_KMK_admin_information["name"],
            "last_name": a_KMK_admin_information["email"],
            "email": "invalid@email",
            "password": a_KMK_admin_information["password"],
        },
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert register_admin_response.status_code == 422


def test_register_admin_with_no_authorization_header_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        "/admin/register", json=a_KMK_admin_information
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_register_admin_with_empty_authorization_header_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        "/admin/register",
        json=a_KMK_admin_information,
        headers={"Authorization": ""},
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_register_admin_with_empty_bearer_token_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        "/admin/register",
        json=a_KMK_admin_information,
        headers={"Authorization": f"Bearer "},
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_register_admin_with_non_bearer_token_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        "/admin/register",
        json=a_KMK_admin_information,
        headers={"Authorization": pytest.initial_admin_bearer},
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_register_admin_with_invalid_bearer_token_returns_401_code():
    response_from_admin_registration_endpoint = client.post(
        "/admin/register",
        json=a_KMK_admin_information,
        headers={"Authorization": "Bearer smth"},
    )

    assert response_from_admin_registration_endpoint.status_code == 401
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_register_admin_by_non_admin_returns_403_code_and_message():
    non_admin_bearer = client.post(
        "/users/login",
        json={
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    ).json()["token"]

    response_from_admin_registration_endpoint = client.post(
        "/admin/register",
        json=a_KMK_admin_information,
        headers={"Authorization": f"Bearer {non_admin_bearer}"},
    )

    assert response_from_admin_registration_endpoint.status_code == 403
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "User must be an admin"
    )


def test_a_previously_created_user_as_non_admin_can_be_registered_as_admin():
    created_user = auth.create_user(
        **{
            "email": a_KMK_physician_information["email"],
            "password": a_KMK_physician_information["password"],
        }
    )
    pytest.test_physician = created_user.uid
    db.collection("physicians").document(pytest.test_physician).set(
        a_KMK_physician_information
    )

    response_from_admin_registration_endpoint = client.post(
        "/admin/register",
        json={
            "name": a_KMK_physician_information["name"],
            "last_name": a_KMK_physician_information["last_name"],
            "email": a_KMK_physician_information["email"],
            "password": a_KMK_physician_information["password"],
        },
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert response_from_admin_registration_endpoint.status_code == 400
    assert (
        response_from_admin_registration_endpoint.json()["detail"]
        == "Esta cuenta ya fue registrada"
    )
