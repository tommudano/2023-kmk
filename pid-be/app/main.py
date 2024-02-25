import os
import uvicorn
from dotenv import load_dotenv
from .config import initialize_firebase_app

initialize_firebase_app()

from fastapi import FastAPI, status, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html


load_dotenv()

from app.routers import (
    users,
    appointments,
    specialties,
    physicians,
    admin,
    records,
    genders,
    bloodTypes,
    analysis,
    dashboards,
)
from app.models.entities.Auth import Auth


CTX_PORT: int = int(os.environ.get("PORT")) if os.environ.get("PORT") else 8080

app = FastAPI(docs_url=None, redoc_url=None, openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

routers = [
    users.router,
    appointments.router,
    specialties.router,
    physicians.router,
    admin.router,
    records.router,
    genders.router,
    bloodTypes.router,
    analysis.router,
    dashboards.router,
]

for router in routers:
    app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "detail": "Invalid input format",  # optionally include the errors
                "body": exc.body,
                "error": exc.errors(),
            }
        ),
    )


@app.get("/docs", response_class=HTMLResponse)
async def get_docs(username=Depends(Auth.is_kmk_maintainer)) -> HTMLResponse:
    return get_swagger_ui_html(openapi_url="/api/openapi.json", title="docs")


@app.get("/redoc", response_class=HTMLResponse)
async def get_redoc(username: str = Depends(Auth.is_kmk_maintainer)) -> HTMLResponse:
    return get_redoc_html(openapi_url="/api/openapi.json", title="redoc")


@app.get("/")
async def root() -> RedirectResponse:
    """
    Root endpoint,

    It returns the OPENAPI docs for the KMK API
    """
    return RedirectResponse(url="/redoc", status_code=status.HTTP_303_SEE_OTHER)


def start():
    """
    _summary_: Start the application
    """
    if os.environ.get("ENV") == "prod":
        uvicorn.run(
            "app.main:app", host="0.0.0.0", port=CTX_PORT, forwarded_allow_ips="*"
        )
    else:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=CTX_PORT,
            forwarded_allow_ips="*",
            reload=True,
        )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Gestion Medica KMK",
        version="1.0.0",
        description="Docs for the KMK API",
        routes=app.routes,
        tags=[
            {
                "name": "Users",
                "description": "Operations that handle users, like **login** and **signup**",
            },
            {
                "name": "Specialties",
                "description": "Operations that handle specialties",
            },
            {
                "name": "Appointments",
                "description": "Operations that handle appointments",
            },
            {
                "name": "Physicians",
                "description": "Operations that handle physicians",
            },
            {
                "name": "Admins",
                "description": "Operations that are handled by admins",
            },
            {
                "name": "Analysis",
                "description": "Operations that handle analysis files",
            },
        ],
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://firebasestorage.googleapis.com/v0/b/pid-kmk.appspot.com/o/appResources%2FmediSyncLogo.png?alt=media&token=5fa730e3-a5cb-4a65-ad71-88af0c72b65a"
    }
    # openapi_schema["paths"]["/users/login"]["post"].pop("security")
    # openapi_schema["paths"]["/users/register"]["post"].pop("security")
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
