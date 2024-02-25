from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from app.models.entities.BloodType import BloodType
from app.models.responses.BloodTypesResponses import (
    GetBloodTypesResponse,
    GetBloodTypesError,
)

router = APIRouter(
    prefix="/blood-types",
    tags=["BloodTypes"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=GetBloodTypesResponse,
    responses={
        500: {"model": GetBloodTypesError},
    },
)
def get_all_blood_types():
    """
    Get all genders.

    This will allow authenticated users to retrieve all genders.

    This path operation will:

    * Return all the genders in the system.
    * Throw an error if specialty retrieving fails.
    """
    try:
        blood_types = BloodType.get_all()
        return {"blood_types": blood_types}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
