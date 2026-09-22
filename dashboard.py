"""Dash Dashboard: Cajas de Alimentación — Santiago."""

from pathlib import Path

import dash
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html, no_update

app = dash.Dash(
    __name__,
    title="Cajas de Alimentación — Santiago",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

# Legado Haring re-mapeado a data-art oscuro (nombres intactos para no tocar llamadas).
HARING_COLORS = {
    "white": "#e8edf2",
    "red": "#f472b6",
    "yellow": "#F0E442",
    "blue": "#56B4E9",
    "green": "#009E73",
    "black": "#0a0e14",
}
# Okabe-Ito (2008), ordenado para dark: categórico colorblind-safe.
# Reemplaza la paleta Haring (no apta para codificar datos).
OKABE_ITO_DARK = ["#56B4E9", "#E69F00", "#009E73", "#F0E442",
                  "#CC79A7", "#D55E00", "#0072B2", "#999999"]
KPI_PALETTE = OKABE_ITO_DARK[:4]
CHART_COLORS = OKABE_ITO_DARK

BASE = Path(__file__).parent
RAW_CSV = BASE / "data" / "raw" / "coordinates.csv"
ANALYSIS_CSV = BASE / "data" / "processed" / "delivery_analysis.csv"
STATS_JSON = BASE / "data" / "export" / "delivery_stats.json"


def load_data():
    data = {}
    if RAW_CSV.exists():
        data["raw"] = pd.read_csv(RAW_CSV)
    if ANALYSIS_CSV.exists():
        data["analysis"] = pd.read_csv(ANALYSIS_CSV)
    if STATS_JSON.exists():
        import json
        with open(STATS_JSON) as f:
            data["stats"] = json.load(f)
    return data


DATA = load_data()

FONT = "'Inter','Segoe UI',system-ui,sans-serif"
FONT_DATA = "'JetBrains Mono',Consolas,'Courier New',monospace"
BG = "#0a0e14"
CARD = "#11161f"
HAIRLINE = "1px solid rgba(255,255,255,0.08)"
INK = "#e8edf2"
MUTED = "#8b94a3"

CHART_TEMPLATE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter,Segoe UI,sans-serif", color="#e8edf2", size=13),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.12)",
               title=dict(font=dict(size=13)), tickfont=dict(family="JetBrains Mono,monospace", size=12)),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.12)",
               title=dict(font=dict(size=13)), tickfont=dict(family="JetBrains Mono,monospace", size=12)),
    legend=dict(font=dict(size=12), bgcolor="rgba(0,0,0,0)"),
)


def haring_card(title, children):
    child_list = children if isinstance(children, list) else [children]
    return html.Div(
        style={
            "backgroundColor": CARD,
            "borderRadius": "14px",
            "padding": "22px",
            "marginBottom": "22px",
            "border": HAIRLINE,
            "boxShadow": "0 8px 32px rgba(0,0,0,0.35)",
        },
        children=[
            html.H3(title, style={
                "color": INK,
                "fontSize": "1.15rem",
                "fontWeight": "700",
                "fontFamily": FONT,
                "margin": "0 0 4px 0",
            }),
            html.Div("insights · metodología · decisión", style={
                "color": MUTED, "fontSize": "0.75rem",
                "fontFamily": FONT_DATA, "marginBottom": "12px",
            }),
        ] + child_list,
    )


def kpi_box(value, label, color, trend=None, delta=None):
    return html.Div(
        style={
            "flex": "1",
            "minWidth": "150px",
            "backgroundColor": CARD,
            "borderRadius": "12px",
            "padding": "18px 14px",
            "textAlign": "center",
            "border": HAIRLINE,
            "borderTop": f"3px solid {color}",
        },
        children=[
            html.Div(str(value), style={
                "fontSize": "2rem",
                "fontWeight": "800",
                "color": INK,
                "fontFamily": FONT_DATA,
                "lineHeight": "1.1",
            }),
            html.Div(label, style={
                "fontSize": "0.78rem",
                "color": MUTED,
                "marginTop": "6px",
                "fontFamily": FONT,
            }),
            sparkline(trend or [], color=color),
            html.Div(delta or "", title="Variación vs periodo anterior",
                     style={"fontSize": "0.78rem", "fontWeight": "700", "color": color,
                            "marginTop": "4px", "fontFamily": FONT_DATA}),
        ],
    )


def sparkline(values, color="#56B4E9"):
    if not values or len(values) < 2:
        return html.Div(style={"height": "32px"})
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=list(values), mode="lines",
        line={"color": color, "width": 2.5, "shape": "spline"},
        fill="tozeroy", hoverinfo="skip", showlegend=False,
    ))
    fig.update_layout(
        margin={"t": 0, "b": 0, "l": 0, "r": 0},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"visible": False}, yaxis={"visible": False}, height=32,
    )
    return dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"height": "32px"})


def insight_card(question, answer, accent="#56B4E9"):
    return html.Div(
        style={"backgroundColor": CARD, "border": HAIRLINE, "borderLeft": f"3px solid {accent}",
               "borderRadius": "10px", "padding": "14px 16px", "marginBottom": "12px"},
        children=[
            html.Div(question, style={"fontWeight": "700", "fontSize": "0.75rem", "letterSpacing": "0.08em",
                                      "textTransform": "uppercase", "color": accent, "fontFamily": FONT}),
            html.Div(answer, style={"marginTop": "4px", "color": INK, "lineHeight": "1.55", "fontSize": "0.92rem"}),
        ],
    )


def stat_row(stats):
    def _norm(item):
        if len(item) == 5:
            return item
        val, label, color = item
        return (val, label, color, None, None)
    return html.Div(
        style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "22px"},
        children=[
            kpi_box(val, label, color, trend, delta)
            for val, label, color, trend, delta in [_norm(item) for item in stats]
        ],
    )


def tab_style():
    return {
        "style": {
            "backgroundColor": "transparent",
            "color": MUTED,
            "border": "none",
            "borderBottom": "2px solid transparent",
            "fontWeight": "600",
            "fontFamily": FONT,
            "fontSize": "0.85rem",
            "letterSpacing": "0.04em",
            "padding": "14px 20px",
        },
        "selected_style": {
            "backgroundColor": "transparent",
            "color": INK,
            "border": "none",
            "borderBottom": "2px solid #22d3ee",
            "fontWeight": "700",
            "fontFamily": FONT,
            "fontSize": "0.85rem",
            "letterSpacing": "0.04em",
            "padding": "14px 20px",
        },
    }


DATA_CANVAS_SVG = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' width='1200' height='110' viewBox='0 0 1200 110'%3E"
    "%3Crect width='1200' height='110' fill='%230a0e14'/%3E"
    "%3Cg fill='%2322d3ee' opacity='0.16'%3E"
    + "".join(f"%3Ccircle cx='{x}' cy='{y}' r='2'/%3E" for x in range(30, 1200, 60) for y in range(20, 110, 30)) +
    "%3C/g%3E%3Cg fill='none' stroke='%23E69F00' stroke-width='2' opacity='0.7'%3E"
    "%3Cpath d='M0,85 Q200,40 400,65 T800,35 T1200,60'/%3E%3C/g%3E"
    "%3C/svg%3E"
)


app.layout = html.Div(
    style={
        "backgroundColor": BG,
        "minHeight": "100vh",
        "fontFamily": FONT,
        "color": INK,
    },
    children=[
        html.Div(
            style={
                "padding": "44px 20px 32px 20px",
                "textAlign": "center",
                "borderBottom": "1px solid rgba(255,255,255,0.08)",
            },
            children=[
                html.Div(
                    "PORTFOLIO · DATA ART",
                    style={"display": "inlineBlock", "color": "#22d3ee", "fontWeight": "700",
                           "letterSpacing": "0.28em", "fontSize": "0.7rem", "fontFamily": FONT_DATA,
                           "padding": "6px 0", "marginBottom": "10px",
                           "borderBottom": "1px solid rgba(34,211,238,0.4)"},
                ),
                html.H1("Cajas de Alimentación", style={
                    "fontSize": "2.4rem",
                    "fontWeight": "800",
                    "color": INK,
                    "margin": "0",
                    "fontFamily": FONT,
                    "letterSpacing": "-0.01em",
                }),
                html.P(id="header-stats", style={
                    "color": MUTED,
                    "marginTop": "8px",
                    "fontSize": "1rem",
                    "fontFamily": FONT_DATA,
                }),
            ],
        ),
        html.Div(style={
            "backgroundImage": f"url(\"{DATA_CANVAS_SVG}\")",
            "backgroundSize": "cover", "backgroundPosition": "center",
            "height": "110px", "borderBottom": "1px solid rgba(255,255,255,0.08)",
        }),
        dcc.Tabs(
            id="tabs",
            value="map",
            style={
                "backgroundColor": "transparent",
                "borderBottom": "1px solid rgba(255,255,255,0.08)",
                "padding": "0 20px",
            },
            children=[
                dcc.Tab(label="Mapa", value="map", **tab_style()),
                dcc.Tab(label="Densidad", value="density", **tab_style()),
                dcc.Tab(label="Clusters", value="clusters", **tab_style()),
                dcc.Tab(label="Estadísticas", value="stats", **tab_style()),
            ],
        ),
        html.Div(id="tab-content", style={"maxWidth": "1200px", "margin": "0 auto", "padding": "24px 20px"}),
    ],
)


@callback(Output("tab-content", "children"), Input("tabs", "value"))
def render_tab(tab):
    if "raw" not in DATA:
        return haring_card("ERROR", html.P("No hay datos disponibles", style={"fontWeight": "700", "fontFamily": FONT}))
    funcs = {"map": map_tab, "density": density_tab, "clusters": clusters_tab, "stats": stats_tab}
    return funcs.get(tab, map_tab)()


@callback(Output("header-stats", "children"), Input("tabs", "value"))
def update_header_stats(_tab):
    if "raw" not in DATA:
        return "Sin datos"
    df = DATA.get("analysis", DATA["raw"])
    total = len(df)
    return f"✦ {total:,} puntos de entrega — Santiago ✦"


def map_tab():
    df = DATA.get("analysis", DATA["raw"])
    if "cluster" not in df.columns:
        df["cluster"] = 0
    # Optimización: downsample para visualización si hay muchos puntos
    display_df = df.sample(n=min(15000, len(df)), random_state=42) if len(df) > 15000 else df
    fig = px.scatter_map(
        display_df, lat="lat", lon="lon", color="cluster",
        center={"lat": -33.45, "lon": -70.66}, zoom=11,
        map_style="carto-positron",
        title=f"MAPA DE ENTREGAS — {len(df):,} PUNTOS (mostrando {len(display_df):,})",
        color_discrete_sequence=CHART_COLORS,
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=600,
        margin=dict(t=0, b=0),
        font=dict(family=FONT, color=INK, size=14),
    )
    fig.update_traces(
        marker=dict(size=6),
        hovertemplate="%{lat:.4f}°, %{lon:.4f}°<br>" + f"{len(df):,} puntos totales<extra></extra>",
    )
    top_cluster = int(df["cluster"].value_counts().index[0]) if "cluster" in df.columns and len(df) else 0
    sample3d = df.sample(n=min(4000, len(df)), random_state=11) if len(df) > 4000 else df
    fig3d = go.Figure()
    for c in sorted(sample3d["cluster"].unique()) if "cluster" in sample3d.columns else [0]:
        cdf = sample3d[sample3d["cluster"] == c] if "cluster" in sample3d.columns else sample3d
        fig3d.add_trace(go.Scatter3d(
            x=cdf["lon"], y=cdf["lat"], z=[c] * len(cdf),
            mode="markers", name=f"Cluster {c}",
            marker=dict(size=3, opacity=0.7),
            hovertemplate="Cluster %{text}<br>Lon: %{x:.4f}<br>Lat: %{y:.4f}<extra></extra>",
            text=[c] * len(cdf),
        ))
    fig3d.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        height=600,
        font=dict(family=FONT, color=INK),
        title="PAISAJE 3D — gira, acerca y rota",
        scene=dict(
            xaxis_title="Longitud", yaxis_title="Latitud", zaxis_title="Cluster",
            xaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.12)"),
            yaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.12)"),
            zaxis=dict(backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(255,255,255,0.12)"),
        ),
        legend=dict(orientation="h", y=1.05),
    )
    return html.Div(children=[
        haring_card("KEY INSIGHTS", html.Div(children=[
            insight_card("¿Problema?", f"{len(df):,} entregas sin zonificación visible para rutas.", HARING_COLORS["red"]),
            insight_card("¿Metodología?", f"KMeans + grilla 0.01°; cluster dominante #{top_cluster} concentra la demanda.", HARING_COLORS["blue"]),
            insight_card("¿Decisión?", "Clic en barras de Clusters para aislar la zona y reasignar flota.", HARING_COLORS["green"]),
            sparkline(df["cluster"].value_counts().sort_index().values.tolist(), HARING_COLORS["red"]),
        ])),
        haring_card("MAPA DE ENTREGAS", dcc.Graph(figure=fig)),
        haring_card("PAISAJE 3D — arrastra para rotar", dcc.Graph(figure=fig3d)),
    ])


def density_tab():
    df = DATA.get("analysis", DATA["raw"])
    fig_density = px.density_map(
        df, lat="lat", lon="lon", radius=8,
        center={"lat": -33.45, "lon": -70.66}, zoom=11,
        map_style="carto-positron",
        title="MAPA DE DENSIDAD",
        color_continuous_scale=[
            [0, "#0a0e14"],
            [0.3, HARING_COLORS["yellow"]],
            [0.6, HARING_COLORS["red"]],
            [1, "#F0E442"],
        ],
    )
    fig_density.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=600,
        font=dict(family=FONT, color=INK),
    )
    if "grid_id" in df.columns:
        grid_counts = df.groupby("grid_id").agg(lat=("lat", "mean"), lon=("lon", "mean"), count=("lat", "count")).reset_index()
        top_grid = grid_counts.nlargest(10, "count")
        fig_bar = px.bar(top_grid, x="grid_id", y="count", title="TOP 10 ZONAS MÁS DENSAS",
                         color_discrete_sequence=[HARING_COLORS["red"]])
        fig_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
            xaxis_title="ZONA",
            yaxis_title="PUNTOS",
            font=dict(family=FONT, color=INK),
        )
        fig_bar.update_traces(
            marker_color=HARING_COLORS["red"],
            marker_line=dict(width=3, color=INK),
        )
    else:
        fig_bar = go.Figure()
    sample = df.sample(n=min(8000, len(df)), random_state=7) if len(df) > 8000 else df
    fig_contour = px.density_contour(
        sample, x="lon", y="lat",
        title="ARTE DE DENSIDAD — curvas de entrega",
    )
    fig_contour.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=500,
        font=dict(family=FONT, color=INK),
        xaxis_title="Longitud",
        yaxis_title="Latitud",
    )
    fig_contour.update_traces(
        contours_coloring="fill",
        colorscale=[
            [0, "#0a0e14"],
            [0.35, HARING_COLORS["yellow"]],
            [0.65, HARING_COLORS["red"]],
            [1, "#F0E442"],
        ],
        contours=dict(showlabels=True, labelfont=dict(size=11, color=INK)),
        hovertemplate="Lon: %{x:.4f}<br>Lat: %{y:.4f}<br>Densidad: %{z:.0f}<extra></extra>",
    )
    return html.Div([
        haring_card("MAPA DE DENSIDAD", dcc.Graph(figure=fig_density)),
        haring_card("TOP 10 ZONAS", dcc.Graph(figure=fig_bar)),
        haring_card("DENSIDAD COMO ARTE — contornos", html.Div(children=[
            dcc.Graph(figure=fig_contour),
            html.Div("Insight: los anillos concéntricos marcan los focos donde se acumula la demanda; ahí van las rutas prioritarias.",
                     style={"fontWeight": "700", "fontFamily": FONT, "marginTop": "8px"}),
        ])),
    ])


def clusters_tab():
    df = DATA.get("analysis", DATA["raw"])
    if "cluster" not in df.columns:
        return haring_card("CLUSTERS", html.P(
            "Ejecuta `python src/analyze.py` para generar clusters",
            style={"fontWeight": "700", "fontFamily": FONT},
        ))
    fig_scatter = px.scatter(
        df, x="lon", y="lat", color="cluster",
        title="CLUSTERS DE ENTREGAS",
        color_discrete_sequence=CHART_COLORS,
        opacity=0.7,
    )
    fig_scatter.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=500,
        font=dict(family=FONT, color=INK),
    )
    fig_scatter.update_traces(marker=dict(size=8, line=dict(width=2, color=INK)))
    stats = DATA.get("stats", {})
    clusters = stats.get("clusters", [])
    if clusters:
        cdf = pd.DataFrame(clusters)
        fig_bar = px.bar(cdf, x="id", y="count", title="ENTREGAS POR CLUSTER — clic para filtrar",
                         color_discrete_sequence=[HARING_COLORS["blue"]])
        fig_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=350,
            font=dict(family=FONT, color=INK),
        )
        fig_bar.update_traces(
            marker_color=HARING_COLORS["blue"],
            marker_line=dict(width=3, color=INK),
            hovertemplate="<b>Cluster %{x}</b><br>Entregas: %{y}<extra></extra>",
        )
        return html.Div([
            haring_card("CLUSTERS", dcc.Graph(figure=fig_scatter)),
            haring_card("DISTRIBUCIÓN POR CLUSTER", html.Div(children=[
                dcc.Graph(id="cluster-bar", figure=fig_bar),
                html.Div(id="cluster-crossfilter-output", style={"marginTop": "8px", "fontWeight": "800", "fontFamily": FONT}),
            ])),
        ])
    return haring_card("CLUSTERS", dcc.Graph(figure=fig_scatter))


@callback(
    Output("cluster-crossfilter-output", "children"),
    Input("cluster-bar", "clickData"),
    prevent_initial_call=True,
)
def cluster_crossfilter(click):
    if not click:
        return no_update
    c = click["points"][0].get("x", "?")
    return f"Cluster seleccionado: {c} — usa el tab Mapa con ese cluster para planificar rutas."


def stats_tab():
    stats = DATA.get("stats", {})
    if not stats:
        return haring_card("ESTADÍSTICAS", html.P(
            "No hay estadísticas disponibles",
            style={"fontWeight": "700", "fontFamily": FONT},
        ))
    total = stats.get("total_deliveries", len(DATA.get("raw", [])))
    n_clusters = len(stats.get("clusters", []))
    n_cells = stats.get("n_grid_cells", 0)
    avg_per_cluster = total // n_clusters if n_clusters else 0
    top_stats = stat_row([
        (f"{total:,}", "Total Entregas", HARING_COLORS["red"]),
        (str(n_clusters), "Clusters", HARING_COLORS["blue"]),
        (f"{avg_per_cluster:,}", "Prom/Cluster", HARING_COLORS["yellow"]),
        (str(n_cells), "Celdas Grid", HARING_COLORS["green"]),
    ])
    clusters = stats.get("clusters", [])
    if clusters:
        cdf = pd.DataFrame(clusters)
        fig_pie = px.pie(
            cdf, values="count",
            names=[f"Cluster {i}" for i in cdf["id"]],
            title="DISTRIBUCIÓN POR CLUSTER",
            hole=0.3,
            color_discrete_sequence=CHART_COLORS,
        )
        fig_pie.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
            font=dict(family=FONT, color=INK),
        )
        fig_pie.update_traces(
            marker=dict(line=dict(width=4, color=INK)),
        )
        return html.Div([
            top_stats,
            haring_card("DISTRIBUCIÓN POR CLUSTER", dcc.Graph(figure=fig_pie)),
        ])
    return html.Div([top_stats])


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8055)))
