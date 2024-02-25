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
number_of_day_of_week = today_date.date().strftime("%w")
next_week_day = today_date + timedelta(days=7)
next_week_day_off_by_one_day = today_date + timedelta(days=8)
next_week_day_first_block = next_week_day.replace(hour=9)
next_week_day_second_block = next_week_day.replace(hour=10)
next_week_day_off_by_hours = next_week_day.replace(hour=21)
another_next_week_day_off_by_hours = next_week_day.replace(hour=3)

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

valid_physician_id = "validphysicianid"
non_virtual_valid_physician_id = "nonvirtualvalidphysicianid"
pending_physician_id = "pendingphysicianid"
denied_physician_id = "deniedphysicianid"

appointment_data = {
    "physician_id": valid_physician_id,
    "date": round(next_week_day_first_block.timestamp()),
}

another_appointment_data = {
    "physician_id": valid_physician_id,
    "date": round(next_week_day_second_block.timestamp()),
}

out_of_working_days_appointment_data = {
    "physician_id": valid_physician_id,
    "date": round(next_week_day_off_by_one_day.timestamp()),
}

out_of_working_hours_appointment_data = {
    "physician_id": valid_physician_id,
    "date": round(next_week_day_off_by_hours.timestamp()),
}

another_out_of_working_hours_appointment_data = {
    "physician_id": valid_physician_id,
    "date": round(another_next_week_day_off_by_hours.timestamp()),
}


pending_physician_appointment_data = {
    "physician_id": pending_physician_id,
    "date": round(another_next_week_day_off_by_hours.timestamp()),
}

denied_physician_appointment_data = {
    "physician_id": denied_physician_id,
    "date": round(another_next_week_day_off_by_hours.timestamp()),
}

a_KMK_user_information = {
    "email": "postApppointmentTestUser@kmk.com",
    "password": "verySecurePassword123",
    "role": "patient",
    "first_name": "KMK",
    "last_name": "Test User",
    "birth_date": "9/1/2000",
    "gender": "m",
    "blood_type": "a",
}


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


@pytest.fixture(autouse=True)
def create_and_delete_physicians(load_and_delete_specialties):
    db.collection("physicians").document(valid_physician_id).set(
        {
            "role": "physician",
            "id": valid_physician_id,
            "first_name": "Doc",
            "agenda": {str(number_of_day_of_week): {"start": 8, "finish": 18.5}},
            "approved": "approved",
            "last_name": "docson",
            "tuition": "A111",
            "specialty": specialties[0],
            "email": "docdocson@postappointments.com",
            "google_meet_conference_enabled": True,
        }
    )
    db.collection("physicians").document(non_virtual_valid_physician_id).set(
        {
            "role": "physician",
            "id": non_virtual_valid_physician_id,
            "first_name": "Doc",
            "agenda": {str(number_of_day_of_week): {"start": 8, "finish": 18.5}},
            "approved": "approved",
            "last_name": "docson",
            "tuition": "A111",
            "specialty": specialties[0],
            "email": "docdocson2@postappointments.com",
            "google_meet_conference_enabled": False,
        }
    )
    db.collection("physicians").document(pending_physician_id).set(
        {
            "role": "physician",
            "id": pending_physician_id,
            "first_name": "Doc",
            "agenda": {str(number_of_day_of_week): {"start": 8, "finish": 18.5}},
            "approved": "pending",
            "last_name": "docson",
            "tuition": "A111",
            "specialty": specialties[0],
            "email": "docdocson@postappointments.com",
            "google_meet_conference_enabled": False,
        }
    )
    db.collection("physicians").document(denied_physician_id).set(
        {
            "role": "physician",
            "id": denied_physician_id,
            "first_name": "Doc",
            "agenda": {str(number_of_day_of_week): {"start": 8, "finish": 18.5}},
            "approved": "denied",
            "last_name": "docson",
            "tuition": "A111",
            "specialty": specialties[0],
            "email": "docdocson@postappointments.com",
            "google_meet_conference_enabled": False,
        }
    )
    yield
    db.collection("physicians").document(valid_physician_id).delete()
    db.collection("physicians").document(non_virtual_valid_physician_id).delete()
    db.collection("physicians").document(pending_physician_id).delete()
    db.collection("physicians").document(denied_physician_id).delete()


@pytest.fixture(scope="module", autouse=True)
def create_test_user(load_and_delete_specialties):
    created_user = auth.create_user(
        **{
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        }
    )
    pytest.patient_uid = created_user.uid
    db.collection("patients").document(pytest.patient_uid).set(a_KMK_user_information)
    pytest.bearer_token = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    ).json()["token"]
    a_KMK_user_information["uid"] = auth.verify_id_token(pytest.bearer_token)["uid"]
    yield
    auth.delete_user(pytest.patient_uid)
    db.collection("patients").document(pytest.patient_uid).delete()


def test_creation_of_appointment_with_valid_data_returns_201_code():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_to_appointment_creation_endpoint = client.post(
            "/appointments",
            json=appointment_data,
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )

    assert response_to_appointment_creation_endpoint.status_code == 201


def test_creation_of_apointment_with_valid_data_returns_the_id_of_the_created_appointment():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_to_appointment_creation_endpoint = client.post(
            "/appointments",
            json=appointment_data,
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )

    assert (
        type(response_to_appointment_creation_endpoint.json()["appointment_id"]) == str
    )


def test_returned_id_is_the_id_of_the_created_appointment():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_to_appointment_creation_endpoint = client.post(
            "/appointments",
            json=appointment_data,
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )

    appointment_id = response_to_appointment_creation_endpoint.json()["appointment_id"]

    created_appointment = db.collection("appointments").document(appointment_id).get()
    assert created_appointment.exists == True
    created_appointment = created_appointment.to_dict()
    assert created_appointment["date"] == appointment_data["date"]
    assert created_appointment["physician_id"] == appointment_data["physician_id"]
    assert created_appointment["id"] == appointment_id
    assert type(created_appointment["created_at"]) == int
    assert created_appointment["patient_id"] == a_KMK_user_information["uid"]
    assert created_appointment["appointment_value"] == 3500
    assert created_appointment["google_meet_conference"] == False


def test_invalid_date_format_in_appointment_creation_endpoint_returns_a_422_Code():
    response_to_appointment_creation_endpoint = client.post(
        "/appointments",
        json={"date": "tomorrow", "physician_id": appointment_data["physician_id"]},
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_creation_endpoint.status_code == 422


def test_past_date_in_appointment_creation_endpoint_returns_a_422_code():
    response_to_appointment_creation_endpoint = client.post(
        "/appointments",
        json={"date": 0, "physician_id": appointment_data["physician_id"]},
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_creation_endpoint.status_code == 422


def test_invalid_physician_id_format_in_appointment_creation_endpoint_returns_a_422_code():
    response_to_appointment_creation_endpoint = client.post(
        "/appointments",
        json={"date": appointment_data["date"], "physician_id": [1, 3, 5]},
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_creation_endpoint.status_code == 422


def test_creation_of_appointment_with_no_authorization_header_returns_401_code():
    response_to_appointment_creation_endpoint = client.post(
        "/appointments", json=appointment_data
    )

    assert response_to_appointment_creation_endpoint.status_code == 401
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_creation_of_appointment_with_empty_authorization_header_returns_401_code():
    response_to_appointment_creation_endpoint = client.post(
        "/appointments",
        json=appointment_data,
        headers={"Authorization": ""},
    )

    assert response_to_appointment_creation_endpoint.status_code == 401
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_creation_of_appointment_with_empty_bearer_token_returns_401_code():
    response_to_appointment_creation_endpoint = client.post(
        "/appointments",
        json=appointment_data,
        headers={"Authorization": f"Bearer "},
    )

    assert response_to_appointment_creation_endpoint.status_code == 401
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_creation_of_appointment_with_non_bearer_token_returns_401_code():
    response_to_appointment_creation_endpoint = client.post(
        "/appointments",
        json=appointment_data,
        headers={"Authorization": pytest.bearer_token},
    )

    assert response_to_appointment_creation_endpoint.status_code == 401
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_creation_of_appointment_with_invalid_bearer_token_returns_401_code():
    response_to_appointment_creation_endpoint = client.post(
        "/appointments",
        json=appointment_data,
        headers={"Authorization": "Bearer smth"},
    )

    assert response_to_appointment_creation_endpoint.status_code == 401
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_creation_of_appointment_with_a_physician_id_that_doesnt_exists_returns_a_422_code():
    response_to_appointment_creation_endpoint = client.post(
        "/appointments",
        json={"date": appointment_data["date"], "physician_id": "invalidPhysicianId"},
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_creation_endpoint.status_code == 422


def test_creating_appointment_in_a_non_working_day_of_the_physician_returns_a_422_code():
    response_to_appointment_creation_endpoint = client.post(
        "/appointments",
        json=out_of_working_days_appointment_data,
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_creation_endpoint.status_code == 422


def test_creating_appointment_in_a_non_working_hour_after_agenda_of_the_physician_returns_a_422_code():
    response_to_appointment_creation_endpoint = client.post(
        "/appointments",
        json=out_of_working_hours_appointment_data,
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_creation_endpoint.status_code == 422


def test_creating_appointment_in_a_non_working_hour_before_agenda_of_the_physician_returns_a_422_code():
    response_to_appointment_creation_endpoint = client.post(
        "/appointments",
        json=another_out_of_working_hours_appointment_data,
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_creation_endpoint.status_code == 422


def test_valid_appointment_creation_saves_slot_in_physicians_agenda():
    physician_doc = (
        db.collection("physicians").document(valid_physician_id).get().to_dict()
    )
    assert physician_doc.get("appointments") == None
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            "/appointments",
            json=appointment_data,
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )
        client.post(
            "/appointments",
            json=another_appointment_data,
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )

    physician_doc = (
        db.collection("physicians").document(valid_physician_id).get().to_dict()
    )

    assert physician_doc["appointments"].get(str(appointment_data["date"])) == True
    assert (
        physician_doc["appointments"].get(str(another_appointment_data["date"])) == True
    )


def test_creating_two_appointments_for_the_same_physician_in_the_same_valid_date_returns_a_422_code():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_to_appointment_creation_endpoint = client.post(
            "/appointments",
            json=appointment_data,
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )

    assert response_to_appointment_creation_endpoint.status_code == 201

    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_to_appointment_creation_endpoint = client.post(
            "/appointments",
            json=appointment_data,
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )

    assert response_to_appointment_creation_endpoint.status_code == 422


def test_appointment_creation_with_a_pending_physician_returns_a_422_code_and_a_detail():
    response_to_appointment_creation_endpoint = client.post(
        "/appointments",
        json=pending_physician_appointment_data,
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_creation_endpoint.status_code == 422


def test_appointment_creation_with_a_denied_physician_returns_a_422_code_and_a_detail():
    response_to_appointment_creation_endpoint = client.post(
        "/appointments",
        json=denied_physician_appointment_data,
        headers={"Authorization": f"Bearer {pytest.bearer_token}"},
    )

    assert response_to_appointment_creation_endpoint.status_code == 422


def test_post_appointments_endpoint_triggers_notification():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            "/appointments",
            json=appointment_data,
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )

    args, kwargs = mocked_request.call_args
    assert kwargs["json"]["type"] == "PENDING_APPOINTMENT"
    assert mocked_request.call_count == 1


def test_appointment_creation_for_virtual_apppointment_for_a_vitual_physician_is_valid():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_to_appointment_creation_endpoint = client.post(
            "/appointments",
            json={**appointment_data, "google_meet_conference": True},
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )

    assert response_to_appointment_creation_endpoint.status_code == 201
    appointment_id = response_to_appointment_creation_endpoint.json()["appointment_id"]

    created_appointment = (
        db.collection("appointments").document(appointment_id).get().to_dict()
    )
    assert created_appointment["google_meet_conference"] == True


def test_appointment_creation_for_virtual_apppointment_for_a_non_vitual_physician_is_invalid():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        response_to_appointment_creation_endpoint = client.post(
            "/appointments",
            json={
                **appointment_data,
                "physician_id": non_virtual_valid_physician_id,
                "google_meet_conference": True,
            },
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )

    assert response_to_appointment_creation_endpoint.status_code == 400
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "El medico no acepta videoconferencias por meet gestionadas a traves de la app"
    )


def test_post_appointments_endpoint_triggers_notification_for_virtual_option():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.post(
            "/appointments",
            json={**appointment_data, "google_meet_conference": True},
            headers={"Authorization": f"Bearer {pytest.bearer_token}"},
        )

    args, kwargs = mocked_request.call_args
    assert kwargs["json"]["type"] == "PENDING_VIRTUAL_APPOINTMENT"
    assert mocked_request.call_count == 1
