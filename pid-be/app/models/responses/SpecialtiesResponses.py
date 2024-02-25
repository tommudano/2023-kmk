from pydantic import BaseModel
from typing import Union

from app.models.entities.Specialty import Specialty


class SpecialtyResponse(BaseModel):
    id: str
    name: str
    value: int

    def __init__(self, **data):
        specialty = Specialty.get_by_name(data["specialty"])
        super().__init__(**specialty.__dict__)


class GetSpecialtiesResponse(BaseModel):
    specialties: list[Union[str, None]]


class GetSpecialtyError(BaseModel):
    detail: str


class UpdateSpecialtiesResponse(BaseModel):
    specialties: list[Union[str, None]]


class UpdateSpecialtiesError(BaseModel):
    detail: str
