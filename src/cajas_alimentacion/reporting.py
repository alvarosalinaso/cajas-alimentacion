"""Sincroniza las cifras del pipeline con los marcadores ``FIND`` del README."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_MARKER = r"<!-- FIND:{key} -->.*?<!-- /FIND:{key} -->"


def _fmt(n: int | float) -> str:
    return f"{n:,}".replace(",", ".")


def findings_replacements(
    findings: dict[str, Any], clusters: list[dict[str, Any]], quality: dict[str, Any]
) -> dict[str, str]:
    """Bloques Markdown por clave de marcador, calculados desde los resultados."""
    f = findings
    headline = (
        f"- **{_fmt(f['total_entregas'])}** entregas en **{_fmt(f['puntos_unicos'])}** "
        f"coordenadas distintas ({f['repetidos_pct']} % son repeticiones de un punto ya listado).\n"
        f"- Se agrupan en **{f['n_zonas']}** zonas; la mayor concentra "
        f"{f['zona_mayor']['share_pct']} % de las entregas.\n"
        f"- Distancia en línea recta al centro de su zona: media **{f['dist_media_km']} km**, "
        f"P90 **{f['dist_p90_km']} km** "
        f"(~{f['tiempo_medio_min']} min de media a {f['velocidad_supuesta_kmh']:g} km/h, "
        "velocidad supuesta, no medida)."
    )
    rows = ["| Zona | Entregas | Peso (%) | Dist. media (km) | Dist. P90 (km) | Min. medios* |"]
    rows.append("|---:|---:|---:|---:|---:|---:|")
    rows += [
        f"| {c['id']} | {_fmt(c['count'])} | {c['share_pct']} | {c['mean_km']} | "
        f"{c['p90_km']} | {c['est_min_mean']} |"
        for c in clusters
    ]
    cov = [
        "| Entregas cubiertas | Celdas necesarias | % de las celdas |",
        "|---:|---:|---:|",
    ] + [f"| {r['nivel_pct']} % | {r['celdas']} | {r['celdas_pct']} |" for r in f["cobertura"]]
    cov.append("")
    cov.append(
        f"Las 10 celdas más densas concentran {f['top10_celdas_pct']} % de las entregas "
        f"({_fmt(f['n_celdas'])} celdas de 0,01° en total)."
    )
    qual = (
        f"Silhouette {quality.get('silhouette_score', 'n/d')} · "
        f"Davies-Bouldin {quality.get('davies_bouldin_score', 'n/d')} "
        f"(muestra de hasta 5.000 puntos, semilla fija)."
    )
    return {
        "headline": headline,
        "clusters": "\n".join(rows),
        "coverage": "\n".join(cov),
        "quality": qual,
    }


def sync_document(path: Path, replacements: dict[str, str]) -> bool:
    """Reescribe el contenido entre marcadores; avisa si falta alguno. Devuelve si cambió."""
    if not path.exists():
        logger.warning("No existe %s; se omite la sincronización", path)
        return False
    text = path.read_text(encoding="utf-8")
    new = text
    for key, body in replacements.items():
        pattern = re.compile(_MARKER.format(key=re.escape(key)), re.DOTALL)
        block = f"<!-- FIND:{key} -->\n{body}\n<!-- /FIND:{key} -->"
        if not pattern.search(new):
            logger.warning("Marcador FIND:%s no encontrado en %s", key, path.name)
            continue
        new = pattern.sub(lambda _m, b=block: b, new)
    if new == text:
        return False
    path.write_text(new, encoding="utf-8")
    logger.info("Sincronizado %s", path.name)
    return True
