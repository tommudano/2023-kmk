import pytest
from firebase_admin import firestore, auth
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

a_KMK_user_information = {
    "display_name": "KMK Test User",
    "email": "getSpecialtiesTestUser@kmk.com",
    "email_verified": True,
    "password": "verySecurePassword123",
}


@pytest.fixture(scope="module", autouse=True)
def create_test_user():
    created_user = auth.create_user(**a_KMK_user_information)
    a_KMK_user_information["uid"] = created_user.uid
    yield
    auth.delete_user(a_KMK_user_information["uid"])


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


def test_get_specialties_endpoint_returns_a_200_code():
    response_from_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_from_get_specialties_endpoint = client.get(
        "/specialties",
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert response_from_get_specialties_endpoint.status_code == 200


def test_get_specialties_endpoint_returns_a_list():
    response_from_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_from_get_specialties_endpoint = client.get(
        "/specialties",
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )

    assert type(response_from_get_specialties_endpoint.json()["specialties"]) == list


def test_get_specialties_endpoint_returns_the_list_of_all_specialties_ordered_alphabetically():
    response_from_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )
    response_from_get_specialties_endpoint = client.get(
        "/specialties",
        headers={
            "Authorization": f"Bearer {response_from_login_endpoint.json()['token']}"
        },
    )
    specialties.sort()
    assert response_from_get_specialties_endpoint.json()["specialties"] == specialties


def test_get_specialties_with_no_authorization_header_returns_200_code():
    response_to_get_specialties_endpoint = client.get("/specialties")

    assert response_to_get_specialties_endpoint.status_code == 200


def test_get_specialties_with_no_specialties_created_returns_an_empty_list():
    specilaties_doc = db.collection("specialties").list_documents()
    for specialty_doc in specilaties_doc:
        specialty_doc.delete()
    response_to_get_specialties_endpoint = client.get("/specialties")
    assert response_to_get_specialties_endpoint.json()["specialties"] == []
