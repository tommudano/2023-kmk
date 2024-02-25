from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from app.models.entities.Gender import Gender
from app.models.responses.GendersResponses import (
    GetGendersResponse,
    GetGendersError,
)

router = APIRouter(
    prefix="/genders",
    tags=["Genders"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=GetGendersResponse,
    responses={
        500: {"model": GetGendersError},
    },
)
def get_all_genders():
    """
    Get all genders.

    This will allow authenticated users to retrieve all genders.

    This path operation will:

    * Return all the genders in the system.
    * Throw an error if specialty retrieving fails.
    """
    try:
        genders = Gender.get_all()
        return {"genders": genders}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
