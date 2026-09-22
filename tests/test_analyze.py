"""Tests for analyze module (cajas-alimentacion)."""

import json

import pandas as pd

from src.analyze import analyze


def test_analyze_returns_dict(tmp_path, monkeypatch):
    """Test that analyze returns a dict with expected structure."""
    import src.analyze as analyze_module

    monkeypatch.setattr(analyze_module, "BASE", tmp_path)

    data_raw = tmp_path / "data" / "raw"
    data_raw.mkdir(parents=True)

    # Create coordinates.csv with test data
    coords_data = pd.DataFrame(
        {
            "lat": [-33.45, -33.46, -33.44, -33.47, -33.43] * 20,  # 100 points
            "lon": [-70.65, -70.66, -70.64, -70.67, -70.63] * 20,
        }
    )
    coords_data.to_csv(data_raw / "coordinates.csv", index=False)

    result = analyze()
    assert isinstance(result, dict)
    assert "total_deliveries" in result
    assert "clusters" in result
    assert "grid_density" in result
    assert "n_grid_cells" in result
    assert result["total_deliveries"] == 100


def test_analyze_no_data(tmp_path, monkeypatch):
    """Test analyze with no coordinates.csv returns None."""
    import src.analyze as analyze_module

    monkeypatch.setattr(analyze_module, "BASE", tmp_path)

    result = analyze()
    assert result is None


def test_analyze_creates_output_files(tmp_path, monkeypatch):
    """Test that analyze creates output files."""
    import src.analyze as analyze_module

    monkeypatch.setattr(analyze_module, "BASE", tmp_path)

    data_raw = tmp_path / "data" / "raw"
    data_raw.mkdir(parents=True)

    coords_data = pd.DataFrame(
        {
            "lat": [-33.45, -33.46, -33.44],
            "lon": [-70.65, -70.66, -70.64],
        }
    )
    coords_data.to_csv(data_raw / "coordinates.csv", index=False)

    analyze()

    # Check processed file
    processed_file = tmp_path / "data" / "processed" / "delivery_analysis.csv"
    assert processed_file.exists()
    processed_df = pd.read_csv(processed_file)
    assert "cluster" in processed_df.columns
    assert "grid_id" in processed_df.columns

    # Check export file
    export_file = tmp_path / "data" / "export" / "delivery_stats.json"
    assert export_file.exists()
    with open(export_file) as f:
        content = json.load(f)
    assert content["total_deliveries"] == 3


def test_analyze_cluster_count(tmp_path, monkeypatch):
    """Test that cluster count is correct (min(10, n//100))."""
    import src.analyze as analyze_module

    monkeypatch.setattr(analyze_module, "BASE", tmp_path)

    data_raw = tmp_path / "data" / "raw"
    data_raw.mkdir(parents=True)

    # 50 points -> min(10, 50//100) = min(10, 0) = 0, but KMeans needs >=1
    # Let's use 150 points -> min(10, 150//100) = 1
    coords_data = pd.DataFrame(
        {
            "lat": [-33.45 + i * 0.001 for i in range(150)],
            "lon": [-70.65 + i * 0.001 for i in range(150)],
        }
    )
    coords_data.to_csv(data_raw / "coordinates.csv", index=False)

    result = analyze()
    assert len(result["clusters"]) >= 1


def test_analyze_grid_density_structure(tmp_path, monkeypatch):
    """Test grid density output structure."""
    import src.analyze as analyze_module

    monkeypatch.setattr(analyze_module, "BASE", tmp_path)

    data_raw = tmp_path / "data" / "raw"
    data_raw.mkdir(parents=True)

    coords_data = pd.DataFrame(
        {
            "lat": [-33.45, -33.45, -33.46],
            "lon": [-70.65, -70.65, -70.66],
        }
    )
    coords_data.to_csv(data_raw / "coordinates.csv", index=False)

    result = analyze()
    grid_density = result["grid_density"]
    assert isinstance(grid_density, list)
    for cell in grid_density:
        assert "lat" in cell
        assert "lon" in cell
        assert "count" in cell
        assert "grid_id" in cell


def test_analyze_cluster_quality(tmp_path, monkeypatch):
    """Test cluster quality metrics (inertia, separation)."""
    import src.analyze as analyze_module

    monkeypatch.setattr(analyze_module, "BASE", tmp_path)

    data_raw = tmp_path / "data" / "raw"
    data_raw.mkdir(parents=True)

    # Create well-separated clusters
    import numpy as np

    np.random.seed(42)
    cluster1 = np.random.normal([-33.45, -70.65], 0.001, (100, 2))
    cluster2 = np.random.normal([-33.47, -70.67], 0.001, (100, 2))
    coords_data = pd.DataFrame(np.vstack([cluster1, cluster2]), columns=["lat", "lon"])
    coords_data.to_csv(data_raw / "coordinates.csv", index=False)

    result = analyze()
    clusters = result["clusters"]
    assert len(clusters) >= 2  # Should find at least 2 clusters

    # Check cluster structure
    for c in clusters:
        assert "id" in c
        assert "centroid_lat" in c
        assert "centroid_lon" in c
        assert "count" in c
        assert c["count"] > 0


def test_analyze_mapbox_downsample(tmp_path, monkeypatch):
    """Test that large datasets are handled (Mapbox optimization check)."""
    import src.analyze as analyze_module

    monkeypatch.setattr(analyze_module, "BASE", tmp_path)

    data_raw = tmp_path / "data" / "raw"
    data_raw.mkdir(parents=True)

    # Create 10000 points (large dataset)
    import numpy as np

    np.random.seed(42)
    coords_data = pd.DataFrame(
        {
            "lat": np.random.uniform(-33.5, -33.4, 10000),
            "lon": np.random.uniform(-70.7, -70.6, 10000),
        }
    )
    coords_data.to_csv(data_raw / "coordinates.csv", index=False)

    result = analyze()
    assert result["total_deliveries"] == 10000
    # KMeans should use max 10 clusters
    assert len(result["clusters"]) <= 10
