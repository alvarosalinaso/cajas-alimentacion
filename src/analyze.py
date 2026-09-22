"""Spatial analysis for food box delivery points."""

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_score

BASE = Path(__file__).parent.parent


def analyze() -> dict[str, Any] | None:
    csv_path = BASE / "data" / "raw" / "coordinates.csv"
    if not csv_path.exists():
        return None

    df = pd.read_csv(csv_path)
    n_clusters = max(1, min(10, len(df) // 100))

    # A8: clustering por distancia métrica — equirectangular (lon escalado por
    # cos(lat)), equivalente a UTM 19S a escala de ciudad sin dependencias nuevas.
    # Los centroides se devuelven inversos en WGS84 (grados) para el dashboard.
    lat0 = float(df["lat"].mean())
    lon_scale = float(np.cos(np.deg2rad(lat0)))
    coords_proj = np.column_stack([df["lon"].to_numpy() * lon_scale, df["lat"]])

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(coords_proj)

    grid_size = 0.01
    df["grid_lat"] = (df["lat"] / grid_size).round().astype(int)
    df["grid_lon"] = (df["lon"] / grid_size).round().astype(int)
    df["grid_id"] = df["grid_lat"].astype(str) + "_" + df["grid_lon"].astype(str)

    processed_path = BASE / "data" / "processed" / "delivery_analysis.csv"
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)

    centroids = []
    for c in range(n_clusters):
        cx, cy = kmeans.cluster_centers_[c]
        centroids.append(
            {
                "id": c,
                # Inversa equirectangular -> WGS84 (grados)
                "centroid_lat": round(float(cy), 6),
                "centroid_lon": round(float(cx / lon_scale), 6),
                "count": int((df["cluster"] == c).sum()),
            }
        )

    # Clustering quality metrics (sample for performance on large datasets)
    cluster_metrics = {}
    if n_clusters > 1 and len(df) > n_clusters:
        try:
            labels = df["cluster"].values
            # Use sample for metrics on large datasets for performance
            if len(df) > 5000:
                # A8: semilla fija -> métricas reproducibles
                sample_idx = np.random.default_rng(42).choice(
                    len(df), 5000, replace=False
                )
                coords_sample = coords_proj[sample_idx]
                labels_sample = labels[sample_idx]
            else:
                coords_sample = coords_proj
                labels_sample = labels
            cluster_metrics["silhouette_score"] = round(
                silhouette_score(coords_sample, labels_sample), 4
            )
            cluster_metrics["davies_bouldin_score"] = round(
                davies_bouldin_score(coords_sample, labels_sample), 4
            )
            cluster_metrics["inertia"] = round(kmeans.inertia_, 2)
        except Exception:
            cluster_metrics["error"] = "Could not compute clustering metrics"

    grid_density = (
        df.groupby("grid_id")
        .agg(lat=("lat", "mean"), lon=("lon", "mean"), count=("lat", "count"))
        .reset_index()
        .sort_values("count", ascending=False)
    )

    stats = {
        "total_deliveries": len(df),
        "clusters": sorted(centroids, key=lambda x: -x["count"]),
        "grid_density": grid_density.head(20).to_dict("records"),
        "n_grid_cells": len(grid_density),
        "cluster_metrics": cluster_metrics,
    }

    output = BASE / "data" / "export" / "delivery_stats.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    return stats


if __name__ == "__main__":
    result = analyze()
    if result:
        print(f"Total deliveries: {result['total_deliveries']}")
        print(f"Clusters: {len(result['clusters'])}")
        print(f"Grid cells: {result['n_grid_cells']}")
    else:
        print("No data")
