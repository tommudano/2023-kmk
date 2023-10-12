import pytest
import requests
from datetime import datetime, timedelta, time
from .config import *
from firebase_admin import auth, firestore

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
    "email": "testphysicianforupdatingappointments@kmk.com",
    "password": "verySecurePassword123",
}

a_KMK_patient_information = {
    "role": "patient",
    "name": "Patient Test User Register",
    "last_name": "Test Last Name",
    "email": "testpatientforupdatingappointments@kmk.com",
    "password": "verySecurePassword123",
}

another_KMK_patient_information = {
    "role": "patient",
    "name": "Patient Test User Register 2",
    "last_name": "Test Last Name",
    "email": "testpatientforupdatingappointmentssecond@kmk.com",
    "password": "verySecurePassword123",
}


@pytest.fixture(scope="session", autouse=True)
def load_and_delete_specialties():
    for specialty in specialties:
        db.collection("specialties").document().set({"name": specialty})
    yield
    specilaties_doc = db.collection("specialties").list_documents()
    for specialty_doc in specilaties_doc:
        specialty_doc.delete()


@pytest.fixture(autouse=True)
def create_patient_and_then_delete_him():
    requests.post(
        "http://localhost:8080/users/register",
        json=a_KMK_patient_information,
    )
    pytest.patient_uid = auth.get_user_by_email(a_KMK_patient_information["email"]).uid
    yield
    auth.delete_user(pytest.patient_uid)
    db.collection("patients").document(pytest.patient_uid).delete()


@pytest.fixture(autouse=True)
def create_another_patient_and_then_delete_him(create_patient_and_then_delete_him):
    requests.post(
        "http://localhost:8080/users/register",
        json=another_KMK_patient_information,
    )
    pytest.another_patient_uid = auth.get_user_by_email(
        another_KMK_patient_information["email"]
    ).uid
    yield
    auth.delete_user(pytest.another_patient_uid)
    db.collection("patients").document(pytest.another_patient_uid).delete()


@pytest.fixture(autouse=True)
def log_in_patient(create_another_patient_and_then_delete_him):
    pytest.bearer_token = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": a_KMK_patient_information["email"],
            "password": a_KMK_patient_information["password"],
        },
    ).json()["token"]


@pytest.fixture(autouse=True)
def log_in_another_patient(log_in_patient):
    pytest.another_bearer_token = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": another_KMK_patient_information["email"],
            "password": another_KMK_patient_information["password"],
        },
    ).json()["token"]


@pytest.fixture(scope="session", autouse=True)
def create_physician_and_then_delete_him(load_and_delete_specialties):
    requests.post(
        "http://localhost:8080/users/register",
        json=a_KMK_physician_information,
    )
    pytest.physician_uid = auth.get_user_by_email(
        a_KMK_physician_information["email"]
    ).uid
    yield
    try:
        auth.delete_user(pytest.physician_uid)
        db.collection("physicians").document(pytest.physician_uid).delete()
    except:
        print("[+] Physisican has not been created")


@pytest.fixture(scope="session", autouse=True)
def approve_created_physician(create_physician_and_then_delete_him):
    db.collection("physicians").document(pytest.physician_uid).update(
        {"approved": "approved"}
    )
    yield


@pytest.fixture(autouse=True)
def create_appointment(log_in_another_patient):
    today_at_now = datetime.now()
    days_until_next_monday = (7 - today_at_now.weekday()) % 7
    next_monday = today_at_now + timedelta(days=days_until_next_monday)
    pytest.original_appointment_date = next_monday.replace(
        hour=9, minute=0, second=0, microsecond=0
    )

    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json={
            "physician_id": pytest.physician_uid,
            "date": round(pytest.original_appointment_date.timestamp()),
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    pytest.appointment_id = response_to_appointment_creation_endpoint.json()[
        "appointment_id"
    ]
    yield
    requests.delete(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )


@pytest.fixture(autouse=True)
def create_another_appointment(create_appointment):
    today_at_now = datetime.now()
    days_until_next_monday = (7 - today_at_now.weekday()) % 7
    next_monday = today_at_now + timedelta(days=days_until_next_monday)
    pytest.another_original_appointment_date = next_monday.replace(
        hour=13, minute=0, second=0, microsecond=0
    )

    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json={
            "physician_id": pytest.physician_uid,
            "date": round(pytest.another_original_appointment_date.timestamp()),
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    pytest.another_appointment_id = response_to_appointment_creation_endpoint.json()[
        "appointment_id"
    ]
    yield
    requests.delete(
        f"http://localhost:8080/appointments/{pytest.another_appointment_id}",
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )


def test_put_apointment_returns_a_200_code():
    new_date = pytest.original_appointment_date.replace(hour=10)
    response_from_put_appointment = requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        json={
            "date": round(new_date.timestamp()),
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_from_put_appointment.status_code == 200


def test_put_apointment_returns_a_message():
    new_date = pytest.original_appointment_date.replace(hour=10)
    response_from_put_appointment = requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        json={
            "date": round(new_date.timestamp()),
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert (
        response_from_put_appointment.json()["message"]
        == "Appointment updated successfully"
    )


def test_put_apointment_updates_the_date_in_firebase_object():
    assert db.collection("appointments").document(
        pytest.appointment_id
    ).get().to_dict()["date"] == round(pytest.original_appointment_date.timestamp())
    new_date = pytest.original_appointment_date.replace(hour=10)
    requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        json={
            "date": round(new_date.timestamp()),
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert db.collection("appointments").document(
        pytest.appointment_id
    ).get().to_dict()["date"] == round(new_date.timestamp())


def test_put_apointment_doenst_update_the_other_fields_in_firebase_object():
    appointment_before_update = (
        db.collection("appointments").document(pytest.appointment_id).get().to_dict()
    )
    new_date = pytest.original_appointment_date.replace(hour=10)
    requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        json={
            "date": round(new_date.timestamp()),
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    appointment_after_update = (
        db.collection("appointments").document(pytest.appointment_id).get().to_dict()
    )

    assert appointment_before_update["id"] == appointment_after_update["id"]
    assert (
        appointment_before_update["physician_id"]
        == appointment_after_update["physician_id"]
    )
    assert (
        appointment_before_update["patient_id"]
        == appointment_after_update["patient_id"]
    )
    assert (
        appointment_before_update["created_at"]
        == appointment_after_update["created_at"]
    )


def test_put_apointment_adds_the_updated_at_property_in_firestore():
    assert (
        db.collection("appointments")
        .document(pytest.appointment_id)
        .get()
        .to_dict()
        .get("updated_at")
        == None
    )
    new_date = pytest.original_appointment_date.replace(hour=10)
    requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        json={
            "date": round(new_date.timestamp()),
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert (
        db.collection("appointments")
        .document(pytest.appointment_id)
        .get()
        .to_dict()
        .get("updated_at")
        != None
    )

    assert (
        type(
            db.collection("appointments")
            .document(pytest.appointment_id)
            .get()
            .to_dict()
            .get("updated_at")
        )
        == int
    )


def test_update_inexistant_appointment_returns_a_400_code_and_message():
    new_date = pytest.original_appointment_date.replace(hour=10)
    response_from_put_appointment = requests.put(
        "http://localhost:8080/appointments/invalidappointmentid",
        json={
            "date": round(new_date.timestamp()),
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_from_put_appointment.status_code == 400
    assert response_from_put_appointment.json()["detail"] == "Invalid appointment id"


def test_update_another_users_appointment_returns_a_400_code_and_message():
    new_date = pytest.original_appointment_date.replace(hour=10)
    response_from_put_appointment = requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        json={
            "date": round(new_date.timestamp()),
        },
        headers={"Authorization": f"Bearer {pytest.another_bearer_token}"},
    )

    assert response_from_put_appointment.status_code == 400
    assert response_from_put_appointment.json()["detail"] == "Invalid appointment id"


def test_update_appointment_with_no_authorization_header_returns_401_code():
    response_from_update_appointment_endpoint = requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}"
    )

    assert response_from_update_appointment_endpoint.status_code == 401
    assert (
        response_from_update_appointment_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_update_appointment_with_empty_authorization_header_returns_401_code():
    response_from_update_appointment_endpoint = requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        headers={"Authorization": ""},
    )

    assert response_from_update_appointment_endpoint.status_code == 401
    assert (
        response_from_update_appointment_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_update_appointment_with_empty_bearer_token_returns_401_code():
    response_from_update_appointment_endpoint = requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        headers={"Authorization": f"Bearer "},
    )

    assert response_from_update_appointment_endpoint.status_code == 401
    assert (
        response_from_update_appointment_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_update_appointment_with_non_bearer_token_returns_401_code():
    response_from_update_appointment_endpoint = requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        headers={"Authorization": pytest.bearer_token},
    )

    assert response_from_update_appointment_endpoint.status_code == 401
    assert (
        response_from_update_appointment_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_update_appointment_with_invalid_bearer_token_returns_401_code():
    response_from_update_appointment_endpoint = requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        headers={"Authorization": "Bearer smth"},
    )

    assert response_from_update_appointment_endpoint.status_code == 401
    assert (
        response_from_update_appointment_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_invalid_date_format_in_appointment_update_endpoint_returns_a_422_Code():
    response_to_appointment_update_endpoint = requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        json={"date": "tomorrow"},
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_update_endpoint.status_code == 422


def test_past_date_in_appointment_update_endpoint_returns_a_422_code():
    response_to_appointment_update_endpoint = requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        json={"date": 0},
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_update_endpoint.status_code == 422


def test_updating_appointment_in_a_non_working_day_of_the_physician_returns_a_400_code():
    today_at_now = datetime.now()
    days_until_next_saturday = (5 - today_at_now.weekday()) % 7
    next_saturday = today_at_now + timedelta(days=days_until_next_saturday)
    non_working_day = next_saturday.replace(hour=9, minute=0, second=0, microsecond=0)
    response_to_appointment_update_endpoint = requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        json={"date": round(non_working_day.timestamp())},
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_update_endpoint.status_code == 400
    assert (
        response_to_appointment_update_endpoint.json()["detail"]
        == "Can only set appointment at physicians available hours"
    )


def test_updating_appointment_in_a_non_working_hour_after_agenda_of_the_physician_returns_a_400_code():
    new_date = pytest.original_appointment_date.replace(hour=22)
    response_to_appointment_update_endpoint = requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        json={"date": round(new_date.timestamp())},
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_update_endpoint.status_code == 400
    assert (
        response_to_appointment_update_endpoint.json()["detail"]
        == "Can only set appointment at physicians available hours"
    )


def test_updating_appointment_in_a_non_working_hour_before_agenda_of_the_physician_returns_a_400_code():
    new_date = pytest.original_appointment_date.replace(hour=3)
    response_to_appointment_update_endpoint = requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        json={"date": round(new_date.timestamp())},
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_update_endpoint.status_code == 400
    assert (
        response_to_appointment_update_endpoint.json()["detail"]
        == "Can only set appointment at physicians available hours"
    )


def test_valid_appointment_update_saves_slot_in_physicians_agenda():
    new_date = pytest.original_appointment_date.replace(hour=10)
    physician_doc = (
        db.collection("physicians").document(pytest.physician_uid).get().to_dict()
    )
    assert physician_doc["appointments"].get(str(round(new_date.timestamp()))) == None
    requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        json={
            "date": round(new_date.timestamp()),
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    physician_doc = (
        db.collection("physicians").document(pytest.physician_uid).get().to_dict()
    )
    assert physician_doc["appointments"].get(str(round(new_date.timestamp()))) == True


def test_valid_appointment_update_removes_previously_saved_time_slot_in_physicians_agenda():
    physician_doc = (
        db.collection("physicians").document(pytest.physician_uid).get().to_dict()
    )
    assert (
        physician_doc["appointments"].get(
            str(round(pytest.original_appointment_date.timestamp()))
        )
        != None
    )
    new_date = pytest.original_appointment_date.replace(hour=10)
    requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        json={
            "date": round(new_date.timestamp()),
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    physician_doc = (
        db.collection("physicians").document(pytest.physician_uid).get().to_dict()
    )
    assert (
        physician_doc["appointments"].get(
            str(round(pytest.original_appointment_date.timestamp()))
        )
        == None
    )


def test_updating_an_appointment_for_an_occupied_slot_of_a_physician_returns_a_400_code():
    response_to_appointment_update_endpoint = requests.put(
        f"http://localhost:8080/appointments/{pytest.appointment_id}",
        json={
            "date": round(pytest.another_original_appointment_date.timestamp()),
        },
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_update_endpoint.status_code == 400
    assert (
        response_to_appointment_update_endpoint.json()["detail"]
        == "Can only set appointment at physicians available hours"
    )
