"""Métricas de cobertura y rutas de reparto: funciones puras sobre DataFrames validados."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import davies_bouldin_score, silhouette_score

from cajas_alimentacion.config import (
    ASSUMED_SPEED_KMH,
    COVERAGE_LEVELS,
    GRID_SIZE_DEG,
    KM_PER_DEG,
    MAX_CLUSTERS,
    METRICS_SAMPLE_SIZE,
    MIN_POINTS_PER_CLUSTER,
    RANDOM_SEED,
)

logger = logging.getLogger(__name__)


def safe_div(num: float, den: float, fill: float = 0.0) -> float:
    """División escalar segura: denominador 0 devuelve ``fill``."""
    return fill if den == 0 else float(num) / float(den)


def safe_divide(num: pd.Series, den: pd.Series | float, fill: float | None = None) -> pd.Series:
    """División vectorial segura: ceros del denominador → ``NaN`` (``fill`` opcional).

    Examples
    --------
    >>> safe_divide(pd.Series([4.0, 2.0]), pd.Series([2.0, 0.0])).tolist()
    [2.0, nan]
    """
    den_s = den if isinstance(den, pd.Series) else pd.Series(den, index=num.index)
    out = num.astype("float64") / den_s.astype("float64").replace(0, np.nan)
    return out.fillna(fill) if fill is not None else out


def choose_n_clusters(n_rows: int) -> int:
    """Número de zonas: ``min(MAX_CLUSTERS, n_rows // MIN_POINTS_PER_CLUSTER)``, al menos 1."""
    return max(1, min(MAX_CLUSTERS, n_rows // MIN_POINTS_PER_CLUSTER))


def add_grid(df: pd.DataFrame, grid_size: float = GRID_SIZE_DEG) -> pd.DataFrame:
    """Agrega ``grid_lat``, ``grid_lon`` y ``grid_id`` (celda de ``grid_size`` grados)."""
    out = df.copy()
    out["grid_lat"] = (out["lat"] / grid_size).round().astype(int)
    out["grid_lon"] = (out["lon"] / grid_size).round().astype(int)
    out["grid_id"] = out["grid_lat"].astype(str) + "_" + out["grid_lon"].astype(str)
    return out


def grid_density(df: pd.DataFrame) -> pd.DataFrame:
    """Entregas por celda, de mayor a menor (desempate estable por ``grid_id``)."""
    return (
        df.groupby("grid_id")
        .agg(lat=("lat", "mean"), lon=("lon", "mean"), count=("lat", "count"))
        .reset_index()
        .sort_values(["count", "grid_id"], ascending=[False, True], kind="stable")
        .reset_index(drop=True)
    )


def cells_to_cover(
    density: pd.DataFrame, levels: tuple[float, ...] = COVERAGE_LEVELS
) -> list[dict[str, Any]]:
    """Celdas mínimas (las más densas primero) que concentran cada nivel de entregas."""
    counts = density["count"].to_numpy()
    cum = safe_divide(pd.Series(np.cumsum(counts)), float(counts.sum()), fill=0.0).to_numpy()
    rows = []
    for level in levels:
        n = min(int(np.searchsorted(cum, level - 1e-12)) + 1, len(counts))
        rows.append(
            {
                "nivel_pct": round(level * 100),
                "celdas": n,
                "celdas_pct": round(safe_div(n, len(counts)) * 100, 1),
            }
        )
    return rows


def distance_to_centers_km(
    coords_proj: np.ndarray, labels: np.ndarray, centers_proj: np.ndarray
) -> np.ndarray:
    """Distancia (km, línea recta) de cada punto al centro de su zona."""
    diff = coords_proj - centers_proj[labels]
    return np.hypot(diff[:, 0], diff[:, 1]) * KM_PER_DEG


def cluster_summary(
    labels: np.ndarray, dist_km: np.ndarray, centers_wgs84: np.ndarray
) -> list[dict[str, Any]]:
    """Resumen por zona: entregas, peso, centroide y distancia al centro (media y P90)."""
    total = len(labels)
    rows = []
    for c in range(len(centers_wgs84)):
        d = dist_km[labels == c]
        count = int(d.size)
        mean_km = float(d.mean()) if count else 0.0
        rows.append(
            {
                "id": c,
                "centroid_lat": round(float(centers_wgs84[c, 0]), 6),
                "centroid_lon": round(float(centers_wgs84[c, 1]), 6),
                "count": count,
                "share_pct": round(safe_div(count, total) * 100, 2),
                "mean_km": round(mean_km, 3),
                "p90_km": round(float(np.percentile(d, 90)), 3) if count else 0.0,
                "est_min_mean": round(mean_km / ASSUMED_SPEED_KMH * 60, 1),
            }
        )
    return sorted(rows, key=lambda r: -r["count"])


def clustering_quality(
    coords_proj: np.ndarray, labels: np.ndarray, inertia: float
) -> dict[str, Any]:
    """Silhouette y Davies-Bouldin sobre una muestra con semilla fija (reproducible)."""
    n_clusters = len(np.unique(labels))
    if n_clusters < 2 or len(labels) <= n_clusters:
        return {}
    if len(labels) > METRICS_SAMPLE_SIZE:
        rng = np.random.default_rng(RANDOM_SEED)
        idx = rng.choice(len(labels), METRICS_SAMPLE_SIZE, replace=False)
        coords_proj, labels = coords_proj[idx], labels[idx]
    try:
        return {
            "silhouette_score": round(float(silhouette_score(coords_proj, labels)), 4),
            "davies_bouldin_score": round(float(davies_bouldin_score(coords_proj, labels)), 4),
            "inertia": round(inertia, 2),
        }
    except ValueError:
        logger.exception("No se pudieron calcular las métricas de clustering")
        return {"error": "Could not compute clustering metrics"}


def key_findings(
    df: pd.DataFrame, density: pd.DataFrame, clusters: list[dict[str, Any]], dist_km: np.ndarray
) -> dict[str, Any]:
    """Cifras clave para el README y la app; solo el tiempo usa un supuesto declarado."""
    total = len(df)
    unique = int(df[["lat", "lon"]].drop_duplicates().shape[0])
    top10 = int(density["count"].head(10).sum())
    mean_km = float(dist_km.mean())
    return {
        "total_entregas": total,
        "puntos_unicos": unique,
        "repetidos_pct": round(safe_div(total - unique, total) * 100, 1),
        "n_zonas": len(clusters),
        "n_celdas": len(density),
        "top10_celdas_pct": round(safe_div(top10, total) * 100, 1),
        "cobertura": cells_to_cover(density),
        "dist_media_km": round(mean_km, 2),
        "dist_p90_km": round(float(np.percentile(dist_km, 90)), 2),
        "tiempo_medio_min": round(mean_km / ASSUMED_SPEED_KMH * 60, 1),
        "velocidad_supuesta_kmh": ASSUMED_SPEED_KMH,
        "zona_mayor": {"id": clusters[0]["id"], "share_pct": clusters[0]["share_pct"]},
    }
