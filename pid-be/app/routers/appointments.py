import os
import requests
from datetime import datetime
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.models.entities.Physician import Physician
from app.models.entities.Patient import Patient
from app.models.entities.Auth import Auth
from app.models.entities.Appointment import Appointment
from app.models.entities.Score import Score
from app.models.requests.AppointmentRequests import (
    AppointmentCreationRequest,
    UpdateAppointmentRequest,
    CloseAppointmentRequest,
)
from app.models.responses.AppointmentResponses import (
    SuccessfulAppointmentCreationResponse,
    AppointmentCreationError,
    GetAppointmentError,
    AllAppointmentsResponse,
    SuccessfulAppointmentDeletionResponse,
    DeleteAppointmentError,
    SuccessfulAppointmentUpdateResponse,
    UpdateAppointmentError,
    SuccessfulAppointmentCloseResponse,
    CloseAppointmentError,
)

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessfulAppointmentCreationResponse,
    responses={
        400: {"model": AppointmentCreationError},
        401: {"model": AppointmentCreationError},
        500: {"model": AppointmentCreationError},
    },
)
async def create_appointment(
    appointment_creation_request: AppointmentCreationRequest,
    patient_id=Depends(Auth.is_logged_in),
):
    """
    Create an appointment.

    This will allow authenticated users to create appointments with their physician of choice.

    This path operation will:

    * Create an appointment.
    * Return the appointments id.
    * Throw an error if appointment creation fails.
    """
    appointment = Appointment(
        **{**appointment_creation_request.model_dump(), "patient_id": patient_id}
    )
    try:
        appointment_id = appointment.create()
        score = Score(
            appointment_id=appointment_id, patient_score=[], physician_score=[]
        )
        score.create()
        physician = Physician.get_by_id(appointment_creation_request.physician_id)
        patient = Patient.get_by_id(patient_id)
        date = datetime.fromtimestamp(appointment_creation_request.date)
        requests.post(
            os.environ.get("NOTIFICATIONS_API_URL"),
            json={
                "type": "PENDING_APPOINTMENT",
                "data": {
                    "email": physician.email,
                    "name": patient["first_name"],
                    "last_name": patient["last_name"],
                    "day": date.day,
                    "month": date.month,
                    "year": date.year,
                    "hour": date.hour,
                    "minute": date.minute,
                    "second": date.second,
                },
            },
        )
        return {"appointment_id": appointment_id}
    except HTTPException as http_exception:
        return JSONResponse(
            status_code=http_exception.status_code,
            content={"detail": http_exception.detail},
        )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=AllAppointmentsResponse,
    responses={
        401: {"model": GetAppointmentError},
        403: {"model": GetAppointmentError},
        500: {"model": GetAppointmentError},
    },
)
def get_all_appointments(uid=Depends(Auth.is_logged_in)):
    """
    Get all appointments.

    This will allow authenticated users to retrieve all their appointments.

    This path operation will:

    * Return all of users appointments ordered by date.
    * Throw an error if appointment retrieving fails.
    """
    try:
        appointments = Appointment.get_all_appointments_for_patient_with(uid)
        return {"appointments": appointments}
    except HTTPException as http_exception:
        raise http_exception
    except:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.get(
    "/patients-pending-appointments",
    status_code=status.HTTP_200_OK,
    response_model=AllAppointmentsResponse,
    responses={
        401: {"model": GetAppointmentError},
        403: {"model": GetAppointmentError},
        500: {"model": GetAppointmentError},
    },
)
def get_all_pending_appointments(uid=Depends(Auth.is_logged_in)):
    """
    Get all appointments.

    This will allow authenticated users to retrieve all their appointments.

    This path operation will:

    * Return all of users appointments ordered by date.
    * Throw an error if appointment retrieving fails.
    """
    try:
        appointments = Appointment.get_all_pending_appointments_for_patient_with(uid)
        return {"appointments": appointments}
    except HTTPException as http_exception:
        raise http_exception
    except:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.get(
    "/physician",
    status_code=status.HTTP_200_OK,
    response_model=AllAppointmentsResponse,
    responses={
        401: {"model": GetAppointmentError},
        403: {"model": GetAppointmentError},
        500: {"model": GetAppointmentError},
    },
)
def get_all_appointments_for_physician(uid=Depends(Auth.is_logged_in)):
    """
    Get all appointments.

    This will allow authenticated users to retrieve all their appointments.

    This path operation will:

    * Return all of users appointments ordered by date.
    * Throw an error if appointment retrieving fails.
    """
    try:
        appointments = Appointment.get_all_approved_appointments_for_physician_with(uid)
        print(appointments)
        return {"appointments": appointments}

    except HTTPException as http_exception:
        raise http_exception
    except:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessfulAppointmentDeletionResponse,
    responses={
        400: {"model": DeleteAppointmentError},
        401: {"model": DeleteAppointmentError},
        403: {"model": DeleteAppointmentError},
        500: {"model": DeleteAppointmentError},
    },
)
def delete_appointment_by_id(id: str, uid=Depends(Auth.is_logged_in)):
    """
    Delete an appointment.

    This will allow authenticated users to delete one of their appointments.

    This path operation will:

    * Delete an appointment.
    * Throw an error if appointment doesn't exist.
    * Throw an error if appointment doesn't belong to the authenticated user.
    * Throw an error if appointment retrieving fails.
    """
    try:
        appointment = Appointment.get_by_id(id)
        if not appointment or (
            appointment.physician_id != uid and appointment.patient_id != uid
        ):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid appointment id"},
            )
        appointment.delete()
        date = datetime.fromtimestamp(appointment.date)
        physician = Physician.get_by_id(appointment.physician_id)
        requests.post(
            os.environ.get("NOTIFICATIONS_API_URL"),
            json={
                "type": "CANCELED_APPOINTMENT",
                "data": {
                    "email": physician.email,
                    "day": date.day,
                    "month": date.month,
                    "year": date.year,
                    "hour": date.hour,
                    "minute": date.minute,
                    "second": date.second,
                },
            },
        )
        patient = Patient.get_by_id(appointment.patient_id)
        requests.post(
            os.environ.get("NOTIFICATIONS_API_URL"),
            json={
                "type": "CANCELED_APPOINTMENT",
                "data": {
                    "email": patient["email"],
                    "day": date.day,
                    "month": date.month,
                    "year": date.year,
                    "hour": date.hour,
                    "minute": date.minute,
                    "second": date.second,
                },
            },
        )
        return {"message": "Appointment cancelled successfully"}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessfulAppointmentUpdateResponse,
    responses={
        400: {"model": UpdateAppointmentError},
        401: {"model": UpdateAppointmentError},
    },
)
def update_appointment(
    id: str,
    update_appointment_request: UpdateAppointmentRequest,
    uid=Depends(Auth.is_logged_in),
):
    """
    Update an appointment.

    This will allow authenticated users to update one of their appointments.

    This path operation will:

    * Update an appointment.
    * Throw an error if appointment doesn't exist.
    * Throw an error if appointment doesn't belong to the authenticated user.
    * Throw an error if appointment retrieving fails.
    """
    appointment = Appointment.get_by_id(id)
    if not appointment or appointment.patient_id != uid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid appointment id"},
        )
    appointment.update(update_appointment_request.model_dump())

    physician = Physician.get_by_id(appointment.physician_id)
    patient = Patient.get_by_id(uid)
    date = datetime.fromtimestamp(update_appointment_request.date)
    requests.post(
        os.environ.get("NOTIFICATIONS_API_URL"),
        json={
            "type": "UPDATED_APPOINTMENT",
            "data": {
                "email": physician.email,
                "name": patient["first_name"],
                "last_name": patient["last_name"],
                "day": date.day,
                "month": date.month,
                "year": date.year,
                "hour": date.hour,
                "minute": date.minute,
                "second": date.second,
            },
        },
    )
    return {"message": "Appointment updated successfully"}


@router.put(
    "/close-appointment/{id}",
    status_code=status.HTTP_200_OK,
    response_model=SuccessfulAppointmentCloseResponse,
    responses={
        400: {"model": CloseAppointmentError},
        401: {"model": CloseAppointmentError},
    },
)
def close_appointment(
    id: str,
    close_appointment_request: CloseAppointmentRequest,
    uid=Depends(Auth.is_logged_in),
):
    """
    Close an appointment.

    This will allow authenticated physicians to close one of their appointments.

    This path operation will:

    * Close an appointment.
    * Throw an error if appointment doesn't exist.
    * Throw an error if appointment doesn't belong to the authenticated user.
    * Throw an error if appointment retrieving fails.
    """
    appointment = Appointment.get_by_id(id)
    if not appointment or appointment.physician_id != uid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid appointment id"},
        )
    appointment.close(close_appointment_request.model_dump())
    return {"message": "Appointment closed successfully"}
