import os
import requests
import json
from dotenv import load_dotenv
from firebase_admin import auth
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from app.models.entities.Specialty import Specialty
from app.models.entities.Physician import Physician
from app.models.entities.Auth import Auth
from app.models.entities.Admin import Admin
from app.models.responses.AdminResponses import (
    SuccessfullAdminRegistrationResponse,
    SuccessfulSpecialtyUpdateValueResponse,
    AdminRegistrationError,
    AdminUserResponse,
    GetAdminUserError,
)
from app.models.requests.AdminRequests import (
    AdminRegisterRequest,
    SpecialtyUpdateValueRequest,
)
from app.models.responses.ValidationResponses import (
    SuccessfullValidationResponse,
    ValidationErrorResponse,
    AllPendingValidationsResponse,
    GetPendingValidationsError,
    AllWorkingPhysiciansResponse,
    GetWorkingPhysiciansError,
    AllBlockedPhysiciansResponse,
    GetBlockedPhysiciansError,
    AdminSpecialtiesGetError,
    AdminSpecialtiesPutError,
    SuccessfulAdminSpecialtiesGetResponse,
)

load_dotenv()

router = APIRouter(
    prefix="/admin",
    tags=["Admins"],
    responses={404: {"description": "Not found"}},
)

with open("credentials/client.json") as fp:
    firebase_client_config = json.loads(fp.read())


@router.post(
    "/approve-physician/{physician_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessfullValidationResponse,
    responses={
        400: {"model": ValidationErrorResponse},
        401: {"model": ValidationErrorResponse},
        403: {"model": ValidationErrorResponse},
        500: {"model": ValidationErrorResponse},
    },
)
async def approve_physician(physician_id: str, uid=Depends(Auth.is_admin)):
    """
    Validate a physician.

    This will allow superusers to approve physicians.

    This path operation will:

    * Validate a physician.
    * Change the _approved_ field from Physicians from _pending_ to _approved_.
    * Throw an error if the validation fails.
    """
    try:
        if not Physician.is_physician(physician_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Can only approve physicians"},
            )
        Admin.approve_physician(physician_id)
        physician = Physician.get_by_id(physician_id)
        requests.post(
            os.environ.get("NOTIFICATIONS_API_URL"),
            json={
                "type": "PHYSICIAN_APPROVED_ACCOUNT",
                "data": {
                    "email": physician["email"],
                },
            },
        )
        return {"message": "Physician validated successfully"}
    except:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.post(
    "/deny-physician/{physician_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessfullValidationResponse,
    responses={
        400: {"model": ValidationErrorResponse},
        401: {"model": ValidationErrorResponse},
        403: {"model": ValidationErrorResponse},
        500: {"model": ValidationErrorResponse},
    },
)
async def deny_physician(physician_id: str, uid=Depends(Auth.is_admin)):
    """
    Validate a physician.

    This will allow superusers to deny physicians.

    This path operation will:

    * Validate a physician.
    * Change the _approved_ field from Physicians from _pending_ to _denied_.
    * Throw an error if the validation fails.
    """
    try:
        if not Physician.is_physician(physician_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Can only deny physicians"},
            )
        physician = Physician.get_by_id(physician_id)
        Admin.deny_physician(physician_id)
        requests.post(
            os.environ.get("NOTIFICATIONS_API_URL"),
            json={
                "type": "PHYSICIAN_DENIED_ACCOUNT",
                "data": {
                    "email": physician["email"],
                },
            },
        )
        return {"message": "Physician denied successfully"}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.post(
    "/unblock-physician/{physician_id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessfullValidationResponse,
    responses={
        400: {"model": ValidationErrorResponse},
        401: {"model": ValidationErrorResponse},
        403: {"model": ValidationErrorResponse},
        500: {"model": ValidationErrorResponse},
    },
)
async def unblock_physician(physician_id: str, uid=Depends(Auth.is_admin)):
    """
    Validate a physician.

    This will allow superusers to unblock blocked physicians.

    This path operation will:

    * Validate a physician.
    * Change the _approved_ field from Physicians from _denied_ to _pending_.
    * Throw an error if the validation fails.
    """
    try:
        if not Physician.is_blocked_physician(physician_id):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Can only unblock blocked physicians"},
            )
        physician = Physician.get_blocked_by_id(physician_id)
        Admin.unblock_physician(physician)
        requests.post(
            os.environ.get("NOTIFICATIONS_API_URL"),
            json={
                "type": "PHYSICIAN_UNBLOCKED_ACCOUNT",
                "data": {
                    "email": physician["email"],
                },
            },
        )
        return {"message": "Physician unblocked successfully"}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.get(
    "/physicians-pending",
    status_code=status.HTTP_200_OK,
    response_model=AllPendingValidationsResponse,
    responses={
        401: {"model": GetPendingValidationsError},
        403: {"model": GetPendingValidationsError},
        500: {"model": GetPendingValidationsError},
    },
)
def get_all_pending_validations(uid=Depends(Auth.is_admin)):
    """
    Get all physicians pending approval.

    This will allow superusers to retrieve all pending validations.

    This path operation will:

    * Return all of physicians pending validations.
    * Throw an error if appointment retrieving fails.
    """
    try:
        physicians_to_validate = Physician.get_pending_physicians()
        return {"physicians_pending_validation": physicians_to_validate}
    except:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.get(
    "/physicians-working",
    status_code=status.HTTP_200_OK,
    response_model=AllWorkingPhysiciansResponse,
    responses={
        401: {"model": GetWorkingPhysiciansError},
        403: {"model": GetWorkingPhysiciansError},
        500: {"model": GetWorkingPhysiciansError},
    },
)
def get_all_working_physicians(uid=Depends(Auth.is_admin)):
    """
    Get all working physicians.

    This will allow superusers to retrieve all working physicians.

    This path operation will:

    * Return all of the working physicians.
    * Throw an error if appointment retrieving fails.
    """
    try:
        physicians_working = Physician.get_physicians_working()
        return {"physicians_working": physicians_working}
    except:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.get(
    "/physicians-blocked",
    status_code=status.HTTP_200_OK,
    response_model=AllBlockedPhysiciansResponse,
    responses={
        401: {"model": GetBlockedPhysiciansError},
        403: {"model": GetBlockedPhysiciansError},
        500: {"model": GetBlockedPhysiciansError},
    },
)
def get_all_blocked_physicians(uid=Depends(Auth.is_admin)):
    """
    Get all blocked physicians.

    This will allow superusers to retrieve all blocked physicians.

    This path operation will:

    * Return all of the blocked physicians.
    * Throw an error if appointment retrieving fails.
    """
    try:
        physicians_blocked = Physician.get_physicians_denied()
        return {"physicians_blocked": physicians_blocked}
    except:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessfullAdminRegistrationResponse,
    responses={
        400: {"model": AdminRegistrationError},
        401: {"model": AdminRegistrationError},
        403: {"model": AdminRegistrationError},
        500: {"model": AdminRegistrationError},
    },
)
def regsiter_admin(
    admin_resgister_request: AdminRegisterRequest, uid=Depends(Auth.is_admin)
):
    """
    Register an admin.

    This will allow superusers to register admins.

    This path operation will:

    * Register an admin.
    * Throw an error if the registration fails.
    """
    url = os.environ.get("REGISTER_URL")
    try:
        auth.get_user_by_email(admin_resgister_request.email)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Esta cuenta ya fue registrada"},
        )
    except:
        print("[+] User doesnt exist in authentication")

    register_response = requests.post(
        url,
        json={
            "email": admin_resgister_request.email,
            "password": admin_resgister_request.password,
            "returnSecureToken": True,
        },
        params={"key": firebase_client_config["apiKey"]},
    )
    if register_response.status_code != 200:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
    auth_uid = register_response.json()["localId"]

    del admin_resgister_request.password
    admin = Admin(
        **admin_resgister_request.model_dump(), id=auth_uid, registered_by=uid
    )
    admin.create()
    return {"message": "Registro exitoso"}


@router.get(
    "/specialties",
    status_code=status.HTTP_200_OK,
    response_model=SuccessfulAdminSpecialtiesGetResponse,
    responses={
        400: {"model": AdminSpecialtiesGetError},
        401: {"model": AdminSpecialtiesGetError},
        403: {"model": AdminSpecialtiesGetError},
        500: {"model": AdminSpecialtiesGetError},
    },
)
def get_specialties_with_physician_count(uid=Depends(Auth.is_admin)):
    specialies_with_physician_count = Admin.get_specialies_with_physician_count()
    return {"specialties": specialies_with_physician_count}


@router.put(
    "/specialties/value/{specialty_name}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessfulSpecialtyUpdateValueResponse,
    responses={
        401: {"model": AdminSpecialtiesPutError},
        403: {"model": AdminSpecialtiesPutError},
        500: {"model": AdminSpecialtiesPutError},
    },
)
def update_specialty_value(
    specialty_name: str,
    specialty_update_value_request: SpecialtyUpdateValueRequest,
    uid=Depends(Auth.is_admin),
):
    """
    Update specialtie's value.

    This will allow superusers to modify the value of a given specialty.

    This path operation will:

    * Update a specific specialties value.
    * Throw an error if the update fails.
    """
    Specialty.update_value(specialty_name, specialty_update_value_request.value)
    return {"message": "Successfull update"}


@router.get(
    "/user-info",
    status_code=status.HTTP_200_OK,
    response_model=AdminUserResponse,
    responses={
        401: {"model": GetAdminUserError},
        403: {"model": GetAdminUserError},
        500: {"model": GetAdminUserError},
    },
)
def get_admin_user_info(user_id=Depends(Auth.is_admin)):
    try:
        return Admin.get_by_id(user_id)
    except:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
