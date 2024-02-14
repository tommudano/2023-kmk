"""
FLOW
---------
1. Tenemos un paciente y un medico
2. El paciente saca un turno con el medico
3. El medico aprueba el turno
4. El medico cierra el turno
5. A partir del punto 4 el paciente no puede sacar turnos a menos que complete el turno
"""
import pytest
import time
from datetime import datetime, timedelta
from firebase_admin import auth, firestore
from app.main import app
from fastapi.testclient import TestClient
import requests
from unittest.mock import patch

client = TestClient(app)

db = firestore.client()

today_date = datetime.fromtimestamp(round(time.time()))
number_of_day_of_week = int(today_date.date().strftime("%w"))
next_week_day = today_date + timedelta(days=7)
next_week_day_first_block = next_week_day.replace(hour=9)
next_week_day_second_block = next_week_day.replace(hour=10)
next_week_day_third_block = next_week_day.replace(hour=11)

a_KMK_user_information = {
    "display_name": "KMK Test User",
    "email": "testUser@kmk.com",
    "email_verified": True,
    "password": "verySecurePassword123",
}

another_KMK_user_information = {
    "display_name": "KMK Test User",
    "email": "testUser2@kmk.com",
    "email_verified": True,
    "password": "verySecurePassword123",
}


a_KMK_physician_information = {
    "display_name": "Doc Docson",
    "email": "docDocson@kmk.com",
    "email_verified": True,
    "password": "verySecurePassword123",
}

an_appointment_data = {
    "date": round(next_week_day_first_block.timestamp()),
}


@pytest.fixture(scope="module", autouse=True)
def create_test_user():
    created_user = auth.create_user(**a_KMK_user_information)
    pytest.patient_uid = created_user.uid

    db.collection("patients").document(pytest.patient_uid).set(
        {
            "id": pytest.patient_uid,
            "first_name": "KMK",
            "last_name": "First",
            "email": a_KMK_user_information["email"],
        }
    )
    yield
    auth.delete_user(pytest.patient_uid)
    db.collection("patients").document(pytest.patient_uid).delete()


@pytest.fixture(scope="module", autouse=True)
def create_another_test_user(create_test_user):
    created_user = auth.create_user(**another_KMK_user_information)
    pytest.another_patient_uid = created_user.uid

    db.collection("patients").document(pytest.another_patient_uid).set(
        {
            "id": pytest.another_patient_uid,
            "first_name": "KMK",
            "last_name": "First",
            "email": another_KMK_user_information["email"],
        }
    )
    yield
    auth.delete_user(pytest.another_patient_uid)
    db.collection("patients").document(pytest.another_patient_uid).delete()


@pytest.fixture(scope="module", autouse=True)
def create_test_physician(create_another_test_user):
    first_created_physician = auth.create_user(**a_KMK_physician_information)
    pytest.physician_uid = first_created_physician.uid

    db.collection("physicians").document(pytest.physician_uid).set(
        {
            "id": pytest.physician_uid,
            "first_name": "Doc",
            "last_name": "Docson",
            "email": a_KMK_physician_information["email"],
            "agenda": {str(number_of_day_of_week): {"start": 8.0, "finish": 18.5}},
            "specialty": "surgeon",
            "approved": "approved",
            "tuition": "A111",
        }
    )
    yield
    auth.delete_user(pytest.physician_uid)
    db.collection("physicians").document(pytest.physician_uid).delete()


@pytest.fixture(scope="module", autouse=True)
def create_login_token_for_patient(create_test_physician):
    response_from_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )

    pytest.patient_bearer_token = response_from_login_endpoint.json()["token"]


@pytest.fixture(scope="module", autouse=True)
def create_login_token_for_another_patient(create_login_token_for_patient):
    response_from_login_endpoint = client.post(
        "/users/login",
        json={
            "email": another_KMK_user_information["email"],
            "password": another_KMK_user_information["password"],
        },
    )

    pytest.another_patient_bearer_token = response_from_login_endpoint.json()["token"]


@pytest.fixture(scope="module", autouse=True)
def create_login_token_for_physician(create_login_token_for_another_patient):
    response_from_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_physician_information["email"],
            "password": a_KMK_physician_information["password"],
        },
    )

    pytest.physician_bearer_token = response_from_login_endpoint.json()["token"]


@pytest.fixture(scope="module", autouse=True)
def create_test_appointment_and_then_delete_it(create_login_token_for_physician):
    an_appointment_data["physician_id"] = pytest.physician_uid
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        appointment_creation_response = client.post(
            "/appointments",
            json=an_appointment_data,
            headers={"Authorization": f"Bearer {pytest.patient_bearer_token}"},
        )

        pytest.appointment_id = appointment_creation_response.json()["appointment_id"]
    yield
    db.collection("appointments").document(pytest.appointment_id).delete()


@pytest.fixture(scope="module", autouse=True)
def approve_test_appointment(create_test_appointment_and_then_delete_it):
    db.collection("appointments").document(pytest.appointment_id).update(
        {"status": "approved"}
    )
    yield


@pytest.fixture(scope="module", autouse=True)
def close_appointment(approve_test_appointment):
    client.put(
        f"/appointments/close-appointment/{pytest.appointment_id}",
        headers={"Authorization": f"Bearer {pytest.physician_bearer_token}"},
        json={"attended": True, "start_time": "0"},
    )
    yield


@pytest.fixture(scope="module", autouse=True)
def delete_pending_scores_collection():
    yield
    pending_scores_docs = db.collection("patientsPendingToScore").list_documents()
    for pending_scores_doc in pending_scores_docs:
        pending_scores_doc.delete()


def test_patients_id_is_in_firestore_pending_to_score_collection():
    assert (
        db.collection("patientsPendingToScore")
        .document(pytest.patient_uid)
        .get()
        .exists
        == True
    )


def test_appointment_id_is_present_in_the_collection():
    patient_pending_to_score_doc = (
        db.collection("patientsPendingToScore")
        .document(pytest.patient_uid)
        .get()
        .to_dict()
    )

    assert patient_pending_to_score_doc.get(pytest.appointment_id) == True


def test_patient_taking_an_appointment_with_pending_scoring_returns_400_code_and_detail():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        appointment_creation_response = client.post(
            "/appointments",
            json={
                **an_appointment_data,
                "date": round(next_week_day_second_block.timestamp()),
            },
            headers={"Authorization": f"Bearer {pytest.patient_bearer_token}"},
        )
    assert appointment_creation_response.status_code == 400
    assert (
        appointment_creation_response.json()["detail"]
        == "El paciente tiene turnos pendientes por puntuar"
    )


def test_patient_taking_an_appointment_with_no_pending_scoring_returns_201_code():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        appointment_creation_response = client.post(
            "/appointments",
            json={
                **an_appointment_data,
                "date": round(next_week_day_third_block.timestamp()),
            },
            headers={"Authorization": f"Bearer {pytest.another_patient_bearer_token}"},
        )
    assert appointment_creation_response.status_code == 201
    db.collection("appointments").document(
        appointment_creation_response.json()["appointment_id"]
    ).delete()
