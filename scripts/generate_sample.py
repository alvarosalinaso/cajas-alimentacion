"""Genera ``data/sample/sample_coordinates.csv``: 500 puntos sintéticos en Santiago.

No contiene domicilios reales. Se usa como entrada de demo (Render) y de CI
cuando ``data/raw/coordinates.csv`` no existe. Reproducible (semilla fija)::

    python scripts/generate_sample.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

SEED = 42
N_POINTS = 500
#: Centros aproximados de comunas de Santiago (lat, lon) y peso relativo.
HUBS: tuple[tuple[float, float, float], ...] = (
    (-33.4489, -70.6693, 0.25),  # Santiago Centro
    (-33.5167, -70.7333, 0.20),  # Maipú
    (-33.6110, -70.5750, 0.20),  # Puente Alto
    (-33.3750, -70.7340, 0.15),  # Pudahuel
    (-33.5420, -70.6380, 0.15),  # La Granja / San Ramón
    (-33.2000, -70.6700, 0.05),  # Colina (periferia)
)
SPREAD_DEG = 0.012


def generate(n: int = N_POINTS, seed: int = SEED) -> pd.DataFrame:
    """Puntos normales alrededor de cada centro, en proporción a su peso."""
    rng = np.random.default_rng(seed)
    centers = np.array([(lat, lon) for lat, lon, _ in HUBS])
    weights = np.array([w for *_, w in HUBS])
    idx = rng.choice(len(HUBS), size=n, p=weights / weights.sum())
    coords = centers[idx] + rng.normal(0, SPREAD_DEG, size=(n, 2))
    return pd.DataFrame(coords.round(6), columns=["lat", "lon"])


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    out = Path(__file__).resolve().parents[1] / "data" / "sample" / "sample_coordinates.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    generate().to_csv(out, index=False)
    logger.info("Muestra sintética escrita en %s", out)


if __name__ == "__main__":
    main()
