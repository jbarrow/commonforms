from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import get_settings
from .logging_config import configure_logging
from .routes.upload import router as upload_router
from .routes.download import router as download_router

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="CommonForms Web")

BASE_DIR = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app.include_router(upload_router)
app.include_router(download_router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    get_settings()  # ensure tmp dir exists and env wired
    return templates.TemplateResponse(
        "index.html", {"request": request, "download_id": None, "processing": False}
    )


@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    # Render a user-friendly error page instead of JSON
    status_code = exc.status_code if hasattr(exc, "status_code") else 500
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "message": getattr(exc, "detail", str(exc))},
        status_code=status_code,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "message": "Si è verificato un errore inatteso."},
        status_code=500,
    )
