import time
from pydantic import BaseModel, field_validator, root_validator
from typing import Optional
from fastapi import Query

from app.models.entities.Physician import Physician


class AppointmentCreationRequest(BaseModel):
    date: int = Query(
        description="Date should be in seconds. The _date_ must be after now"
    )
    physician_id: str = Query(
        description="The _physician_id_ must be the id of an existant physician"
    )
    google_meet_conference: Optional[bool] = False

    @field_validator("date")
    def validate_date(cls, date_to_validate):
        if date_to_validate < time.time():
            raise ValueError("Date can't be in the past")
        return date_to_validate

    @field_validator("physician_id")
    def validate_physician_id(cls, physician_id_to_validate):
        if not Physician.is_physician(physician_id_to_validate):
            raise ValueError("Physician id doesnt belong to an existant physician")
        if not Physician.get_by_id(physician_id_to_validate).approved == "approved":
            raise ValueError("Can only set an appointment with a valid physician")
        return physician_id_to_validate

    @root_validator(pre=False, skip_on_failure=True)
    def validate_physicians_availability(cls, appointment_creation_request_attributes):
        if not Physician.get_by_id(
            appointment_creation_request_attributes["physician_id"]
        ).has_availability(appointment_creation_request_attributes["date"]):
            raise ValueError("Can only set appointment at physicians available hours")
        return appointment_creation_request_attributes


class UpdateAppointmentRequest(BaseModel):
    date: int = Query(
        description="Date should be in seconds. The _date_ must be after now"
    )

    @field_validator("date")
    def validate_date(cls, date_to_validate):
        if date_to_validate < time.time():
            raise ValueError("Date can't be in the past")
        return date_to_validate


class CloseAppointmentRequest(BaseModel):
    attended: bool
    start_time: str
