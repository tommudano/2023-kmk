import json
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from app.models.entities.Auth import Auth
from app.models.entities.Admin import Admin
from app.models.entities.Appointment import Appointment
from app.models.responses.DashboardResponses import (
    SuccessfullDashboardResponse,
    DashboardErrorResponse,
)

from app.helpers.MetricParserHelper import MetricParserHelper

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/admin",
    status_code=status.HTTP_200_OK,
    response_model=SuccessfullDashboardResponse,
    responses={
        401: {"model": DashboardErrorResponse},
        403: {"model": DashboardErrorResponse},
        500: {"model": DashboardErrorResponse},
    },
)
def get_admin_dashboard(uid=Depends(Auth.is_admin)):
    """
    Get admin dashboard.

    This will allow admins to retrieve the metrics insights.

    This path operation will:

    * Return the admin metrics.
    * Throw an error if dashboard retrieving fails.
    """
    try:
        all_appointments = Appointment.get_all_appointments()
        all_appointments_per_specialty = (
            MetricParserHelper.filter_appointments_per_specialty(all_appointments)
        )
        # updated_appointments = len(Appointment.get_all_appointments_updtated())
        return {
            "dashboard_metrics": {
                "all_appointments_by_specialty": all_appointments_per_specialty
            }
        }
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.get(
    "/physician",
    status_code=status.HTTP_200_OK,
    response_model=SuccessfullDashboardResponse,
    responses={
        401: {"model": DashboardErrorResponse},
        403: {"model": DashboardErrorResponse},
        500: {"model": DashboardErrorResponse},
    },
)
def get_physician_dashboard(uid=Depends(Auth.is_logged_in)):
    """
    Get physician dashboard.

    This will allow physicians to retrieve their metrics insights.

    This path operation will:

    * Return the physician metrics.
    * Throw an error if dashboard retrieving fails.
    """
    try:
        all_appointments = Appointment.get_all_appointments_for_physician_with(uid)
        all_appointments_per_month = (
            MetricParserHelper.filter_appointments_for_current_year_by_month_and_key(
                all_appointments, "date"
            )
        )
        updated_appointments = Appointment.get_all_appointments_updtated_for_physician(
            uid
        )

        updated_appointments_per_month = (
            MetricParserHelper.filter_appointments_for_current_year_by_month_and_key(
                updated_appointments, "updated_at"
            )
        )
        return {
            "dashboard_metrics": {
                "all_appointments": all_appointments_per_month,
                "updated_appointments": updated_appointments_per_month,
            }
        }
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
