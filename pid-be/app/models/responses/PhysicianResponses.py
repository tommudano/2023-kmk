from pydantic import BaseModel
from typing import Union

from .AgendaResponses import AgendaResponse


class PhysicianResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    specialty: str
    email: str
    tuition: str
    agenda: AgendaResponse

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


class GetPhysiciansError(BaseModel):
    detail: str
