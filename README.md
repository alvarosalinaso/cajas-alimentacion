# Delivery Coverage Engine: cajas de alimentación, Santiago

[![CI](https://github.com/alvarosalinaso/cajas-alimentacion/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/cajas-alimentacion/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Dash](https://img.shields.io/badge/App-Dash-008DE4?logo=plotly&logoColor=white)](dashboard.py)
[![Estado](https://img.shields.io/badge/estado-producción-2ea44f)](#reproducibilidad)
[![Licencia](https://img.shields.io/badge/licencia-MIT-green)](LICENSE)

Pipeline que convierte un registro plano de puntos de entrega en zonas operativas de reparto, un mapa de densidad y una curva de cobertura: cuántas celdas del territorio hay que atender para llegar al 50 %, 80 % y 90 % de las entregas.

---

## Problema

Un programa de distribución masiva de cajas de alimentación genera decenas de miles de puntos de entrega dispersos por la ciudad. Sin una agregación espacial, la planificación logística (cuántas rutas, dónde poner centros de acopio, qué zonas priorizar) se hace a ojo y no hay forma de medir:

- **Concentración:** ¿la demanda está repartida o se concentra en pocas zonas?
- **Distancia operativa:** ¿qué tan lejos queda cada entrega del centro de su zona?
- **Cobertura marginal:** ¿cuánto territorio hay que cubrir para atender a la mayoría?

---

## Hallazgos y métricas

Cifras calculadas por el pipeline (`python -m cajas_alimentacion`) y reinyectadas en este README.

<!-- FIND:headline -->
- **80.595** entregas en **12.253** coordenadas distintas (84.8 % son repeticiones de un punto ya listado).
- Se agrupan en **10** zonas; la mayor concentra 18.8 % de las entregas.
- Distancia en línea recta al centro de su zona: media **0.65 km**, P90 **0.99 km** (~1.9 min de media a 20 km/h, velocidad supuesta, no medida).
<!-- /FIND:headline -->

### Zonas de reparto (K-Means sobre coordenadas proyectadas)

<!-- FIND:clusters -->
| Zona | Entregas | Peso (%) | Dist. media (km) | Dist. P90 (km) | Min. medios* |
|---:|---:|---:|---:|---:|---:|
| 4 | 15.154 | 18.8 | 0.672 | 0.989 | 2.0 |
| 0 | 14.639 | 18.16 | 0.573 | 0.886 | 1.7 |
| 5 | 13.503 | 16.75 | 0.625 | 1.06 | 1.9 |
| 1 | 12.141 | 15.06 | 0.626 | 1.016 | 1.9 |
| 9 | 10.708 | 13.29 | 0.548 | 0.973 | 1.6 |
| 7 | 8.361 | 10.37 | 0.715 | 0.964 | 2.1 |
| 8 | 4.693 | 5.82 | 0.619 | 0.929 | 1.9 |
| 6 | 720 | 0.89 | 1.24 | 2.846 | 3.7 |
| 2 | 379 | 0.47 | 3.343 | 4.435 | 10.0 |
| 3 | 297 | 0.37 | 2.535 | 5.496 | 7.6 |
<!-- /FIND:clusters -->

\* Minutos estimados con una velocidad urbana **supuesta**, no medida.

Calidad del agrupamiento: <!-- FIND:quality -->
Silhouette 0.4336 · Davies-Bouldin 0.6805 (muestra de hasta 5.000 puntos, semilla fija).
<!-- /FIND:quality -->

### Curva de cobertura (grilla de 0,01°)

<!-- FIND:coverage -->
| Entregas cubiertas | Celdas necesarias | % de las celdas |
|---:|---:|---:|
| 50 % | 9 | 8.6 |
| 80 % | 17 | 16.2 |
| 90 % | 21 | 20.0 |

Las 10 celdas más densas concentran 58.9 % de las entregas (105 celdas de 0,01° en total).
<!-- /FIND:coverage -->

**Lectura operativa:** la curva de cobertura indica cuántas celdas de la grilla concentran la mayor parte de la demanda, que es donde conviene ubicar los puntos de acopio. Las distancias son en línea recta: sirven para comparar zonas entre sí, no para estimar tiempos reales de ruta.

---

## Arquitectura

```
cajas-alimentacion/
├── dashboard.py                    # App Dash (mapa, zonas, cobertura); la despliega render.yaml
├── src/cajas_alimentacion/
│   ├── config.py                   # Rutas desde la raíz o CAJAS_ROOT; parámetros y supuestos declarados
│   ├── logging_config.py           # Logging centralizado (sin print)
│   ├── data_loader.py              # Ingesta con pathlib: cabeceras saneadas, casteo estricto a float
│   ├── validator.py                # Fail-fast: columnas, nulos, coordenadas fuera de rango
│   ├── clustering.py               # K-Means sobre coordenadas proyectadas (semilla fija)
│   ├── metrics.py                  # Funciones puras: grilla, densidad, cobertura, distancias, división segura
│   ├── exports.py                  # CSV/JSON de salida
│   ├── reporting.py                # Tablas Markdown y sincronización de marcadores del README
│   └── pipeline.py                 # Orquestador y CLI: python -m cajas_alimentacion
├── data/raw/coordinates.csv        # Entrada (NO versionada: puede contener domicilios)
└── tests/                          # pytest con coordenadas sintéticas en tmp_path
```

**Privacidad:** `data/raw/`, `data/processed/` y `data/export/` están en `.gitignore`. Los tests y el CI usan coordenadas sintéticas.

---

## Reproducibilidad

**1. Clonar**
```bash
git clone https://github.com/alvarosalinaso/cajas-alimentacion.git && cd cajas-alimentacion
```

**2. Crear el entorno** (Windows: `.venv\Scripts\activate`)
```bash
python -m venv .venv && source .venv/bin/activate
```

**3. Instalar** (versiones fijadas, `numpy==1.26.4`)
```bash
pip install -r requirements-render.txt && pip install -e . --no-deps
```

**4. Ejecutar** (requiere `data/raw/coordinates.csv` con columnas `lat`, `lon`)
```bash
python -m cajas_alimentacion       # métricas, exports y README
python dashboard.py                # dashboard en http://localhost:8055
```

Desarrollo: `pip install -r requirements-dev.txt`, `pytest` y `ruff check .`.

---

## Autor

**Álvaro Salinas Ortiz** · Licenciado en Historia · Business Analytics & Operations

[LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz) · [GitHub](https://github.com/alvarosalinaso)
