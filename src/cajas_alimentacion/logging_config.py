"""Configuración de logging común al pipeline y a la app."""

from __future__ import annotations

import logging
import os

DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def setup_logging(level: str | None = None) -> None:
    """Configura el logging raíz; el nivel sale del argumento o de ``LOG_LEVEL``."""
    name = (level or os.getenv("LOG_LEVEL") or "INFO").upper()
    logging.basicConfig(level=getattr(logging, name, logging.INFO), format=DEFAULT_FORMAT)
