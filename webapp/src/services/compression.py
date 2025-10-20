from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter  # type: ignore


def zip_output(pdf_path: str, zip_path: str) -> None:
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(pdf_path, arcname=Path(pdf_path).name)


def compress_pdf(input_pdf: str, output_pdf: str) -> None:
    """
    Best-effort re-save to reduce size using pypdf. This may not dramatically reduce size
    but avoids adding heavy dependencies. Replace with a stronger compressor if needed.
    """
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with open(output_pdf, "wb") as f:
        writer.write(f)
