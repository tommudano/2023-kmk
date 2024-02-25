import os
import uvicorn
from dotenv import load_dotenv

from fastapi import FastAPI, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

from app.routers import emails

load_dotenv()


CTX_PORT: int = int(os.environ.get("PORT")) if os.environ.get("PORT") else 8080

app = FastAPI(docs_url=None, redoc_url=None, openapi_url="/api/openapi.json")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

routers = [emails.router]

for router in routers:
    app.include_router(router)


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
    uvicorn.run("app.main:app", host="0.0.0.0", port=CTX_PORT, reload=True)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Gestion Medica KMK",
        version="1.0.0",
        description="Docs for the KMK API",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://firebasestorage.googleapis.com/v0/b/pid-kmk.appspot.com/o/appResources%2FmediSyncLogo.png?alt=media&token=5fa730e3-a5cb-4a65-ad71-88af0c72b65a"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
