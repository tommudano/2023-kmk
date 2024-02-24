from fastapi import Query
from pydantic import BaseModel, root_validator
from typing import Dict


class AgendaUpdateRequest(BaseModel):
    start: float = Query(ge=0)
    finish: float = Query(ge=0)

    @root_validator(pre=False, skip_on_failure=True)
    def validate_physicians_availability(cls, agenda_update_request_attributes):
        if (
            agenda_update_request_attributes["start"]
            > agenda_update_request_attributes["finish"]
        ):
            raise ValueError("Finishing time must be greater thabn start time")
        return agenda_update_request_attributes


class UpdatePhysicianValueRequest(BaseModel):
    new_value: int = Query(ge=0)
