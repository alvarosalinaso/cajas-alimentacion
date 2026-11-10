"""Agrupación de puntos de entrega en zonas de reparto (K-Means métrico)."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from cajas_alimentacion.config import RANDOM_SEED

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClusterResult:
    """Resultado del clustering; los centros están en coordenadas proyectadas."""

    labels: np.ndarray
    coords_proj: np.ndarray
    centers_proj: np.ndarray
    lon_scale: float
    inertia: float

    @property
    def centers_wgs84(self) -> np.ndarray:
        """Centros como columnas ``(lat, lon)`` en grados."""
        return np.column_stack([self.centers_proj[:, 1], self.centers_proj[:, 0] / self.lon_scale])


def project_equirectangular(df: pd.DataFrame) -> tuple[np.ndarray, float]:
    """Proyecta a ``(lon * cos(lat0), lat)`` en grados: distancia métrica a escala de ciudad."""
    lon_scale = float(np.cos(np.deg2rad(float(df["lat"].mean()))))
    coords = np.column_stack([df["lon"].to_numpy() * lon_scale, df["lat"].to_numpy()])
    return coords, lon_scale


def fit_clusters(df: pd.DataFrame, n_clusters: int, seed: int = RANDOM_SEED) -> ClusterResult:
    """Ajusta K-Means sobre coordenadas proyectadas (``df`` ya validado)."""
    coords, lon_scale = project_equirectangular(df)
    model = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10)
    labels = model.fit_predict(coords)
    logger.info("K-Means con %d zonas; inercia %.4f", n_clusters, model.inertia_)
    return ClusterResult(
        labels=labels,
        coords_proj=coords,
        centers_proj=model.cluster_centers_,
        lon_scale=lon_scale,
        inertia=float(model.inertia_),
    )
