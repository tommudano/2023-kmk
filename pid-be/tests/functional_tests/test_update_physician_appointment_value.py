import pytest
import time
from datetime import datetime
from firebase_admin import firestore, auth
from app.main import app
from fastapi.testclient import TestClient
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

today_date = datetime.fromtimestamp(round(time.time()))
number_of_day_of_week = int(today_date.date().strftime("%w"))

a_physician_information = {
    "role": "physician",
    "first_name": "Doc",
    "last_name": "Docson",
    "email": "doctor@getbyspecialty.com",
    "specialty": specialties[0],
    "agenda": {str(number_of_day_of_week): {"start": 8, "finish": 18.5}},
    "approved": "approved",
    "tuition": "A111",
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


@pytest.fixture(scope="module", autouse=True)
def load_and_delete_physicians(load_and_delete_specialties):
    created_user = auth.create_user(
        **{"email": a_physician_information["email"], "password": "verystrongpassword"}
    )
    pytest.physician_id = created_user.uid
    db.collection("physicians").document(pytest.physician_id).set(
        {**a_physician_information, "id": pytest.physician_id}
    )

    yield
    auth.delete_user(pytest.physician_id)
    db.collection("physicians").document(pytest.physician_id).delete()


@pytest.fixture(scope="module", autouse=True)
def log_in_physician(load_and_delete_physicians):
    pytest.physician_bearer_token = client.post(
        "/users/login",
        json={
            "email": a_physician_information["email"],
            "password": "verystrongpassword",
        },
    ).json()["token"]
    yield


def test_put_to_update_value_returns_200_code_and_message():
    response_from_update_value_endpoint = client.put(
        "/physicians/value",
        json={"new_value": 4500},
        headers={"Authorization": f"Bearer {pytest.physician_bearer_token}"},
    )

    assert response_from_update_value_endpoint.status_code == 200
    assert (
        response_from_update_value_endpoint.json()["message"]
        == "Valor actualizado correctamente"
    )


def test_put_to_update_value_updates_value_in_firestore():
    client.put(
        "/physicians/value",
        json={"new_value": 4500},
        headers={"Authorization": f"Bearer {pytest.physician_bearer_token}"},
    )

    assert (
        db.collection("physicians")
        .document(pytest.physician_id)
        .get()
        .to_dict()["appointment_value"]
        == 4500
    )


def test_registration_and_value_update_flow():
    physician_data = {
        "role": "physician",
        "first_name": "Physician Test User Register",
        "last_name": "Test Last Name",
        "tuition": "777777",
        "specialty": specialties[0],
        "email": "testphysicianforregister@kmk.com",
        "password": "verySecurePassword123",
    }
    with patch("requests.post") as mocked_request:
        response_to_register_endpoint = client.post(
            "/users/register",
            json=physician_data,
        )
    assert response_to_register_endpoint.status_code == 201
    created_test_user_uid = auth.get_user_by_email(physician_data["email"]).uid
    db.collection("physicians").document(created_test_user_uid).update(
        {"approved": "approved"}
    )
    physician_logged_in_token = client.post(
        "/users/login",
        json={"email": physician_data["email"], "password": physician_data["password"]},
    ).json()["token"]
    physicians_user_data = client.get(
        "/users/user-info",
        headers={"Authorization": f"Bearer {physician_logged_in_token}"},
    ).json()
    assert physicians_user_data["appointment_value"] == 3500
    client.put(
        "/physicians/value",
        json={"new_value": 4500},
        headers={"Authorization": f"Bearer {physician_logged_in_token}"},
    )
    physicians_user_data = client.get(
        "/users/user-info",
        headers={"Authorization": f"Bearer {physician_logged_in_token}"},
    ).json()
    assert physicians_user_data["appointment_value"] == 4500
    auth.delete_user(created_test_user_uid)
    db.collection("physicians").document(created_test_user_uid).delete()


def test_update_appointment_value_with_no_authorization_header_returns_401_code():
    response_from_update_value_endpoint = client.put(
        "/physicians/value", json={"new_value": 4500}
    )

    assert response_from_update_value_endpoint.status_code == 401
    assert (
        response_from_update_value_endpoint.json()["detail"] == "User must be logged in"
    )


def test_update_appointment_value_with_empty_authorization_header_returns_401_code():
    response_from_update_value_endpoint = client.put(
        "/physicians/value",
        json={"new_value": 4500},
        headers={"Authorization": ""},
    )

    assert response_from_update_value_endpoint.status_code == 401
    assert (
        response_from_update_value_endpoint.json()["detail"] == "User must be logged in"
    )


def test_update_appointment_value_with_empty_bearer_token_returns_401_code():
    response_from_update_value_endpoint = client.put(
        "/physicians/value",
        json={"new_value": 4500},
        headers={"Authorization": f"Bearer "},
    )

    assert response_from_update_value_endpoint.status_code == 401
    assert (
        response_from_update_value_endpoint.json()["detail"] == "User must be logged in"
    )


def test_update_appointment_value_with_non_bearer_token_returns_401_code():
    response_from_update_value_endpoint = client.put(
        "/physicians/value",
        json={"new_value": 4500},
        headers={"Authorization": pytest.physician_id},
    )

    assert response_from_update_value_endpoint.status_code == 401
    assert (
        response_from_update_value_endpoint.json()["detail"] == "User must be logged in"
    )


def test_update_appointment_value_with_invalid_bearer_token_returns_401_code():
    response_from_update_value_endpoint = client.put(
        "/physicians/value",
        json={"new_value": 4500},
        headers={"Authorization": "Bearer smth"},
    )

    assert response_from_update_value_endpoint.status_code == 401
    assert (
        response_from_update_value_endpoint.json()["detail"] == "User must be logged in"
    )


def test_update_appointment_value_not_as_a_physician_returns_403_code():
    created_user = auth.create_user(
        **{
            "email": "anemail@test.com",
            "password": "apassword",
        }
    )
    user_uid = created_user.uid
    user_bearer = client.post(
        "/users/login",
        json={
            "email": "anemail@test.com",
            "password": "apassword",
        },
    ).json()["token"]
    response_from_update_value_endpoint = client.put(
        "/physicians/value",
        json={"new_value": 4500},
        headers={"Authorization": f"Bearer {user_bearer}"},
    )
    auth.delete_user(user_uid)
    assert response_from_update_value_endpoint.status_code == 403
    assert (
        response_from_update_value_endpoint.json()["detail"]
        == "Solo los medicos pueden actualizar el valor de sus consultas"
    )


def test_put_to_update_value_with_negative_amount_returns_422_code():
    response_from_update_value_endpoint = client.put(
        "/physicians/value",
        json={"new_value": -4500},
        headers={"Authorization": f"Bearer {pytest.physician_bearer_token}"},
    )

    assert response_from_update_value_endpoint.status_code == 422


def test_put_to_update_value_with_float_amount_returns_422_code():
    response_from_update_value_endpoint = client.put(
        "/physicians/value",
        json={"new_value": 4500.50},
        headers={"Authorization": f"Bearer {pytest.physician_bearer_token}"},
    )

    assert response_from_update_value_endpoint.status_code == 422


def test_put_to_update_value_with_value_grater_than_twice_the_amount_returns_400_code():
    response_from_update_value_endpoint = client.put(
        "/physicians/value",
        json={"new_value": 50000},
        headers={"Authorization": f"Bearer {pytest.physician_bearer_token}"},
    )

    assert response_from_update_value_endpoint.status_code == 400
    assert (
        response_from_update_value_endpoint.json()["detail"]
        == "El nuevo valor debe ser menor o igual al doble del valo que uso el administrador"
    )
