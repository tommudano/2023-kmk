import pytest
from firebase_admin import firestore, auth
from app.main import app
from fastapi.testclient import TestClient
from datetime import datetime
import time

client = TestClient(app)

db = firestore.client()

today_date = datetime.fromtimestamp(round(time.time()))
number_of_day_of_week = int(today_date.date().strftime("%w"))

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
    "name": "Physician Test User Register 1",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": specialties[0],
    "email": "testphysicianforpendingvalidations@kmk.com",
    "agenda": {str(number_of_day_of_week): {"start": 8.0, "finish": 18.5}},
}

another_KMK_physician_information = {
    "role": "physician",
    "name": "Physician Test User Register 2",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": specialties[0],
    "email": "testphysicianforpendingvalidations2@kmk.com",
    "agenda": {str(number_of_day_of_week): {"start": 8.0, "finish": 18.5}},
}

other_KMK_physician_information = {
    "role": "physician",
    "name": "Physician Test User Register 3",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": specialties[0],
    "email": "testphysicianforpendingvalidations3@kmk.com",
    "agenda": {str(number_of_day_of_week): {"start": 8.0, "finish": 18.5}},
}

a_KMK_patient_information = {
    "role": "patient",
    "name": "Patient Test User Register",
    "last_name": "Test Last Name",
    "email": "testpatientforpendingvalidations@kmk.com",
    "password": "verySecurePassword123",
    "birth_date": "9/1/2000",
    "gender": "m",
    "blood_type": "a",
}

initial_admin_information = {
    "email": "testinitialadminforpendingvalidations@kmk.com",
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
def create_validated_physician_and_then_delete_him(create_patient_and_then_delete_him):
    created_user = auth.create_user(
        **{
            "email": a_KMK_physician_information["email"],
            "password": "verySecurePassword123",
        }
    )
    pytest.physician_uid = created_user.uid
    db.collection("physicians").document(pytest.physician_uid).set(
        {
            "id": pytest.physician_uid,
            "first_name": a_KMK_physician_information["name"],
            "last_name": a_KMK_physician_information["last_name"],
            "email": a_KMK_physician_information["email"],
            "agenda": a_KMK_physician_information["agenda"],
            "specialty": a_KMK_physician_information["specialty"],
            "tuition": a_KMK_physician_information["tuition"],
            "approved": "approved",
            "agenda": {"1": {"start": 8, "finish": 18.5}},
        }
    )
    yield
    try:
        auth.delete_user(pytest.physician_uid)
        db.collection("physicians").document(pytest.physician_uid).delete()
    except:
        print("[+] Physisican has not been created")


@pytest.fixture(scope="module", autouse=True)
def create_denied_physician_and_then_delete_him(
    create_validated_physician_and_then_delete_him,
):
    created_user = auth.create_user(
        **{
            "email": another_KMK_physician_information["email"],
            "password": "verySecurePassword123",
        }
    )
    pytest.another_physician_uid = created_user.uid
    db.collection("physicians").document(pytest.another_physician_uid).set(
        {
            "id": pytest.another_physician_uid,
            "first_name": another_KMK_physician_information["name"],
            "last_name": another_KMK_physician_information["last_name"],
            "email": another_KMK_physician_information["email"],
            "agenda": another_KMK_physician_information["agenda"],
            "specialty": another_KMK_physician_information["specialty"],
            "tuition": another_KMK_physician_information["tuition"],
            "approved": "denied",
            "agenda": {"1": {"start": 8, "finish": 18.5}},
        }
    )
    yield
    try:
        auth.delete_user(pytest.another_physician_uid)
        db.collection("physicians").document(pytest.another_physician_uid).delete()
    except:
        print("[+] Physisican has not been created")


@pytest.fixture(scope="module", autouse=True)
def create_pending_physician_and_then_delete_him(
    create_denied_physician_and_then_delete_him,
):
    created_user = auth.create_user(
        **{
            "email": other_KMK_physician_information["email"],
            "password": "verySecurePassword123",
        }
    )
    pytest.other_physician_uid = created_user.uid
    db.collection("physicians").document(pytest.other_physician_uid).set(
        {
            "id": pytest.other_physician_uid,
            "first_name": other_KMK_physician_information["name"],
            "last_name": other_KMK_physician_information["last_name"],
            "email": other_KMK_physician_information["email"],
            "agenda": other_KMK_physician_information["agenda"],
            "specialty": other_KMK_physician_information["specialty"],
            "tuition": other_KMK_physician_information["tuition"],
            "approved": "pending",
            "agenda": {"1": {"start": 8, "finish": 18.5}},
        }
    )
    yield
    try:
        auth.delete_user(pytest.other_physician_uid)
        db.collection("physicians").document(pytest.other_physician_uid).delete()
    except:
        print("[+] Physisican has not been created")


@pytest.fixture(scope="module", autouse=True)
def create_initial_admin_and_then_delete_him(
    create_pending_physician_and_then_delete_him,
):
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


def test_get_working_physicians_returns_a_200_code():
    response_to_get_working_physicians_endpoint = client.get(
        "/admin/physicians-working",
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert response_to_get_working_physicians_endpoint.status_code == 200


def test_get_working_physicians_returns_a_list():
    response_to_get_working_physicians_endpoint = client.get(
        "/admin/physicians-working",
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert (
        type(response_to_get_working_physicians_endpoint.json()["physicians_working"])
        == list
    )


def test_get_working_physicians_returns_a_list_of_one_element():
    response_to_get_working_physicians_endpoint = client.get(
        "/admin/physicians-working",
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert (
        len(response_to_get_working_physicians_endpoint.json()["physicians_working"])
        == 1
    )


def test_get_working_physicians_returns_a_list_of_a_populated_physician():
    response_to_get_working_physicians_endpoint = client.get(
        "/admin/physicians-working",
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    physician_to_validate = response_to_get_working_physicians_endpoint.json()[
        "physicians_working"
    ][0]

    assert type(physician_to_validate["id"]) == str
    assert physician_to_validate["first_name"] == a_KMK_physician_information["name"]
    assert (
        physician_to_validate["last_name"] == a_KMK_physician_information["last_name"]
    )
    assert (
        physician_to_validate["specialty"] == a_KMK_physician_information["specialty"]
    )
    physician_to_validate["agenda"]["working_days"] = set(
        physician_to_validate["agenda"]["working_days"]
    )
    physician_to_validate["agenda"]["working_hours"].sort(
        key=lambda x: x["day_of_week"]
    )
    assert physician_to_validate["agenda"] == {
        "working_days": {number_of_day_of_week},
        "working_hours": [
            {
                "day_of_week": number_of_day_of_week,
                "start_time": 8.0,
                "finish_time": 18.5,
            }
        ],
        "appointments": [],
    }


def test_get_working_physicians_with_no_authorization_header_returns_401_code():
    response_from_get_working_physicians_endpoint = client.get(
        "/admin/physicians-working",
    )

    assert response_from_get_working_physicians_endpoint.status_code == 401
    assert (
        response_from_get_working_physicians_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_get_working_physicians_with_empty_authorization_header_returns_401_code():
    response_from_get_working_physicians_endpoint = client.get(
        "/admin/physicians-working",
        headers={"Authorization": ""},
    )

    assert response_from_get_working_physicians_endpoint.status_code == 401
    assert (
        response_from_get_working_physicians_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_get_working_physicians_with_empty_bearer_token_returns_401_code():
    response_from_get_working_physicians_endpoint = client.get(
        "/admin/physicians-working",
        headers={"Authorization": f"Bearer "},
    )

    assert response_from_get_working_physicians_endpoint.status_code == 401
    assert (
        response_from_get_working_physicians_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_get_working_physicians_with_non_bearer_token_returns_401_code():
    response_from_get_working_physicians_endpoint = client.get(
        "/admin/physicians-working",
        headers={"Authorization": pytest.initial_admin_bearer},
    )

    assert response_from_get_working_physicians_endpoint.status_code == 401
    assert (
        response_from_get_working_physicians_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_get_working_physicians_with_invalid_bearer_token_returns_401_code():
    response_from_get_working_physicians_endpoint = client.get(
        "/admin/physicians-working",
        headers={"Authorization": "Bearer smth"},
    )

    assert response_from_get_working_physicians_endpoint.status_code == 401
    assert (
        response_from_get_working_physicians_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_get_working_physicians_by_non_admin_returns_403_code_and_message():
    non_admin_bearer = client.post(
        "/users/login",
        json={
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    ).json()["token"]

    response_from_get_working_physicians_endpoint = client.get(
        "/admin/physicians-working",
        headers={"Authorization": f"Bearer {non_admin_bearer}"},
    )

    assert response_from_get_working_physicians_endpoint.status_code == 403
    assert (
        response_from_get_working_physicians_endpoint.json()["detail"]
        == "User must be an admin"
    )


def test_get_working_physicians_if_none_exists_returns_an_empty_list():
    db.collection("physicians").document(pytest.physician_uid).update(
        {"approved": "pending"}
    )
    response_to_get_working_physicians_endpoint = client.get(
        "/admin/physicians-working",
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert (
        response_to_get_working_physicians_endpoint.json()["physicians_working"] == []
    )
