import requests
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from app.models.entities.Appointment import Appointment
from app.models.entities.Patient import Patient
from app.models.entities.Auth import Auth
from app.models.entities.Record import Record
from app.models.responses.RecordResponses import (
    GetRecordResponse,
    GetRecordError,
)
from app.models.requests.ObservationRequest import (
    ObservationRequest,
)

router = APIRouter(
    prefix="/records",
    tags=["Records"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/get-record/{patient_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetRecordResponse,
    responses={
        401: {"model": GetRecordError},
        403: {"model": GetRecordError},
        500: {"model": GetRecordError},
    },
)
def get_record(patient_id):
    """
    Get record from a patient.

    This will allow authenticated physicians to retrieve the record from a patient.

    This path operation will:

    * Return the patient record.
    * Throw an error if recrods retrieving fails.
    """
    try:
        record = Record.get_by_id(patient_id)
        return {"record": record}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.get(
    "/get-my-record",
    status_code=status.HTTP_200_OK,
    response_model=GetRecordResponse,
    responses={
        401: {"model": GetRecordError},
        403: {"model": GetRecordError},
        500: {"model": GetRecordError},
    },
)
def get_my_record(patient_id=Depends(Auth.is_logged_in)):
    """
    Get record from a patient.

    This will allow authenticated physicians to retrieve the record from a patient.

    This path operation will:

    * Return the patient record.
    * Throw an error if recrods retrieving fails.
    """
    try:
        print(patient_id)
        record = Record.get_by_id(patient_id)
        print(record)
        return {"record": record}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.post(
    "/update",
    status_code=status.HTTP_200_OK,
    response_model=GetRecordResponse,
    responses={
        401: {"model": GetRecordError},
        403: {"model": GetRecordError},
        500: {"model": GetRecordError},
    },
)
def update_record(
    observation_creation_request: ObservationRequest,
    uid=Depends(Auth.is_logged_in),
):
    """
    Update a patient's record with new observation.

    This will allow authenticated physicians to add observations to a patient's record.

    This path operation will:

    * Update the patient record with the provided observation.
    * Return the updated patient record.
    * Throw an error if the record is not found or updating fails.
    """
    try:
        print(observation_creation_request)
        appointment = Appointment.get_by_id(observation_creation_request.appointment_id)
        print(appointment.patient_id)
        record = Record.add_observation(
            appointment.patient_id, observation_creation_request.dict(), uid
        )
        return {"record": record}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
