from pydantic import BaseModel, Field
from typing import Annotated
from fastapi import Query


class AdminRegisterRequest(BaseModel):
    name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: Annotated[str, Query(pattern="^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$")]
    password: str


class SpecialtyUpdateValueRequest(BaseModel):
    value: int = Field(ge=1)
