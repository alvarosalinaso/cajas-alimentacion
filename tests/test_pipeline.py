import json

import numpy as np
import pandas as pd
import pytest

from cajas_alimentacion import data_loader, exports, metrics, pipeline, reporting
from cajas_alimentacion.config import ProjectPaths
from cajas_alimentacion.validator import SchemaError, validate_coordinates


def test_loader_sanea_cabeceras_y_bom(tmp_path):
    p = tmp_path / "c.csv"
    p.write_text("﻿ Lat ,LON\n-33.4,-70.6\n-33.5,-70.7\n", encoding="utf-8")
    df = data_loader.load_coordinates(p)
    assert list(df.columns) == ["lat", "lon"]
    assert df["lat"].dtype == "float64"


def test_loader_errores(tmp_path):
    with pytest.raises(FileNotFoundError):
        data_loader.load_coordinates(tmp_path / "no.csv")
    bad = tmp_path / "b.csv"
    bad.write_text("lat,lon\n-33.4,abc\n", encoding="utf-8")
    with pytest.raises(SchemaError, match="no numéricos"):
        data_loader.load_coordinates(bad)
    miss = tmp_path / "m.csv"
    miss.write_text("lat,x\n1,2\n", encoding="utf-8")
    with pytest.raises(SchemaError, match="faltan columnas"):
        data_loader.load_coordinates(miss)


@pytest.mark.parametrize(
    "df",
    [
        pd.DataFrame({"lat": [], "lon": []}),
        pd.DataFrame({"lat": [1.0, np.nan], "lon": [1.0, 2.0]}),
        pd.DataFrame({"lat": [100.0], "lon": [1.0]}),
        pd.DataFrame({"lat": [1.0], "lon": [200.0]}),
        pd.DataFrame({"lat": ["a"], "lon": [1.0]}),
    ],
)
def test_validator_rechaza(df):
    with pytest.raises(SchemaError):
        validate_coordinates(df)


def test_metricas_basicas(coords_df):
    assert metrics.choose_n_clusters(50) == 1
    assert metrics.choose_n_clusters(10_000) == 10
    assert metrics.safe_div(1, 0) == 0.0
    dens = metrics.grid_density(metrics.add_grid(coords_df))
    assert dens["count"].sum() == len(coords_df)
    cov = metrics.cells_to_cover(dens)
    assert [c["nivel_pct"] for c in cov] == [50, 80, 90]
    assert cov[0]["celdas"] <= cov[1]["celdas"] <= cov[2]["celdas"] <= len(dens)


def test_compute_y_cifras(project):
    res = pipeline.compute(project.raw_csv)
    f = res.findings
    assert f["total_entregas"] == 800
    assert f["n_zonas"] == 8
    assert f["puntos_unicos"] <= 800
    assert sum(c["count"] for c in res.stats["clusters"]) == 800
    assert 0 < f["dist_media_km"] < f["dist_p90_km"]


def test_pipeline_determinista_y_json_estricto(project):
    r1 = pipeline.run(project, sync_docs=False)
    first = project.stats_json.read_text(encoding="utf-8")
    pipeline.run(project, sync_docs=False)
    assert project.stats_json.read_text(encoding="utf-8") == first
    assert json.loads(first)["total_deliveries"] == 800
    assert len(r1.outputs) == 2
    assert pd.read_csv(project.processed_csv).shape[0] == 800


def test_sync_readme(project):
    pipeline.run(project, sync_docs=True)
    text = project.readme.read_text(encoding="utf-8")
    assert "| Zona |" in text
    assert "Silhouette" in text
    assert reporting.sync_document(project.readme, {"quality": "zzz"}) is True
    assert reporting.sync_document(project.readme, {"nada": "zzz"}) is False
    assert reporting.sync_document(project.root / "no.md", {"a": "b"}) is False


def test_exports_sanitize(tmp_path):
    data = {"a": float("nan"), "b": np.int64(3), "c": [np.float64(1.5)]}
    out = exports.write_json(data, tmp_path / "x.json")
    assert json.loads(out.read_text(encoding="utf-8")) == {"a": None, "b": 3, "c": [1.5]}


def test_main_codigos_de_salida(tmp_path, monkeypatch):
    monkeypatch.setenv("CAJAS_ROOT", str(tmp_path))
    assert ProjectPaths.default().root == tmp_path.resolve()
    assert pipeline.main(["--no-sync"]) == 2
    raw = ProjectPaths.default().raw_csv
    raw.parent.mkdir(parents=True)
    raw.write_text("lat,lon\n1,2\n", encoding="utf-8")
    assert pipeline.main(["--no-sync", "--log-level", "ERROR"]) == 0
    raw.write_text("foo\n1\n", encoding="utf-8")
    assert pipeline.main(["--no-sync"]) == 3
