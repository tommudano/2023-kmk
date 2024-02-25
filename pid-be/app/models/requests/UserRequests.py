import re
from pydantic import BaseModel, Field, field_validator
from typing import Annotated, Literal
from fastapi import Query

from app.models.entities.Specialty import Specialty


class UserLoginRequest(BaseModel):
    email: Annotated[str, Query(pattern="^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$")]
    password: str


class PatientRegisterRequest(BaseModel):
    role: Literal["patient"] = "patient"
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: Annotated[str, Query(pattern="^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$")]
    birth_date: str
    gender: str
    blood_type: str
    password: str = Field(
        min_length=8,
        description="Must contain at least one uppercase, at least one lowercase and at least one number",
    )

    @field_validator("password")
    def validate_password(cls, password_to_validate):
        if not re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)", password_to_validate):
            raise ValueError("Invalid password format")
        return password_to_validate


class PhysicianRegisterRequest(BaseModel):
    role: Literal["physician"] = "physician"
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    email: Annotated[str, Query(pattern="^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$")]
    password: str = Field(
        min_length=8,
        description="Must contain at least one uppercase, at least one lowercase and at least one number",
    )
    tuition: str
    specialty: str

    @field_validator("specialty")
    def validate_specialty(cls, specialty_to_validate):
        if not Specialty.exists_with_name(specialty_to_validate):
            raise ValueError("Specilaty doesnt exist")
        return specialty_to_validate

    @field_validator("password")
    def validate_password(cls, password_to_validate):
        if not re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)", password_to_validate):
            raise ValueError("Invalid password format")
        return password_to_validate


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(
        min_length=8,
        description="Must contain at least one uppercase, at least one lowercase and at least one number",
    )

    @field_validator("new_password")
    def validate_password(cls, password_to_validate):
        if not re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)", password_to_validate):
            raise ValueError("Invalid password format")
        return password_to_validate
