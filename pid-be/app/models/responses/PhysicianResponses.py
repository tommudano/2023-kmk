from pydantic import BaseModel
from typing import Union

from .AgendaResponses import AgendaResponse
from .SpecialtiesResponses import SpecialtyResponse


class CompletePhysicianResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    specialty: SpecialtyResponse
    email: str
    tuition: str
    agenda: AgendaResponse
    appointment_value: int

    def __init__(self, **data):
        data = {
            **PhysicianResponse(**data).__dict__,
            "specialty": SpecialtyResponse(**data),
        }
        super().__init__(**data)


class PhysicianResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    specialty: str
    email: str
    tuition: str
    agenda: AgendaResponse
    appointment_value: int

    def __init__(self, **data):
        data["agenda"] = AgendaResponse(
            **{
                "agenda": data["agenda"],
                "appointments": (
                    list(data["appointments"].keys())
                    if data.get("appointments")
                    else []
                ),
            }
        ).model_dump()
        super().__init__(**data)


class GetPhysiciansResponse(BaseModel):
    physicians: list[Union[PhysicianResponse, None]]


class PhysiciansError(BaseModel):
    detail: str


class SuccessfullUpdate(BaseModel):
    message: str
