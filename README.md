# Cajas de Alimentación — Santiago

Análisis espacial de 80,595 puntos de entrega de cajas de alimentación en Santiago de Chile. El proyecto aplica clustering K-Means, análisis de densidad por grilla y un dashboard interactivo en Dash para explorar la distribución geográfica del programa de asistencia alimentaria del gobierno chileno.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?logo=plotly&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-2.x-008DE4?logo=dash&logoColor=white)

---

## Datos

Datos georreferenciados del programa **Cajas de Alimentación** del gobierno de Chile. Cada registro contiene coordenadas de latitud y longitud de un punto de entrega en el área metropolitana de Santiago.

| Campo | Descripción |
|-------|-------------|
| `lat` | Latitud del punto de entrega |
| `lon` | Longitud del punto de entrega |
| `cluster` | Grupo asignado por K-Means (10 clusters) |
| `grid_id` | Celda de la grilla de densidad (0.01 grados) |

---

## Qué hace

El pipeline de análisis realiza cuatro operaciones principales:

1. **Clustering K-Means** — Agrupa los 80,595 puntos en 10 clusters geográficos con `scikit-learn`
2. **Grilla de densidad** — Divide el mapa en celdas de 0.01° × 0.01° y cuenta puntos por celda
3. **Exportación** — Genera `delivery_analysis.csv` y `delivery_stats.json`
4. **Dashboard interactivo** — Aplicación Dash con 4 pestañas para explorar los resultados

---

## Dashboard

```bash
python dashboard.py
```

| Pestaña | Qué muestra |
|---------|-------------|
| **Mapa** | Scatter plot interactivo con los 80,595 puntos coloreados por cluster |
| **Densidad** | Mapa de calor (density mapbox) + top 10 zonas más densas |
| **Clusters** | Scatter de clusters + barras de distribución por cluster |
| **Estadísticas** | KPIs, gráfico de torta y métricas resumen |

---

## Cómo correr

```bash
pip install -r requirements.txt
python src/analyze.py
python dashboard.py
```

El dashboard se ejecuta en `http://localhost:8055`.

---

## Estructura

```
cajas-alimentacion/
├── src/
│   └── analyze.py          # Pipeline de clustering y grilla
├── data/
│   ├── raw/coordinates.csv  # Datos originales
│   ├── processed/           # CSV con clusters y grilla
│   └── export/              # JSON con estadísticas
├── tests/
│   └── test_analysis.py     # Tests del pipeline
├── dashboard.py             # App Dash
├── requirements.txt
└── README.md
```

---

## Tech stack

- **Python 3.10+**
- **pandas** — Manipulación de datos
- **scikit-learn** — K-Means clustering
- **plotly** — Visualizaciones interactivas
- **dash** — Dashboard web
- **numpy** — Operaciones numéricas
