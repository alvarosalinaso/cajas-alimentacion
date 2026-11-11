"""Configuración central: rutas del proyecto y parámetros del análisis.

Las rutas se derivan de la raíz del repositorio o de la variable de entorno
``CAJAS_ROOT``; no hay rutas absolutas en el código.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Final

ENV_ROOT: Final[str] = "CAJAS_ROOT"

RAW_FILE: Final[str] = "coordinates.csv"
SAMPLE_FILE: Final[str] = "sample_coordinates.csv"
PROCESSED_FILE: Final[str] = "delivery_analysis.csv"
STATS_FILE: Final[str] = "delivery_stats.json"

#: Máximo de zonas de reparto y mínimo de puntos por zona (n = min(MAX, filas // MIN)).
MAX_CLUSTERS: Final[int] = 10
MIN_POINTS_PER_CLUSTER: Final[int] = 100
RANDOM_SEED: Final[int] = 42
#: Filas máximas para silhouette / Davies-Bouldin (muestra con semilla fija).
METRICS_SAMPLE_SIZE: Final[int] = 5000
#: Tamaño de celda de la grilla de densidad, en grados.
GRID_SIZE_DEG: Final[float] = 0.01
#: Kilómetros por grado de latitud (esfera de radio medio 6 371 km).
KM_PER_DEG: Final[float] = 111.195
#: SUPUESTO (no medido): velocidad urbana media para convertir km en minutos.
ASSUMED_SPEED_KMH: Final[float] = 20.0
#: Coberturas acumuladas de entregas que se reportan sobre la grilla.
COVERAGE_LEVELS: Final[tuple[float, ...]] = (0.5, 0.8, 0.9)


def _default_root() -> Path:
    env_root = os.getenv(ENV_ROOT)
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ProjectPaths:
    """Rutas de entrada y salida, derivadas de ``root``."""

    root: Path

    @property
    def raw_csv(self) -> Path:
        return self.root / "data" / "raw" / RAW_FILE

    @property
    def sample_csv(self) -> Path:
        """Muestra sintética versionada (sin domicilios reales) para demo y CI."""
        return self.root / "data" / "sample" / SAMPLE_FILE

    @property
    def input_csv(self) -> Path:
        """Datos reales si existen (entorno privado); si no, la muestra sintética."""
        return self.raw_csv if self.raw_csv.exists() else self.sample_csv

    @property
    def processed_csv(self) -> Path:
        return self.root / "data" / "processed" / PROCESSED_FILE

    @property
    def stats_json(self) -> Path:
        return self.root / "data" / "export" / STATS_FILE

    @property
    def readme(self) -> Path:
        return self.root / "README.md"

    @classmethod
    def default(cls) -> ProjectPaths:
        return cls(root=_default_root())
