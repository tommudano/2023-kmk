from pydantic import BaseModel
from typing import Union, Optional

from .PhysicianResponses import PhysicianResponse
from .PatientResponses import PatientResponse
from app.models.entities.Physician import Physician
from app.models.entities.Patient import Patient


class SuccessfulAppointmentCreationResponse(BaseModel):
    appointment_id: str


class SuccessfulAppointmentDeletionResponse(BaseModel):
    message: str


class SuccessfulAppointmentUpdateResponse(BaseModel):
    message: str


class SuccessfulAppointmentCloseResponse(BaseModel):
    message: str


class AppointmentCreationError(BaseModel):
    detail: str


class GetAppointmentError(BaseModel):
    detail: str


class DeleteAppointmentError(BaseModel):
    detail: str


class UpdateAppointmentError(BaseModel):
    detail: str


class CloseAppointmentError(BaseModel):
    detail: str


class BasicAppointmentResponse(BaseModel):
    id: str
    date: int
    physician: PhysicianResponse
    patient: PatientResponse
    created_at: int
    status: str = "pending"
    attended: Union[bool, None] = None
    start_time: Union[str, None] = None
    appointment_value: int
    google_meet_conference: bool
    meet_link: Optional[str] = None

    def __init__(self, **data):
        physician = Physician.get_by_id(data["physician_id"])
        data["physician"] = PhysicianResponse(**physician.__dict__).model_dump()

        patient = Patient.get_by_id(data["patient_id"])
        data["patient"] = PatientResponse(**patient).model_dump()
        super().__init__(**data)


class AllAppointmentsResponse(BaseModel):
    appointments: list[Union[BasicAppointmentResponse, None]]
