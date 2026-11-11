"""Escritura determinista de salidas (CSV y JSON sin NaN)."""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def sanitize(obj: Any) -> Any:
    """Convierte NaN/inf en ``None`` y tipos numpy en nativos, de forma recursiva."""
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list | tuple):
        return [sanitize(v) for v in obj]
    if hasattr(obj, "item") and not isinstance(obj, str | bytes):
        obj = obj.item()
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    return obj


def write_csv(df: pd.DataFrame, path: Path) -> Path:
    """Escribe ``df`` creando el directorio si hace falta."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info("Escrito %s (%d filas)", path.name, len(df))
    return path


def write_json(data: dict[str, Any], path: Path) -> Path:
    """Escribe JSON estricto (``allow_nan=False``) con claves en orden de inserción."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(sanitize(data), indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    logger.info("Escrito %s", path.name)
    return path
