import pytest
from datetime import datetime, timedelta
from firebase_admin import auth, firestore
from app.main import app
from fastapi.testclient import TestClient
import requests
from unittest.mock import patch
import time

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

initial_admin_information = {
    "email": "testinitialadminfordenial@kmk.com",
    "password": "verySecurePassword123",
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
def create_initial_admin_and_then_delete_him():
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


# def test_add_specialty_updates_document_in_firestore():
#     specialties_before_update = ( db.collection("specialties").get())

#     pytest.initial_admin_bearer = client.post(
#         "/specialties/add/aNewSpecialty",
#         headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
#     )
#     specialties_after_update = ( db.collection("specialties").get())
#     assert len(specialties_before_update) + 1 == len(specialties_after_update)
#     assert "aNewSpecialty" in specialties_after_update


def test_add_specialty_updates_document_in_firestore_in_lowercase():
    specialties_before_update = db.collection("specialties").get()
    new_specialty = "aNewSpecialty"
    client.post(
        f"/specialties/add/{new_specialty}",
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )
    specialties_after_update = db.collection("specialties").get()

    # Verificar si el nuevo nombre "aNewSpecialty" está presente en los datos de los documentos
    new_specialty_added = False
    for doc in specialties_after_update:
        data = doc.to_dict()
        if "name" in data and data["name"] == new_specialty.lower():
            new_specialty_added = True
            break

    assert len(specialties_before_update) + 1 == len(specialties_after_update)
    assert new_specialty_added


def test_delete_specialty_updates_document_in_firestore():
    mocked_response = requests.Response()
    mocked_response.status_code = 200
    with patch("requests.post", return_value=mocked_response) as mocked_request:
        client.delete(
            f"/specialties/delete/{specialties[0]}",
            headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
        )
    print("*******")
    assert db.collection("appointments").document(specialties[0]).get().exists == False


def test_add_specialty_with_repeated_name_returns_400_code_and_detail():
    response_from_add_specialty_endpoint = client.post(
        f"/specialties/add/{specialties[1].upper()}",
        headers={"Authorization": f"Bearer {pytest.initial_admin_bearer}"},
    )

    assert response_from_add_specialty_endpoint.status_code == 400
    assert (
        response_from_add_specialty_endpoint.json()["detail"]
        == "La especialidad ya existe"
    )
