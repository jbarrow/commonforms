from __future__ import annotations

import os
from typing import Optional

from commonforms import prepare_form


def process_pdf(
    input_path: str,
    output_path: str,
    *,
    keep_existing_fields: bool = False,
    use_signature_fields: bool = False,
    device: str = "cpu",
    image_size: int = 1600,
    confidence: float = 0.3,
    fast: bool = False,
    model: str = "FFDNet-L",
    multiline: bool = False,
) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prepare_form(
        input_path,
        output_path,
        model=model,
        keep_existing_fields=keep_existing_fields,
        use_signature_fields=use_signature_fields,
        device=device,
        image_size=image_size,
        confidence=confidence,
        fast=fast,
        multiline=multiline,
    )
