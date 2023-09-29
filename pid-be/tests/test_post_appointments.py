import pytest
import requests
import time
from datetime import datetime, timedelta
from .config import *
from firebase_admin import auth, firestore

db = firestore.client()

today_date = datetime.fromtimestamp(round(time.time()))
number_of_day_of_week = today_date.isoweekday()
next_week_day = today_date + timedelta(days=7)
next_week_day_off_by_one_day = today_date + timedelta(days=8)
next_week_day_first_block = next_week_day.replace(hour=9)
next_week_day_second_block = next_week_day.replace(hour=10)
next_week_day_off_by_hours = next_week_day.replace(hour=21)
another_next_week_day_off_by_hours = next_week_day.replace(hour=3)

valid_physician_id = "validphysicianid"

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

a_KMK_user_information = {
    "display_name": "KMK Test User",
    "email": "postApppointmentTestUser@kmk.com",
    "email_verified": True,
    "password": "verySecurePassword123",
}


@pytest.fixture(autouse=True)
def create_and_delete_physician():
    db.collection("physicians").document(valid_physician_id).set(
        {
            "first_name": "Doc",
            "agenda": {str(number_of_day_of_week): {"start": 8, "finish": 18.5}},
        }
    )
    yield
    db.collection("physicians").document(valid_physician_id).delete()


@pytest.fixture(autouse=True)
def create_test_user():
    created_user = auth.create_user(**a_KMK_user_information)
    a_KMK_user_information["uid"] = created_user.uid
    yield
    auth.delete_user(a_KMK_user_information["uid"])


def test_creation_of_appointment_with_valid_data_returns_201_code():
    response_from_login_endpoint = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json=appointment_data,
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert response_to_appointment_creation_endpoint.status_code == 201


def test_creation_of_apointment_with_valid_data_returns_the_id_of_the_created_appointment():
    response_from_login_endpoint = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json=appointment_data,
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert (
        type(response_to_appointment_creation_endpoint.json()["appointment_id"]) == str
    )


def test_returned_id_is_the_id_of_the_created_appointment():
    response_from_login_endpoint = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json=appointment_data,
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
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


def test_invalid_date_format_in_appointment_creation_endpoint_returns_a_422_Code():
    response_from_login_endpoint = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json={"date": "tomorrow", "physician_id": appointment_data["physician_id"]},
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert response_to_appointment_creation_endpoint.status_code == 422


def test_past_date_in_appointment_creation_endpoint_returns_a_422_code():
    response_from_login_endpoint = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json={"date": 0, "physician_id": appointment_data["physician_id"]},
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert response_to_appointment_creation_endpoint.status_code == 422


def test_invalid_physician_id_format_in_appointment_creation_endpoint_returns_a_422_code():
    response_from_login_endpoint = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json={"date": appointment_data["date"], "physician_id": [1, 3, 5]},
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert response_to_appointment_creation_endpoint.status_code == 422


def test_creation_of_appointment_with_no_authorization_header_returns_401_code():
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments", json=appointment_data
    )

    assert response_to_appointment_creation_endpoint.status_code == 401
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_creation_of_appointment_with_empty_authorization_header_returns_401_code():
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json=appointment_data,
        headers={"Authorization": ""},
    )

    assert response_to_appointment_creation_endpoint.status_code == 401
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_creation_of_appointment_with_empty_bearer_token_returns_401_code():
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json=appointment_data,
        headers={"Authorization": f"Bearer "},
    )

    assert response_to_appointment_creation_endpoint.status_code == 401
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_creation_of_appointment_with_non_bearer_token_returns_401_code():
    response_from_login_endpoint = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json=appointment_data,
        headers={"Authorization": response_from_login_endpoint.json()["token"]},
    )

    assert response_to_appointment_creation_endpoint.status_code == 401
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_creation_of_appointment_with_invalid_bearer_token_returns_401_code():
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json=appointment_data,
        headers={"Authorization": "Bearer smth"},
    )

    assert response_to_appointment_creation_endpoint.status_code == 401
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_creation_of_appointment_with_a_physician_id_that_doesnt_exists_returns_a_422_code():
    response_from_login_endpoint = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json={"date": appointment_data["date"], "physician_id": "invalidPhysicianId"},
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert response_to_appointment_creation_endpoint.status_code == 422


def test_creating_appointment_in_a_non_working_day_of_the_physician_returns_a_400_code():
    response_from_login_endpoint = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json=out_of_working_days_appointment_data,
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert response_to_appointment_creation_endpoint.status_code == 400
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "Can only set appointment at physicians available hours"
    )


def test_creating_appointment_in_a_non_working_hour_after_agenda_of_the_physician_returns_a_400_code():
    response_from_login_endpoint = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json=out_of_working_hours_appointment_data,
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert response_to_appointment_creation_endpoint.status_code == 400
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "Can only set appointment at physicians available hours"
    )


def test_creating_appointment_in_a_non_working_hour_before_agenda_of_the_physician_returns_a_400_code():
    response_from_login_endpoint = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json=another_out_of_working_hours_appointment_data,
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert response_to_appointment_creation_endpoint.status_code == 400
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "Can only set appointment at physicians available hours"
    )


def test_valid_appointment_creation_saves_slot_in_physicians_agenda():
    physician_doc = (
        db.collection("physicians").document(valid_physician_id).get().to_dict()
    )
    assert physician_doc.get("appointments") == None
    response_from_login_endpoint = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    requests.post(
        "http://localhost:8080/appointments",
        json=appointment_data,
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    requests.post(
        "http://localhost:8080/appointments",
        json=another_appointment_data,
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    physician_doc = (
        db.collection("physicians").document(valid_physician_id).get().to_dict()
    )

    assert physician_doc["appointments"].get(str(appointment_data["date"])) == True
    assert (
        physician_doc["appointments"].get(str(another_appointment_data["date"])) == True
    )


def test_creating_two_appointments_for_the_same_physician_in_the_same_valid_date_returns_a_400_code():
    response_from_login_endpoint = requests.post(
        "http://localhost:8080/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json=appointment_data,
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert response_to_appointment_creation_endpoint.status_code == 201

    response_to_appointment_creation_endpoint = requests.post(
        "http://localhost:8080/appointments",
        json=appointment_data,
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert response_to_appointment_creation_endpoint.status_code == 400
    assert (
        response_to_appointment_creation_endpoint.json()["detail"]
        == "Can only set appointment at physicians available hours"
    )
