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
    result = analyze()
    assert result is not None
    assert isinstance(result, dict)


def test_analyze_returns_expected_keys():
    result = analyze()
    assert result is not None
    expected_keys = {"total_deliveries", "clusters", "grid_density", "n_grid_cells", "cluster_metrics"}
    assert expected_keys == set(result.keys())


def test_cluster_count():
    result = analyze()
    assert result is not None
    assert len(result["clusters"]) == 10


def test_delivery_analysis_csv_columns(analysis_df):
    expected_columns = {"lat", "lon", "cluster", "grid_id"}
    assert expected_columns.issubset(set(analysis_df.columns))


def test_total_deliveries(stats):
    assert stats["total_deliveries"] == 80595
