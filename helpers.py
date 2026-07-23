"""Dosya, zaman ve doğrulama işlemleri için ortak yardımcılar."""

from __future__ import annotations

import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo


class MissingColumnsError(ValueError):
    """Modelin beklediği CSV sütunları eksik olduğunda kullanılır."""

    def __init__(self, columns: list[str]) -> None:
        self.columns = columns
        super().__init__(
            "CSV dosyasında modelin beklediği sütunlar eksik."
        )

def make_file_signature(file_bytes: bytes) -> str:
    """Dosya içeriği için kararlı bir SHA-256 imzası üretir."""
    return hashlib.sha256(file_bytes).hexdigest()

def format_bytes(byte_count: int | float) -> str:
    """Byte değerini okunabilir dosya boyutuna dönüştürür."""
    size = float(max(byte_count, 0))
    units = ["B", "KB", "MB", "GB", "TB"]

    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size):,} {unit}".replace(",", ".")
            return f"{size:.2f} {unit}"
        size /= 1024

    return f"{size:.2f} TB"

def current_analysis_time() -> str:
    """Son analiz zamanını İstanbul saatine göre biçimlendirir."""
    try:
        current_time = datetime.now(ZoneInfo("Europe/Istanbul"))
    except Exception:
        current_time = datetime.now().astimezone()

    return current_time.strftime("%d.%m.%Y %H:%M:%S")
