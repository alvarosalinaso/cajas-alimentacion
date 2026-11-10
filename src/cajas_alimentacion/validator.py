"""Validación temprana (fail-fast) del esquema de coordenadas."""

from __future__ import annotations

import logging
from collections.abc import Iterable

import pandas as pd

logger = logging.getLogger(__name__)

COORDINATES_SCHEMA: frozenset[str] = frozenset({"lat", "lon"})


class SchemaError(ValueError):
    """Los datos de entrada no cumplen el esquema esperado."""


def require_columns(df: pd.DataFrame, required: Iterable[str], source: str) -> None:
    """Lanza :class:`SchemaError` si faltan columnas obligatorias."""
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise SchemaError(f"{source}: faltan columnas {missing}; presentes: {list(df.columns)}")


def validate_coordinates(df: pd.DataFrame, source: str = "coordinates") -> pd.DataFrame:
    """Valida columnas, tipos numéricos, nulos y rangos geográficos.

    Returns
    -------
    pandas.DataFrame
        El mismo DataFrame, para encadenar llamadas.
    """
    require_columns(df, COORDINATES_SCHEMA, source)
    if df.empty:
        raise SchemaError(f"{source}: no contiene filas")
    for col in sorted(COORDINATES_SCHEMA):
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise SchemaError(f"{source}: la columna '{col}' no es numérica")
        n_null = int(df[col].isna().sum())
        if n_null:
            raise SchemaError(f"{source}: la columna '{col}' tiene {n_null} valores nulos")
    if not df["lat"].between(-90, 90).all():
        raise SchemaError(f"{source}: 'lat' fuera del rango [-90, 90]")
    if not df["lon"].between(-180, 180).all():
        raise SchemaError(f"{source}: 'lon' fuera del rango [-180, 180]")
    logger.debug("%s validado: %d filas", source, len(df))
    return df
