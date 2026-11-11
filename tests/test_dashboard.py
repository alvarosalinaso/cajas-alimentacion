"""Verificación headless del dashboard Dash: layout y callbacks sin servidor."""

import importlib

import pytest


@pytest.fixture
def dashboard(project, monkeypatch):
    monkeypatch.setenv("CAJAS_ROOT", str(project.root))
    import dashboard as dash_module

    return importlib.reload(dash_module)


def test_tabs_renderizan_sin_excepciones(dashboard):
    assert dashboard.server is not None
    assert "analysis" in dashboard.DATA
    for tab in ("map", "density", "clusters", "stats", "otro"):
        assert dashboard.render_tab(tab) is not None
    assert "800" in dashboard.update_header_stats("map")
    assert dashboard.stats_crossfilter({"points": [{"label": "3"}]}).startswith("Seleccionado")


def test_sin_datos(tmp_path, monkeypatch):
    monkeypatch.setenv("CAJAS_ROOT", str(tmp_path))
    import dashboard as dash_module

    mod = importlib.reload(dash_module)
    assert mod.DATA == {}
    assert mod.update_header_stats("map") == "Sin datos"
    assert mod.render_tab("map") is not None
