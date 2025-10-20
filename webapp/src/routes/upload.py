from __future__ import annotations

import logging
import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..config import get_settings
from ..services.cleanup import cleanup_temp
from ..services.commonforms_adapter import process_pdf
from ..utils.validation import validate_filename, validate_mime, validate_size

logger = logging.getLogger(__name__)
router = APIRouter()

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))


@router.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, file: UploadFile = File(...)):
    settings = get_settings()

    # Basic validation
    if not validate_filename(file.filename or ""):
        raise HTTPException(status_code=400, detail="Formato file non supportato (solo PDF)")
    if not validate_mime(file.content_type):
        raise HTTPException(status_code=400, detail="MIME type non valido (solo PDF)")

    # Save to temp
    tmp_in = os.path.join(settings.tmp_dir, f"{uuid.uuid4()}-in.pdf")
    size = 0
    with open(tmp_in, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            size += len(chunk)
            if not validate_size(size, settings.max_upload_mb):
                f.close()
                try:
                    os.remove(tmp_in)
                except OSError:
                    pass
                raise HTTPException(status_code=413, detail="File troppo grande")

    # Process
    tmp_out = os.path.join(settings.tmp_dir, f"{uuid.uuid4()}-out.pdf")
    try:
        # Enforce CPU-only execution
        process_pdf(tmp_in, tmp_out, device="cpu")
    except Exception as exc:  # best-effort mapping
        logger.exception("Processing failed")
        raise HTTPException(status_code=500, detail=f"Errore durante l'elaborazione: {exc}")

    # Simple cleanup sweep
    try:
        cleanup_temp(settings.tmp_dir, settings.cleanup_minutes)
    except Exception:
        logger.debug("Cleanup failed", exc_info=True)

    # Id is the output filename
    file_id = Path(tmp_out).name
    # Compute size in MB for UI (best effort)
    try:
        size_mb = round(os.path.getsize(tmp_out) / (1024 * 1024), 2)
    except OSError:
        size_mb = None
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "download_id": file_id,
            "download_size": size_mb,
            "processing": False,
        },
    )
