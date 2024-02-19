import pytest
from firebase_admin import auth, firestore
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

db = firestore.client()

a_KMK_user_information = {
    "display_name": "KMK Test User",
    "email": "loginTestUser@kmk.com",
    "email_verified": True,
    "password": "verySecurePassword123",
}

a_pending_KMK_physician_information = {
    "role": "physician",
    "first_name": "Physician Test User Register 1",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": "surgeon",
    "email": "testphysician1@kmk.com",
    "approved": "pending",
    "agenda": {"1": {"start": 8, "finish": 18.5}},
}


an_approved_KMK_physician_information = {
    "role": "physician",
    "first_name": "Physician Test User Register 1",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": "surgeon",
    "email": "testphysician2@kmk.com",
    "approved": "approved",
    "agenda": {"start": 8, "finish": 18.5},
}

a_denied_KMK_physician_information = {
    "role": "physician",
    "first_name": "Physician Test User Register 1",
    "last_name": "Test Last Name",
    "tuition": "777777",
    "specialty": "surgeon",
    "email": "testphysician3@kmk.com",
    "approved": "denied",
    "agenda": {"start": 8, "finish": 18.5},
}


@pytest.fixture(scope="module", autouse=True)
def create_test_user():
    created_user = auth.create_user(**a_KMK_user_information)
    a_KMK_user_information["uid"] = created_user.uid
    yield
    auth.delete_user(a_KMK_user_information["uid"])


@pytest.fixture(scope="module", autouse=True)
def create_pending_test_physician_and_then_delete_him():
    created_user = auth.create_user(
        **{
            "email": a_pending_KMK_physician_information["email"],
            "password": "verySecurePassword123",
        }
    )
    pytest.a_pending_phisician_uid = created_user.uid
    db.collection("physicians").document(pytest.a_pending_phisician_uid).set(
        {**a_pending_KMK_physician_information, "id": pytest.a_pending_phisician_uid}
    )
    yield
    auth.delete_user(pytest.a_pending_phisician_uid)
    db.collection("physicians").document(pytest.a_pending_phisician_uid).delete()


@pytest.fixture(scope="module", autouse=True)
def create_approved_test_physician_and_then_delete_him():
    created_user = auth.create_user(
        **{
            "email": an_approved_KMK_physician_information["email"],
            "password": "verySecurePassword123",
        }
    )
    pytest.an_approved_phisician_uid = created_user.uid
    db.collection("physicians").document(pytest.an_approved_phisician_uid).set(
        {
            **an_approved_KMK_physician_information,
            "id": pytest.an_approved_phisician_uid,
        }
    )
    yield
    auth.delete_user(pytest.an_approved_phisician_uid)
    db.collection("physicians").document(pytest.an_approved_phisician_uid).delete()


@pytest.fixture(scope="module", autouse=True)
def create_denied_test_physician_and_then_delete_him():
    created_user = auth.create_user(
        **{
            "email": a_denied_KMK_physician_information["email"],
            "password": "verySecurePassword123",
        }
    )
    pytest.a_denied_phisician_uid = created_user.uid
    db.collection("physicians").document(pytest.a_denied_phisician_uid).set(
        {**a_denied_KMK_physician_information, "id": pytest.a_denied_phisician_uid}
    )
    yield
    auth.delete_user(pytest.a_denied_phisician_uid)
    db.collection("physicians").document(pytest.a_denied_phisician_uid).delete()


def test_Login_With_Valid_Credentials_Returns_A_200_Code():
    response_to_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )

    assert response_to_login_endpoint.status_code == 200


def test_Login_With_Valid_Credentials_Returns_A_Token():
    response_to_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )

    assert response_to_login_endpoint.json().get("token") != None
    assert type(response_to_login_endpoint.json()["token"]) == str


def test_Returned_Bearer_Is_Valid():
    response_to_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )

    bearer = response_to_login_endpoint.json()["token"]
    assert type(auth.verify_id_token(bearer)) == dict


def test_Login_With_Invalid_Email_Credential_Returns_A_400_Code_And_Message():
    response_to_login_endpoint = client.post(
        "/users/login",
        json={
            "email": "invalid@email.com",
            "password": a_KMK_user_information["password"],
        },
    )

    assert response_to_login_endpoint.status_code == 400
    assert (
        response_to_login_endpoint.json()["detail"] == "Invalid email and/or password"
    )


def test_Login_With_Invalid_Password_Credential_Returns_A_400_Code_And_Message():
    response_to_login_endpoint = client.post(
        "/users/login",
        json={"email": a_KMK_user_information["email"], "password": "invalidPassword"},
    )

    assert response_to_login_endpoint.status_code == 400
    assert (
        response_to_login_endpoint.json()["detail"] == "Invalid email and/or password"
    )


def test_Invalid_Email_Format_For_Login_Returns_A_422_Code():
    response_to_login_endpoint = client.post(
        "/users/login",
        json={"email": "invalidEmail@format", "password": "aPassword"},
    )

    assert response_to_login_endpoint.status_code == 422
    assert response_to_login_endpoint.json()["detail"] == "Invalid input format"


def test_Loggin_Endpoint_Returns_A_403_Code_And_Message_If_User_Is_Logged_In():
    response_to_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )

    bearer = response_to_login_endpoint.json()["token"]

    response_to_second_request_to_login_endpoint = client.post(
        "/users/login",
        headers={"Authorization": f"Bearer {bearer}"},
        json={
            "email": a_KMK_user_information["email"],
            "password": a_KMK_user_information["password"],
        },
    )

    assert response_to_second_request_to_login_endpoint.status_code == 403
    assert (
        response_to_second_request_to_login_endpoint.json()["detail"]
        == "User has already logged in"
    )


def test_an_approved_phisician_Login_With_Valid_Credentials_Returns_A_200_Code():
    response_to_login_endpoint = client.post(
        "/users/login",
        json={
            "email": an_approved_KMK_physician_information["email"],
            "password": "verySecurePassword123",
        },
    )

    assert response_to_login_endpoint.status_code == 200


def test_a_pending_phisician_Login_With_Valid_Credentials_Returns_A_403_Code_and_detail():
    response_to_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_pending_KMK_physician_information["email"],
            "password": "verySecurePassword123",
        },
    )

    assert response_to_login_endpoint.status_code == 403
    assert (
        response_to_login_endpoint.json()["detail"]
        == "Account has to be approved by admin"
    )


def test_a_denied_phisician_Login_With_Valid_Credentials_Returns_A_403_Code_and_detail():
    response_to_login_endpoint = client.post(
        "/users/login",
        json={
            "email": a_denied_KMK_physician_information["email"],
            "password": "verySecurePassword123",
        },
    )

    assert response_to_login_endpoint.status_code == 403
    assert response_to_login_endpoint.json()["detail"] == "Account is not approved"
