"""Ingesta de coordenadas de entrega: saneamiento de cabeceras y casteo estricto."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from cajas_alimentacion.config import ProjectPaths
from cajas_alimentacion.validator import (
    COORDINATES_SCHEMA,
    SchemaError,
    require_columns,
    validate_coordinates,
)

logger = logging.getLogger(__name__)


def load_coordinates(path: Path | None = None) -> pd.DataFrame:
    """Lee y valida el CSV de coordenadas (``lat``, ``lon``).

    Parameters
    ----------
    path : Path | None
        Ruta del CSV; por defecto la de :class:`ProjectPaths`.

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe.
    SchemaError
        Si faltan columnas, hay valores no numéricos, nulos o fuera de rango.
    """
    csv_path = Path(path) if path is not None else ProjectPaths.default().input_csv
    if not csv_path.exists():
        logger.error("No existe el archivo de coordenadas: %s", csv_path)
        raise FileNotFoundError(f"No existe {csv_path}")
    df = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str)
    df.columns = [str(c).strip().lower() for c in df.columns]
    require_columns(df, COORDINATES_SCHEMA, csv_path.name)
    df = df[["lat", "lon"]].copy()
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col].str.strip(), errors="raise").astype("float64")
        except (ValueError, TypeError) as exc:
            logger.exception("Valores no numéricos en '%s' de %s", col, csv_path.name)
            raise SchemaError(f"{csv_path.name}: '{col}' contiene valores no numéricos") from exc
    validate_coordinates(df, csv_path.name)
    logger.info("Cargadas %d coordenadas desde %s", len(df), csv_path.name)
    return df
