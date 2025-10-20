from __future__ import annotations

import os
from dataclasses import dataclass


def _int(env: str, default: int) -> int:
    try:
        return int(os.getenv(env, str(default)))
    except (TypeError, ValueError):
        return default


def _str(env: str, default: str) -> str:
    v = os.getenv(env)
    return v if v not in (None, "") else default


@dataclass(frozen=True)
class Settings:
    port: int = _int("PORT", 8080)
    max_upload_mb: int = _int("MAX_UPLOAD_MB", 25)
    language: str = _str("LANGUAGE", "it")
    hf_home: str | None = os.getenv("HF_HOME")
    cleanup_minutes: int = _int("CLEANUP_MINUTES", 10)
    tmp_dir: str = _str("TMP_DIR", "/tmp/commonforms-web")


def get_settings() -> Settings:
    s = Settings()
    if s.hf_home:
        os.environ["HF_HOME"] = s.hf_home
    os.makedirs(s.tmp_dir, exist_ok=True)
    return s
