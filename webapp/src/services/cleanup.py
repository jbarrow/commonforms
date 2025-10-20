from __future__ import annotations

import os
import time
from pathlib import Path


def cleanup_temp(tmp_dir: str, ttl_minutes: int) -> int:
    """Delete files older than ttl_minutes. Returns deleted count."""
    now = time.time()
    cutoff = now - ttl_minutes * 60
    deleted = 0
    p = Path(tmp_dir)
    if not p.exists():
        return 0
    for child in p.iterdir():
        try:
            if child.is_file():
                if child.stat().st_mtime < cutoff:
                    child.unlink(missing_ok=True)
                    deleted += 1
            elif child.is_dir():
                # Skip directories for simplicity
                pass
        except Exception:
            # Best effort
            continue
    return deleted
