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

HARING_COLORS = {
    "white": "#ffffff",
    "red": "#ff0000",
    "yellow": "#ffdd00",
    "blue": "#0066ff",
    "green": "#00cc44",
    "black": "#000000",
}
KPI_PALETTE = [HARING_COLORS["red"], HARING_COLORS["blue"], HARING_COLORS["yellow"], HARING_COLORS["green"]]
CHART_COLORS = [HARING_COLORS["red"], HARING_COLORS["blue"], HARING_COLORS["yellow"], HARING_COLORS["green"],
                "#ff6600", "#cc00cc"]

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

FONT = "'Arial Rounded MT Bold', 'Arial', sans-serif"


def haring_card(title, children):
    child_list = children if isinstance(children, list) else [children]
    return html.Div(
        style={
            "backgroundColor": HARING_COLORS["white"],
            "borderRadius": "12px",
            "padding": "25px",
            "marginBottom": "25px",
            "border": f"4px solid {HARING_COLORS['black']}",
        },
        children=[
            html.H3(title, style={
                "color": HARING_COLORS["black"],
                "fontSize": "1.4rem",
                "fontWeight": "900",
                "fontFamily": FONT,
                "marginBottom": "15px",
                "paddingBottom": "10px",
                "borderBottom": f"3px solid {HARING_COLORS['black']}",
            }),
        ] + child_list,
    )


def kpi_box(value, label, color):
    return html.Div(
        style={
            "flex": "1",
            "minWidth": "150px",
            "backgroundColor": HARING_COLORS["white"],
            "borderRadius": "10px",
            "padding": "24px 16px",
            "textAlign": "center",
            "border": f"4px solid {HARING_COLORS['black']}",
            "position": "relative",
            "overflow": "hidden",
        },
        children=[
            html.Div("●", style={
                "position": "absolute", "top": "8px", "right": "10px",
                "fontSize": "1.2rem", "color": color,
            }),
            html.Div("✦", style={
                "position": "absolute", "bottom": "8px", "left": "10px",
                "fontSize": "1rem", "color": color,
            }),
            html.Div(str(value), style={
                "fontSize": "3.2rem",
                "fontWeight": "900",
                "color": color,
                "fontFamily": FONT,
                "lineHeight": "1.1",
            }),
            html.Div(label, style={
                "fontSize": "0.85rem",
                "color": HARING_COLORS["black"],
                "marginTop": "6px",
                "fontWeight": "700",
                "fontFamily": FONT,
                "textTransform": "uppercase",
            }),
        ],
    )


def sparkline(values, color="#ff0000"):
    if not values or len(values) < 2:
        return html.Div(style={"height": "32px"})
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=list(values), mode="lines",
        line={"color": color, "width": 3, "shape": "spline"},
        fill="tozeroy", hoverinfo="skip", showlegend=False,
    ))
    fig.update_layout(
        margin={"t": 0, "b": 0, "l": 0, "r": 0},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis={"visible": False}, yaxis={"visible": False}, height=32,
    )
    return dcc.Graph(figure=fig, config={"displayModeBar": False}, style={"height": "32px"})


def insight_card(question, answer, accent="#ff0000"):
    return html.Div(
        style={"backgroundColor": "#ffffff", "border": "4px solid #000000", "borderLeft": f"10px solid {accent}", "padding": "14px 16px", "marginBottom": "12px"},
        children=[
            html.Div(question, style={"fontWeight": "900", "textTransform": "uppercase", "fontSize": "0.75rem", "letterSpacing": "0.06em", "fontFamily": FONT}),
            html.Div(answer, style={"marginTop": "4px", "fontFamily": FONT, "lineHeight": "1.5"}),
        ],
    )


def stat_row(stats):
    return html.Div(
        style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "25px"},
        children=[
            kpi_box(val, label, color)
            for val, label, color in stats
        ],
    )


def tab_style():
    return {
        "style": {
            "backgroundColor": HARING_COLORS["white"],
            "color": HARING_COLORS["black"],
            "border": f"3px solid {HARING_COLORS['black']}",
            "borderRadius": "6px",
            "fontWeight": "800",
            "fontFamily": FONT,
            "textTransform": "uppercase",
            "letterSpacing": "0.5px",
            "margin": "4px",
        },
        "selected_style": {
            "backgroundColor": HARING_COLORS["yellow"],
            "color": HARING_COLORS["black"],
            "border": f"3px solid {HARING_COLORS['black']}",
            "borderRadius": "6px",
            "fontWeight": "800",
            "fontFamily": FONT,
            "textTransform": "uppercase",
            "letterSpacing": "0.5px",
            "margin": "4px",
        },
    }


app.layout = html.Div(
    style={
        "backgroundColor": HARING_COLORS["white"],
        "minHeight": "100vh",
        "fontFamily": FONT,
        "color": HARING_COLORS["black"],
    },
    children=[
        html.Div(
            style={
                "background": HARING_COLORS["white"],
                "padding": "32px 20px",
                "textAlign": "center",
                "borderBottom": f"4px solid {HARING_COLORS['black']}",
            },
            children=[
                html.Div(
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        "gap": "0",
                        "marginBottom": "12px",
                    },
                    children=[
                        html.Div(style={"height": "8px", "width": "80px", "backgroundColor": HARING_COLORS["red"]}),
                        html.Div(style={"height": "8px", "width": "80px", "backgroundColor": HARING_COLORS["yellow"]}),
                        html.Div(style={"height": "8px", "width": "80px", "backgroundColor": HARING_COLORS["blue"]}),
                    ],
                ),
                html.H1("CAJAS DE ALIMENTACIÓN", style={
                    "fontSize": "2.8rem",
                    "fontWeight": "900",
                    "color": HARING_COLORS["black"],
                    "margin": "0",
                    "fontFamily": FONT,
                    "letterSpacing": "3px",
                    "textTransform": "uppercase",
                }),
                html.P(id="header-stats", style={
                    "color": HARING_COLORS["black"],
                    "marginTop": "10px",
                    "fontSize": "1.1rem",
                    "fontWeight": "700",
                    "fontFamily": FONT,
                }),
                html.Div(style={"display": "flex", "justifyContent": "center", "gap": "10px", "marginTop": "12px"}, children=[
                    html.Div(style={"width": "44px", "height": "44px", "borderRadius": "50%", "backgroundColor": HARING_COLORS["red"], "border": f"3px solid {HARING_COLORS['black']}"}),
                    html.Div(style={"width": "44px", "height": "44px", "backgroundColor": HARING_COLORS["blue"], "border": f"3px solid {HARING_COLORS['black']}"}),
                    html.Div(style={"width": "0", "height": "0", "borderLeft": "26px solid transparent", "borderRight": "26px solid transparent", "borderBottom": f"44px solid {HARING_COLORS['yellow']}"}),
                ]),
            ],
        ),
        dcc.Tabs(
            id="tabs",
            value="map",
            style={
                "backgroundColor": HARING_COLORS["white"],
                "borderBottom": f"4px solid {HARING_COLORS['black']}",
                "padding": "8px 20px",
            },
            children=[
                dcc.Tab(label="● MAPA", value="map", **tab_style()),
                dcc.Tab(label="★ DENSIDAD", value="density", **tab_style()),
                dcc.Tab(label="■ CLUSTERS", value="clusters", **tab_style()),
                dcc.Tab(label="✦ ESTADÍSTICAS", value="stats", **tab_style()),
            ],
        ),
        html.Div(id="tab-content", style={"maxWidth": "1200px", "margin": "0 auto", "padding": "30px 20px"}),
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
        template="plotly_white",
        paper_bgcolor=HARING_COLORS["white"],
        plot_bgcolor=HARING_COLORS["white"],
        height=600,
        margin=dict(t=0, b=0),
        font=dict(family=FONT, color=HARING_COLORS["black"], size=14),
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
        template="plotly_white",
        paper_bgcolor=HARING_COLORS["white"],
        height=600,
        font=dict(family=FONT, color=HARING_COLORS["black"]),
        title="PAISAJE 3D — gira, acerca y rota",
        scene=dict(
            xaxis_title="Longitud", yaxis_title="Latitud", zaxis_title="Cluster",
            xaxis=dict(backgroundcolor=HARING_COLORS["white"], gridcolor="#dddddd"),
            yaxis=dict(backgroundcolor=HARING_COLORS["white"], gridcolor="#dddddd"),
            zaxis=dict(backgroundcolor=HARING_COLORS["white"], gridcolor="#dddddd"),
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
            [0, HARING_COLORS["white"]],
            [0.3, HARING_COLORS["yellow"]],
            [0.6, HARING_COLORS["red"]],
            [1, HARING_COLORS["black"]],
        ],
    )
    fig_density.update_layout(
        template="plotly_white",
        paper_bgcolor=HARING_COLORS["white"],
        plot_bgcolor=HARING_COLORS["white"],
        height=600,
        font=dict(family=FONT, color=HARING_COLORS["black"]),
    )
    if "grid_id" in df.columns:
        grid_counts = df.groupby("grid_id").agg(lat=("lat", "mean"), lon=("lon", "mean"), count=("lat", "count")).reset_index()
        top_grid = grid_counts.nlargest(10, "count")
        fig_bar = px.bar(top_grid, x="grid_id", y="count", title="TOP 10 ZONAS MÁS DENSAS",
                         color_discrete_sequence=[HARING_COLORS["red"]])
        fig_bar.update_layout(
            template="plotly_white",
            paper_bgcolor=HARING_COLORS["white"],
            plot_bgcolor=HARING_COLORS["white"],
            height=400,
            xaxis_title="ZONA",
            yaxis_title="PUNTOS",
            font=dict(family=FONT, color=HARING_COLORS["black"]),
        )
        fig_bar.update_traces(
            marker_color=HARING_COLORS["red"],
            marker_line=dict(width=3, color=HARING_COLORS["black"]),
        )
    else:
        fig_bar = go.Figure()
    sample = df.sample(n=min(8000, len(df)), random_state=7) if len(df) > 8000 else df
    fig_contour = px.density_contour(
        sample, x="lon", y="lat",
        title="ARTE DE DENSIDAD — curvas de entrega",
    )
    fig_contour.update_layout(
        template="plotly_white",
        paper_bgcolor=HARING_COLORS["white"],
        plot_bgcolor=HARING_COLORS["white"],
        height=500,
        font=dict(family=FONT, color=HARING_COLORS["black"]),
        xaxis_title="Longitud",
        yaxis_title="Latitud",
    )
    fig_contour.update_traces(
        contours_coloring="fill",
        colorscale=[
            [0, HARING_COLORS["white"]],
            [0.35, HARING_COLORS["yellow"]],
            [0.65, HARING_COLORS["red"]],
            [1, HARING_COLORS["black"]],
        ],
        contours=dict(showlabels=True, labelfont=dict(size=11, color=HARING_COLORS["black"])),
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
        template="plotly_white",
        paper_bgcolor=HARING_COLORS["white"],
        plot_bgcolor=HARING_COLORS["white"],
        height=500,
        font=dict(family=FONT, color=HARING_COLORS["black"]),
    )
    fig_scatter.update_traces(marker=dict(size=8, line=dict(width=2, color=HARING_COLORS["black"])))
    stats = DATA.get("stats", {})
    clusters = stats.get("clusters", [])
    if clusters:
        cdf = pd.DataFrame(clusters)
        fig_bar = px.bar(cdf, x="id", y="count", title="ENTREGAS POR CLUSTER — clic para filtrar",
                         color_discrete_sequence=[HARING_COLORS["blue"]])
        fig_bar.update_layout(
            template="plotly_white",
            paper_bgcolor=HARING_COLORS["white"],
            plot_bgcolor=HARING_COLORS["white"],
            height=350,
            font=dict(family=FONT, color=HARING_COLORS["black"]),
        )
        fig_bar.update_traces(
            marker_color=HARING_COLORS["blue"],
            marker_line=dict(width=3, color=HARING_COLORS["black"]),
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
            template="plotly_white",
            paper_bgcolor=HARING_COLORS["white"],
            plot_bgcolor=HARING_COLORS["white"],
            height=400,
            font=dict(family=FONT, color=HARING_COLORS["black"]),
        )
        fig_pie.update_traces(
            marker=dict(line=dict(width=4, color=HARING_COLORS["black"])),
        )
        return html.Div([
            top_stats,
            haring_card("DISTRIBUCIÓN POR CLUSTER", dcc.Graph(figure=fig_pie)),
        ])
    return html.Div([top_stats])


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8055)))
