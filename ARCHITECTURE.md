# Arquitectura — cajas-alimentacion

## Visión general
Análisis espacial de puntos de entrega de cajas de alimentación (80,595 registros). Clustering KMeans, grilla de densidad, dashboard con Mapbox.

## Componentes principales

### Datos
- `data/raw/coordinates.csv` — 80,595 puntos (lat, lon)
- `data/processed/delivery_analysis.csv` — Puntos enriquecidos con cluster y grid_id
- `data/export/delivery_stats.json` — Estadísticas: total, clusters, grid_density

### Análisis (src/)
- `analyze.py` — analyze():
  - Lee coordinates.csv
  - KMeans clustering (n_clusters = min(10, n//100))
  - Grid 0.01° → grid_id
  - Guarda delivery_analysis.csv
  - Calcula centroides y densidad por grilla
  - Guarda delivery_stats.json

### Dashboard
- `dashboard.py` — Dash app:
  - Mapa Mapbox con 80K puntos (lento en navegador)
  - Histograma de clusters
  - Tabla de densidad de grilla
  - Estadísticas resumidas

## Flujo de datos
```
coordinates.csv → analyze.analyze → delivery_analysis.csv + delivery_stats.json
dashboard.py → Mapbox (80K puntos)
```

## Despliegue
- Render: `gunicorn dashboard:server` (ver `render.yaml`)
- **Problema**: 80K puntos en Mapbox = lento en navegador. Considerar: clustering servidor, downsampling, o deck.gl

## Tests
- `tests/test_analysis.py` — analyze() con fixtures CSV mock
- `tests/test_analyze.py` — Tests unitarios: estructura output, cluster count, grid density
- CI: pytest + coverage + ruff (Python 3.10, 3.11, 3.12)

## Seguridad
- `data/processed/delivery_analysis.csv` (4MB) en .gitignore
- Datos gubernamentales públicos, pero volumen grande