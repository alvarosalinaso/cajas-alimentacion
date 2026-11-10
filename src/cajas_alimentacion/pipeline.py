"""Orquestador: ingesta, validación, clustering, métricas y salidas.

Uso::

    python -m cajas_alimentacion              # pipeline completo
    python -m cajas_alimentacion --no-sync    # sin reescribir el README
"""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from cajas_alimentacion import clustering, data_loader, exports, metrics, reporting
from cajas_alimentacion.config import ProjectPaths
from cajas_alimentacion.logging_config import setup_logging
from cajas_alimentacion.validator import SchemaError

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Resultados en memoria de una ejecución (los usan los tests y el dashboard)."""

    analysis: pd.DataFrame
    stats: dict[str, Any]
    findings: dict[str, Any]
    outputs: list[Path] = field(default_factory=list)


def compute(csv_path: Path | None = None) -> PipelineResult:
    """Carga, valida y calcula todo sin escribir en disco."""
    df = data_loader.load_coordinates(csv_path)
    n_clusters = metrics.choose_n_clusters(len(df))
    fit = clustering.fit_clusters(df, n_clusters)

    analysis = metrics.add_grid(df.assign(cluster=fit.labels))
    density = metrics.grid_density(analysis)
    dist_km = metrics.distance_to_centers_km(fit.coords_proj, fit.labels, fit.centers_proj)
    clusters = metrics.cluster_summary(fit.labels, dist_km, fit.centers_wgs84)
    quality = metrics.clustering_quality(fit.coords_proj, fit.labels, fit.inertia)
    findings = metrics.key_findings(analysis, density, clusters, dist_km)

    stats = {
        "total_deliveries": len(analysis),
        "clusters": clusters,
        "grid_density": density.head(20).to_dict("records"),
        "n_grid_cells": len(density),
        "cluster_metrics": quality,
        "findings": findings,
    }
    logger.info("%d entregas, %d zonas, %d celdas", len(analysis), len(clusters), len(density))
    return PipelineResult(analysis=analysis, stats=stats, findings=findings)


def write_outputs(
    result: PipelineResult, paths: ProjectPaths, sync_docs: bool = True
) -> list[Path]:
    """Persiste CSV y JSON; opcionalmente sincroniza los marcadores del README."""
    written = [
        exports.write_csv(result.analysis, paths.processed_csv),
        exports.write_json(result.stats, paths.stats_json),
    ]
    if sync_docs:
        reporting.sync_document(
            paths.readme,
            reporting.findings_replacements(
                result.findings, result.stats["clusters"], result.stats["cluster_metrics"]
            ),
        )
    return written


def run(
    paths: ProjectPaths | None = None, csv_path: Path | None = None, sync_docs: bool = True
) -> PipelineResult:
    """Ejecuta el pipeline completo."""
    paths = paths or ProjectPaths.default()
    result = compute(csv_path or paths.raw_csv)
    result.outputs = write_outputs(result, paths, sync_docs)
    return result


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="cajas_alimentacion",
        description="Cobertura y zonas de reparto de cajas de alimentación (Santiago).",
    )
    parser.add_argument("--no-sync", action="store_true", help="No reescribir el README.")
    parser.add_argument("--log-level", default=None, help="DEBUG, INFO, WARNING...")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada CLI; devuelve el código de salida."""
    args = _parse_args(argv)
    setup_logging(args.log_level)
    try:
        result = run(sync_docs=not args.no_sync)
    except FileNotFoundError:
        return 2
    except SchemaError:
        logger.exception("Datos de entrada inválidos")
        return 3
    logger.info("Listo: %d salidas", len(result.outputs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
