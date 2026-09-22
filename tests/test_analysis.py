"""Tests for the spatial analysis pipeline."""

import json
from pathlib import Path

import pandas as pd
import pytest

from src.analyze import analyze

BASE = Path(__file__).parent.parent
RAW_CSV = BASE / "data" / "raw" / "coordinates.csv"
ANALYSIS_CSV = BASE / "data" / "processed" / "delivery_stats.json"
STATS_JSON = BASE / "data" / "export" / "delivery_stats.json"


@pytest.fixture
def raw_csv():
    return RAW_CSV


@pytest.fixture
def analysis_csv():
    return BASE / "data" / "processed" / "delivery_analysis.csv"


@pytest.fixture
def stats_json():
    return STATS_JSON


@pytest.fixture
def stats():
    if not STATS_JSON.exists():
        pytest.skip("delivery_stats.json not found")
    with open(STATS_JSON, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def analysis_df():
    if not (BASE / "data" / "processed" / "delivery_analysis.csv").exists():
        pytest.skip("delivery_analysis.csv not found")
    return pd.read_csv(BASE / "data" / "processed" / "delivery_analysis.csv")


def test_analyze_returns_dict():
    if not RAW_CSV.exists():
        pytest.skip("coordinates.csv not found")
    result = analyze()
    assert result is not None
    assert isinstance(result, dict)


def test_analyze_returns_expected_keys():
    if not RAW_CSV.exists():
        pytest.skip("coordinates.csv not found")
    result = analyze()
    assert result is not None
    expected_keys = {
        "total_deliveries",
        "clusters",
        "grid_density",
        "n_grid_cells",
        "cluster_metrics",
    }
    assert expected_keys == set(result.keys())


def test_cluster_count():
    if not RAW_CSV.exists():
        pytest.skip("coordinates.csv not found")
    result = analyze()
    assert result is not None
    assert len(result["clusters"]) == 10


def test_delivery_analysis_csv_columns(analysis_df):
    expected_columns = {"lat", "lon", "cluster", "grid_id"}
    assert expected_columns.issubset(set(analysis_df.columns))


def test_total_deliveries(stats):
    assert stats["total_deliveries"] == 80595


def test_centroids_exported_in_wgs84_santiago_bounds():
    """A8: centroides inversos a WGS84 dentro del AM de Santiago."""
    if not RAW_CSV.exists():
        pytest.skip("coordinates.csv not found")
    result = analyze()
    assert result is not None
    for c in result["clusters"]:
        assert -33.9 <= c["centroid_lat"] <= -33.0
        assert -71.3 <= c["centroid_lon"] <= -70.3


def test_cluster_metrics_reproducible():
    """A8: muestra con semilla fija -> métricas idénticas entre corridas."""
    if not RAW_CSV.exists():
        pytest.skip("coordinates.csv not found")
    m1 = analyze()["cluster_metrics"]
    m2 = analyze()["cluster_metrics"]
    assert m1 == m2
