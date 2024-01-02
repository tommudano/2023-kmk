from pydantic import BaseModel


class SuccessfullAdminRegistrationResponse(BaseModel):
    message: str


class AdminRegistrationError(BaseModel):
    detail: str


class GetAdminUserError(BaseModel):
    detail: str


class AdminUserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str


class SuccessfulSpecialtyUpdateValueResponse(BaseModel):
    message: str
