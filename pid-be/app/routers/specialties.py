from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.models.entities.Auth import Auth
from app.models.entities.Admin import Admin
from app.models.entities.Specialty import Specialty
from app.models.responses.SpecialtiesResponses import (
    GetSpecialtiesResponse,
    GetSpecialtyError,
    UpdateSpecialtiesResponse,
    UpdateSpecialtiesError,
)

router = APIRouter(
    prefix="/specialties",
    tags=["Specialties"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=GetSpecialtiesResponse,
    responses={
        500: {"model": GetSpecialtyError},
    },
)
def get_all_specialties():
    """
    Get all specialties.

    This will allow authenticated users to retrieve all specialties.

    This path operation will:

    * Return all the specialties in the system.
    * Throw an error if specialty retrieving fails.
    """
    try:
        specialties = Specialty.get_all_names()
        return {"specialties": specialties}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.post(
    "/add/{specialty_name}",
    status_code=status.HTTP_200_OK,
    response_model=UpdateSpecialtiesResponse,
    responses={
        400: {"model": UpdateSpecialtiesError},
        401: {"model": UpdateSpecialtiesError},
        403: {"model": UpdateSpecialtiesError},
        500: {"model": UpdateSpecialtiesError},
    },
)
def add_specialty(
    specialty_name: str,
    uid=Depends(Auth.is_admin),
):
    """
    Add a new specialty.

    This will allow authenticated admins to add new specialties.

    This path operation will:

    * Add the new specialty.
    * Return the updated list of specialties.
    * Throw an error if it fails.
    """
    try:
        Specialty.add_specialty(specialty_name)
        updated_specialties = Specialty.get_all_names()
        return {"specialties": updated_specialties}
    except HTTPException as http_exception:
        return JSONResponse(
            status_code=http_exception.status_code,
            content={"detail": http_exception.detail},
        )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.delete(
    "/delete/{specialty_name}",
    status_code=status.HTTP_200_OK,
    response_model=UpdateSpecialtiesResponse,
    responses={
        401: {"model": UpdateSpecialtiesError},
        403: {"model": UpdateSpecialtiesError},
        500: {"model": UpdateSpecialtiesError},
    },
)
def delete_specialty(
    specialty_name: str,
    uid=Depends(Auth.is_admin),
):
    """
    Deletes a specialty.

    This will allow authenticated admins to delete specialties.

    This path operation will:

    * Delete the specialty.
    * Return the updated list of specialties.
    * Throw an error if it fails.
    """
    try:
        Specialty.delete_specialty(specialty_name)
        updated_specialties = Specialty.get_all_names()
        return {"specialties": updated_specialties}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
