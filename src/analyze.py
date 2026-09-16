"""Spatial analysis for food box delivery points."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

BASE = Path(__file__).parent.parent


def analyze():
    csv_path = BASE / "data" / "raw" / "coordinates.csv"
    if not csv_path.exists():
        return None

    df = pd.read_csv(csv_path)
    n_clusters = min(10, len(df) // 100)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(df[["lat", "lon"]])

    grid_size = 0.01
    df["grid_lat"] = (df["lat"] / grid_size).round().astype(int)
    df["grid_lon"] = (df["lon"] / grid_size).round().astype(int)
    df["grid_id"] = df["grid_lat"].astype(str) + "_" + df["grid_lon"].astype(str)

    processed_path = BASE / "data" / "processed" / "delivery_analysis.csv"
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(processed_path, index=False)

    centroids = []
    for c in range(n_clusters):
        cluster_df = df[df["cluster"] == c]
        centroids.append({
            "id": c,
            "centroid_lat": round(float(cluster_df["lat"].mean()), 6),
            "centroid_lon": round(float(cluster_df["lon"].mean()), 6),
            "count": len(cluster_df),
        })

    grid_density = df.groupby("grid_id").agg(
        lat=("lat", "mean"), lon=("lon", "mean"), count=("lat", "count")
    ).reset_index().sort_values("count", ascending=False)

    stats = {
        "total_deliveries": len(df),
        "clusters": sorted(centroids, key=lambda x: -x["count"]),
        "grid_density": grid_density.head(20).to_dict("records"),
        "n_grid_cells": len(grid_density),
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
