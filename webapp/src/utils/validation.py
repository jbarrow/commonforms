from __future__ import annotations

import os
from typing import Iterable

ALLOWED_EXTS: tuple[str, ...] = (".pdf",)
ALLOWED_MIME: tuple[str, ...] = ("application/pdf", "application/x-pdf")


def validate_filename(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTS


def validate_mime(content_type: str | None) -> bool:
    if not content_type:
        return False
    return any(content_type.startswith(m) for m in ALLOWED_MIME)


def validate_size(size_bytes: int, max_mb: int) -> bool:
    return size_bytes <= max_mb * 1024 * 1024
