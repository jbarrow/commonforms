from __future__ import annotations

import mimetypes
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from ..config import get_settings

router = APIRouter()


@router.get("/download/{file_id}")
async def download(file_id: str, mode: str = Query("none", pattern="^(none|zip|pdf)$")):
    settings = get_settings()
    path = os.path.join(settings.tmp_dir, file_id)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File non trovato")
    filename = Path(path).name

    # Handle compression modes
    if mode == "zip":
        from ..services.compression import zip_output

        zip_path = os.path.join(settings.tmp_dir, f"{filename}.zip")
        zip_output(path, zip_path)
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=f"{Path(filename).stem}.zip",
        )
    elif mode == "pdf":
        from ..services.compression import compress_pdf

        out_path = os.path.join(settings.tmp_dir, f"{Path(filename).stem}-compressed.pdf")
        compress_pdf(path, out_path)
        media_type = mimetypes.guess_type(out_path)[0] or "application/pdf"
        return FileResponse(
            out_path,
            media_type=media_type,
            filename=Path(out_path).name,
        )
    else:
        media_type = mimetypes.guess_type(filename)[0] or "application/pdf"
        return FileResponse(
            path,
            media_type=media_type,
            filename=filename,
        )
