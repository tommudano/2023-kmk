import pytest
import time
from datetime import datetime
from firebase_admin import firestore, auth
from app.main import app
from fastapi.testclient import TestClient
import requests

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

today_date = datetime.fromtimestamp(round(time.time()))
number_of_day_of_week = int(today_date.date().strftime("%w"))

a_KMK_user_information = {
    "display_name": "KMK Test User",
    "email": "getPhysiciansBySpecialtyTestUser@kmk.com",
    "email_verified": True,
    "password": "verySecurePassword123",
}

a_physician_information = {
    "id": "avalidid",
    "first_name": "Doc",
    "last_name": "Docson",
    "email": "doctor@getbyspecialty.com",
    "specialty": specialties[0],
    "agenda": {str(number_of_day_of_week): {"start": 8, "finish": 18.5}},
    "approved": "approved",
    "tuition": "A111",
    "role": "physician",
}

another_physician_information = {
    "id": "anothervalidid",
    "first_name": "Doc",
    "last_name": "Docson the Second",
    "email": "doctor@getbyspecialty.com",
    "specialty": specialties[0],
    "agenda": {str(number_of_day_of_week): {"start": 8, "finish": 18.5}},
    "approved": "approved",
    "tuition": "A111",
    "role": "physician",
}

other_physician_information = {
    "id": "othervalidid",
    "first_name": "Doc",
    "last_name": "Docson the Third",
    "email": "doctor@getbyspecialty.com",
    "specialty": specialties[1],
    "agenda": {str(number_of_day_of_week): {"start": 8, "finish": 18.5}},
    "approved": "approved",
    "tuition": "A111",
    "role": "physician",
}

pending_to_approve_physician_information = {
    "id": "pendingphysicianid",
    "first_name": "Doc",
    "last_name": "Docson the Third",
    "email": "doctor@getbyspecialty.com",
    "specialty": specialties[1],
    "agenda": {str(number_of_day_of_week): {"start": 8, "finish": 18.5}},
    "approved": "pending",
    "tuition": "A111",
    "role": "physician",
}

denied_approve_physician_information = {
    "id": "deniedphysicianid",
    "first_name": "Doc",
    "last_name": "Docson the Third",
    "email": "doctor@getbyspecialty.com",
    "specialty": specialties[1],
    "agenda": {str(number_of_day_of_week): {"start": 8, "finish": 18.5}},
    "approved": "denied",
    "tuition": "A111",
    "role": "physician",
}


@pytest.fixture(scope="module", autouse=True)
def load_and_delete_physicians():
    db.collection("physicians").document(a_physician_information["id"]).set(
        a_physician_information
    )
    db.collection("physicians").document(another_physician_information["id"]).set(
        another_physician_information
    )
    db.collection("physicians").document(other_physician_information["id"]).set(
        other_physician_information
    )
    db.collection("physicians").document(
        pending_to_approve_physician_information["id"]
    ).set(pending_to_approve_physician_information)
    db.collection("physicians").document(
        denied_approve_physician_information["id"]
    ).set(denied_approve_physician_information)

    yield
    physicians_doc = db.collection("physicians").list_documents()
    for physician_doc in physicians_doc:
        physician_doc.delete()


@pytest.fixture(scope="module", autouse=True)
def create_test_user():
    created_user = auth.create_user(**a_KMK_user_information)
    a_KMK_user_information["uid"] = created_user.uid
    yield
    auth.delete_user(a_KMK_user_information["uid"])


@pytest.fixture(scope="module", autouse=True)
def load_and_delete_specialties():
    for specialty in specialties:
        db.collection("specialties").document().set({"name": specialty})
    yield
    specilaties_doc = db.collection("specialties").list_documents()
    for specialty_doc in specilaties_doc:
        specialty_doc.delete()


def test_valid_request_to_get_physicians_endpoint_returns_200_code():
    response_from_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )

    response_to_get_physicians_endpoint = client.get(
        f"/physicians/specialty/{specialties[0]}",
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert response_to_get_physicians_endpoint.status_code == 200


def test_valid_request_to_get_physicians_endpoint_returns_a_list():
    response_from_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_get_physicians_endpoint = client.get(
        f"/physicians/specialty/{specialties[0]}",
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert type(response_to_get_physicians_endpoint.json()["physicians"]) == list


def test_valid_request_to_get_physicians_endpoint_for_first_specialty_returns_a_list_of_two_elements():
    response_from_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_get_physicians_endpoint = client.get(
        f"/physicians/specialty/{specialties[0]}",
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert len(response_to_get_physicians_endpoint.json()["physicians"]) == 2


def test_valid_request_to_get_physicians_endpoint_for_second_specialty_returns_a_list_of_one_element():
    response_from_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_get_physicians_endpoint = client.get(
        f"/physicians/specialty/{specialties[1]}",
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert len(response_to_get_physicians_endpoint.json()["physicians"]) == 1


def test_valid_request_to_get_physicians_endpoint_for_third_specialty_returns_an_empty_list():
    response_from_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_get_physicians_endpoint = client.get(
        f"/physicians/specialty/{specialties[2]}",
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert len(response_to_get_physicians_endpoint.json()["physicians"]) == 0


def test_valid_request_to_get_physicians_endpoint_for_first_specialty_returns_a_list_of_two_physician_objects():
    response_from_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_get_physicians_endpoint = client.get(
        f"/physicians/specialty/{specialties[0]}",
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    physicians = response_to_get_physicians_endpoint.json()["physicians"]
    if physicians[0]["id"] == a_physician_information["id"]:
        first_physician_to_assert = physicians[0]
        second_physician_to_assert = physicians[1]
    else:
        first_physician_to_assert = physicians[1]
        second_physician_to_assert = physicians[0]

    assert first_physician_to_assert["id"] == a_physician_information["id"]
    assert (
        first_physician_to_assert["first_name"] == a_physician_information["first_name"]
    )
    assert (
        first_physician_to_assert["last_name"] == a_physician_information["last_name"]
    )
    assert (
        first_physician_to_assert["specialty"] == a_physician_information["specialty"]
    )
    assert first_physician_to_assert["agenda"]["working_days"] == [
        number_of_day_of_week
    ]
    assert first_physician_to_assert["agenda"]["appointments"] == []
    assert first_physician_to_assert["agenda"]["working_hours"] == [
        {
            "day_of_week": number_of_day_of_week,
            "start_time": a_physician_information["agenda"][str(number_of_day_of_week)][
                "start"
            ],
            "finish_time": a_physician_information["agenda"][
                str(number_of_day_of_week)
            ]["finish"],
        }
    ]

    assert second_physician_to_assert["id"] == another_physician_information["id"]
    assert (
        second_physician_to_assert["first_name"]
        == another_physician_information["first_name"]
    )
    assert (
        second_physician_to_assert["last_name"]
        == another_physician_information["last_name"]
    )
    assert (
        second_physician_to_assert["specialty"]
        == another_physician_information["specialty"]
    )
    assert second_physician_to_assert["agenda"]["working_days"] == [
        number_of_day_of_week
    ]
    assert second_physician_to_assert["agenda"]["appointments"] == []
    assert second_physician_to_assert["agenda"]["working_hours"] == [
        {
            "day_of_week": number_of_day_of_week,
            "start_time": another_physician_information["agenda"][
                str(number_of_day_of_week)
            ]["start"],
            "finish_time": another_physician_information["agenda"][
                str(number_of_day_of_week)
            ]["finish"],
        }
    ]


def test_get_physicians_by_specialty_with_no_authorization_header_returns_401_code():
    response_to_get_physicians_by_specialty_endpoint = client.get(
        f"/physicians/specialty/{specialties[0]}"
    )

    assert response_to_get_physicians_by_specialty_endpoint.status_code == 401
    assert (
        response_to_get_physicians_by_specialty_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_get_physicians_by_specialty_with_empty_authorization_header_returns_401_code():
    response_to_get_physicians_by_specialty_endpoint = client.get(
        f"/physicians/specialty/{specialties[0]}",
        headers={"Authorization": ""},
    )

    assert response_to_get_physicians_by_specialty_endpoint.status_code == 401
    assert (
        response_to_get_physicians_by_specialty_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_get_physicians_by_specialty_with_empty_bearer_token_returns_401_code():
    response_to_get_physicians_by_specialty_endpoint = client.get(
        f"/physicians/specialty/{specialties[0]}",
        headers={"Authorization": f"Bearer "},
    )

    assert response_to_get_physicians_by_specialty_endpoint.status_code == 401
    assert (
        response_to_get_physicians_by_specialty_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_get_physicians_by_specialty_with_non_bearer_token_returns_401_code():
    response_from_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_get_physicians_by_specialty_endpoint = client.get(
        f"/physicians/specialty/{specialties[0]}",
        headers={"Authorization": response_from_login_endpoint.json()["token"]},
    )

    assert response_to_get_physicians_by_specialty_endpoint.status_code == 401
    assert (
        response_to_get_physicians_by_specialty_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_get_physicians_by_specialty_with_invalid_bearer_token_returns_401_code():
    response_to_get_physicians_by_specialty_endpoint = client.get(
        f"/physicians/specialty/{specialties[0]}",
        headers={"Authorization": "Bearer smth"},
    )

    assert response_to_get_physicians_by_specialty_endpoint.status_code == 401
    assert (
        response_to_get_physicians_by_specialty_endpoint.json()["detail"]
        == "User must be logged in"
    )


def test_valid_request_to_get_physicians_endpoint_for_unexistant_specialty_returns_an_empty_list():
    response_from_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_to_get_physicians_endpoint = client.get(
        "/physicians/specialty/invalidspecialty",
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert len(response_to_get_physicians_endpoint.json()["physicians"]) == 0
