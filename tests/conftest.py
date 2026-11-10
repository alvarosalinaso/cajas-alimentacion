"""Fixtures compartidas: coordenadas sintéticas en ``tmp_path`` (sin tocar el repo)."""

import numpy as np
import pandas as pd
import pytest

from cajas_alimentacion.config import ProjectPaths


@pytest.fixture
def coords_df() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    centers = [(-33.40, -70.60), (-33.50, -70.70)]
    parts = [
        pd.DataFrame(
            {
                "lat": c[0] + rng.normal(0, 0.01, 400).round(5),
                "lon": c[1] + rng.normal(0, 0.01, 400).round(5),
            }
        )
        for c in centers
    ]
    return pd.concat(parts, ignore_index=True)


@pytest.fixture
def project(tmp_path, coords_df) -> ProjectPaths:
    paths = ProjectPaths(root=tmp_path)
    paths.raw_csv.parent.mkdir(parents=True)
    coords_df.to_csv(paths.raw_csv, index=False)
    paths.readme.write_text(
        "# T\n<!-- FIND:headline -->\nx\n<!-- /FIND:headline -->\n"
        "<!-- FIND:clusters -->\nx\n<!-- /FIND:clusters -->\n"
        "<!-- FIND:coverage -->\nx\n<!-- /FIND:coverage -->\n"
        "<!-- FIND:quality -->\nx\n<!-- /FIND:quality -->\n",
        encoding="utf-8",
    )
    return paths
