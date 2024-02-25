import requests
import json
import os
from dotenv import load_dotenv
from typing import Union, Annotated

from fastapi import APIRouter, status, Depends, Body
from fastapi.responses import JSONResponse

from app.models.requests.UserRequests import (
    UserLoginRequest,
    PatientRegisterRequest,
    PhysicianRegisterRequest,
    ChangePasswordRequest,
)
from app.models.responses.UserResponses import (
    SuccessfulLoginResponse,
    LoginErrorResponse,
    SuccessfullRegisterResponse,
    RegisterErrorResponse,
    UserRolesResponse,
    UserProfileErrorResponse,
    UserInfoErrorResponse,
    IsLoggedInResponse,
    SuccessfullChangePasswordResponse,
    ChangePasswordErrorResponse,
)
from app.models.responses.ScoreResponses import (
    SuccessfullLoadScoreResponse,
    ScoreErrorResponse,
    SuccessfullScoreResponse,
    PendingScoresErrorResponse,
    PendingScoresResponse,
)
from app.models.requests.ScoreRequests import (
    LoadScoreRequest,
)
from app.models.responses.PatientResponses import PatientResponse
from app.models.responses.PhysicianResponses import CompletePhysicianResponse

from app.models.entities.Auth import Auth
from app.models.entities.Patient import Patient
from app.models.entities.Physician import Physician
from app.models.entities.Admin import Admin
from app.models.entities.Record import Record
from app.models.entities.Score import Score
from app.models.entities.Appointment import Appointment

from firebase_admin import firestore, auth

db = firestore.client()

load_dotenv()

router = APIRouter(
    prefix="/users", tags=["Users"], responses={404: {"description": "Not found"}}
)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=SuccessfulLoginResponse,
    responses={
        400: {"model": LoginErrorResponse},
        403: {"model": LoginErrorResponse},
        500: {"model": LoginErrorResponse},
    },
)
async def login_user(
    user_login_request: UserLoginRequest,
    token=Depends(Auth.has_bearer_token),
):
    """
    Login a user.

    This will allow for unauthenticated clients to log into the system.

    This path operation will:

    * Login the user, performing validations on data received and on its validity.
    * Return the users Bearer token if login is successful.
    * Throw an error if login fails.
    """
    url = os.environ.get("LOGIN_URL")
    login_response = requests.post(
        url,
        json={
            "email": user_login_request.email,
            "password": user_login_request.password,
            "return_secure_token": True,
        },
        params={"key": os.environ.get("API_KEY")},
    )
    if login_response.status_code == 400:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid email and/or password"},
        )
    elif login_response.status_code == 200:
        if Physician.is_physician(login_response.json()["localId"]):
            physician = Physician.get_by_id(login_response.json()["localId"])
            if physician.approved == "denied" or physician.approved == "blocked":
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Account is not approved"},
                )
            elif physician.approved == "pending":
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Account has to be approved by admin"},
                )
        return {"token": login_response.json()["idToken"]}
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessfullRegisterResponse,
    responses={
        400: {"model": RegisterErrorResponse},
        403: {"model": RegisterErrorResponse},
        500: {"model": RegisterErrorResponse},
    },
)
async def register(
    register_request: Annotated[
        Union[PatientRegisterRequest, PhysicianRegisterRequest],
        Body(discriminator="role"),
    ]
):
    """
    Register a user.
    This will allow users to register on the platform.
    This path operation will:
    * Register users, performing validations on data received and on its validity.
    * If the user is a patient, it's record will be created.
    * Throw an error if registration fails.
    """
    try:
        auth.get_user_by_email(register_request.email)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Esta cuenta ya fue registrada"},
        )
    except:
        print("[+] User doesnt exist in authentication")

    try:
        register_response = auth.create_user(
            **{
                "email": register_request.email,
                "password": register_request.password,
            }
        )
        auth_uid = register_response.uid
    except:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"},
        )

    del register_request.password
    if register_request.role == "patient":
        patient_data = {
            key: value
            for key, value in register_request.model_dump().items()
            if key not in ["birth_date", "gender", "blood_type"]
        }
        patient = Patient(**patient_data, id=auth_uid)
        patient.create()
        record_data = {
            key: value
            for key, value in register_request.model_dump().items()
            if key not in ["role", "email"]
        }
        record = Record(**record_data, id=auth_uid)
        record.create()
    else:
        physician = Physician(
            **register_request.model_dump(exclude_none=True), id=auth_uid
        )
        physician.create()
    requests.post(
        os.environ.get("NOTIFICATIONS_API_URL") + "/emails/send",
        json={
            "type": (
                "PATIENT_REGISTERED_ACCOUNT"
                if register_request.role == "patient"
                else "PHYSICIAN_REGISTERED_ACCOUNT"
            ),
            "data": {
                "name": register_request.first_name,
                "last_name": register_request.last_name,
                "email": register_request.email,
            },
        },
    )
    return {"message": "Successfull registration"}


@router.get(
    "/role",
    status_code=status.HTTP_200_OK,
    response_model=UserRolesResponse,
    responses={
        401: {"model": UserProfileErrorResponse},
        403: {"model": UserProfileErrorResponse},
        500: {"model": UserProfileErrorResponse},
    },
)
def get_user_roles(user_id=Depends(Auth.is_logged_in)):
    """
    Get a users roles.

    This will return the users roles.

    This path operation will:

    * Return the users roles.
    * Throw an error if users role retrieving process fails.
    """
    roles = []
    try:
        if Admin.is_admin(user_id):
            roles.append("admin")
        if Patient.is_patient(user_id):
            roles.append("patient")
        if Physician.is_physician(user_id):
            roles.append("physician")
        return {"roles": roles}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.get(
    "/user-info",
    status_code=status.HTTP_200_OK,
    response_model=Union[CompletePhysicianResponse, PatientResponse],
    responses={
        401: {"model": UserInfoErrorResponse},
        403: {"model": UserInfoErrorResponse},
        500: {"model": UserInfoErrorResponse},
    },
)
def get_user_info(user_id=Depends(Auth.is_logged_in)):
    """
    Get a user info.

    This will return the user info.

    This path operation will:

    * Return the user info.
    * Throw an error if user info retrieving process fails.
    """
    try:
        if Patient.get_by_id(user_id):
            return PatientResponse(**Patient.get_by_id(user_id))
        if Physician.get_by_id(user_id):
            return CompletePhysicianResponse(**Physician.get_by_id(user_id).__dict__)
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
            )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.get(
    "/is-logged-in", status_code=status.HTTP_200_OK, response_model=IsLoggedInResponse
)
def is_logged_in(token=Depends(Auth.get_bearer_token)):
    """
    Get a users logged in status.

    This will return the users logged in status.

    This path operation will:

    * Return True if user is logged in.
    * Return False if user is not logged in.
    """
    if token:
        try:
            auth.verify_id_token(token.credentials)
            return {"is_logged_in": True}
        except:
            return {"is_logged_in": False}
    return {"is_logged_in": False}


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    response_model=SuccessfullChangePasswordResponse,
    responses={
        400: {"model": ChangePasswordErrorResponse},
        401: {"model": ChangePasswordErrorResponse},
    },
)
def change_password(
    change_password_request: ChangePasswordRequest, uid=Depends(Auth.is_logged_in)
):
    """
    Change users password.

    This will allow authenticated users to change their passwords.

    This path operation will:

    * Change users password.
    * Raise an error if password change fails.
    """
    user = auth.get_user(uid)
    url = os.environ.get("LOGIN_URL")
    print(user.email, change_password_request.current_password)
    login_response = requests.post(
        url,
        json={
            "email": user.email,
            "password": change_password_request.current_password,
        },
        params={"key": os.environ.get("API_KEY")},
    )
    if login_response.status_code == 200:
        auth.update_user(uid, **{"password": change_password_request.new_password})
        requests.post(
            os.environ.get("NOTIFICATIONS_API_URL") + "/emails/send",
            json={
                "type": "PASSWORD_CHANGED",
                "data": {
                    "email": user.email,
                },
            },
        )
        return {"message": "Contraseña cambiada exitosamente"}
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Contraseña actual incorrecta"},
    )


@router.post(
    "/add-score",
    status_code=status.HTTP_200_OK,
    response_model=SuccessfullLoadScoreResponse,
    responses={
        400: {"model": ScoreErrorResponse},
        401: {"model": ScoreErrorResponse},
    },
)
def add_score(add_score_request: LoadScoreRequest, uid=Depends(Auth.is_logged_in)):
    """
    Add score.

    This will allow authenticated users to add scores.

    This path operation will:

    * Add score.
    * Raise an error if password change fails.
    """
    add_score_request = add_score_request.model_dump(exclude_none=True)
    appointment_id = add_score_request.pop("appointment_id")
    try:
        if Patient.get_by_id(uid):
            Score.add_physician_score(add_score_request, appointment_id)
            Appointment.update_rated_status(appointment_id)
            Appointment.remove_pending_to_score_patient_register(uid, appointment_id)
            return {"message": "Scores added successfully"}
        if Physician.get_by_id(uid):
            Score.add_patient_score(add_score_request, appointment_id)
            return {"message": "Scores added successfully"}
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
            )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.get(
    "/score/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessfullScoreResponse,
    responses={
        400: {"model": ScoreErrorResponse},
        401: {"model": ScoreErrorResponse},
    },
)
def show_score(
    user_id: str,
    # uid=Depends(Auth.is_logged_in)
):
    """
    Show scores from a physician.

    This will allow authenticated users to see physician scores.

    This path operation will:

    * Show physician scores.
    * Raise an error if password change fails.
    """
    try:
        if Patient.is_patient(user_id):
            appointments = Appointment.get_all_rated_appointments_for_patient_with(
                user_id
            )
            score_sums = {
                "puntuality": 0,
                "communication": 0,
                "attendance": 0,
                "treat": 0,
                "cleanliness": 0,
            }
            score_counts = {
                "puntuality": 0,
                "communication": 0,
                "attendance": 0,
                "treat": 0,
                "cleanliness": 0,
            }
            scores = []
            for appt in appointments:
                score = Score.get_by_id(appt["id"])
                scores.append(score["patient_score"][0])

        if Physician.is_physician(user_id):
            appointments = Appointment.get_all_rated_appointments_for_physician_with(
                user_id
            )
            score_sums = {
                "puntuality": 0,
                "attention": 0,
                "cleanliness": 0,
                "availability": 0,
                "price": 0,
                "communication": 0,
            }
            score_counts = {
                "puntuality": 0,
                "attention": 0,
                "cleanliness": 0,
                "availability": 0,
                "price": 0,
                "communication": 0,
            }
            scores = []
            for appt in appointments:
                score = Score.get_by_id(appt["id"])
                if len(score["physician_score"]) > 0:
                    scores.append(score["physician_score"][0])

        for score in scores:
            for key, value in score.items():
                if key in score_sums:
                    score_sums[key] += value
                    score_counts[key] += 1

        score_averages = {}
        for key, value in score_sums.items():
            if score_counts[key] > 0:
                score_averages[key] = value / score_counts[key]
            else:
                score_averages[key] = "No hay reviews"

        print(score_averages)

        return {"score_metrics": score_averages}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.get(
    "/patient-pending-scores",
    status_code=status.HTTP_200_OK,
    response_model=PendingScoresResponse,
    responses={
        400: {"model": PendingScoresErrorResponse},
        401: {"model": PendingScoresErrorResponse},
    },
)
def pending_scores(user_id=Depends(Auth.is_logged_in)):
    """
    Get pending scores for a patient.

    This will allow us to check if a patient has pending scores.

    This path operation will:

    * Check for pending scores.
    * Return a list of pending scores.
    * Raise an error if password change fails.
    """
    try:
        appointments = Appointment.get_all_closed_appointments_for_patient_with(user_id)
        pending_scores = []
        for appointment in appointments:
            physician = Physician.get_by_id(appointment["physician_id"])
            physician_info = {
                "first_name": physician["first_name"],
                "last_name": physician["last_name"],
                "specialty": physician["specialty"],
            }
            appointment.update(physician_info)
            pending_scores.append(appointment)

        return {"pending_scores": pending_scores}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
