"""Dash Dashboard: Cajas de Alimentación — Santiago."""

from pathlib import Path

import dash
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

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


def kpi_box(value, label, color, index):
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


def stat_row(stats):
    return html.Div(
        style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "25px"},
        children=[
            kpi_box(val, label, color, i)
            for i, (val, label, color) in enumerate(stats)
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
                html.P("✦ 80,595 puntos de entrega — Santiago ✦", style={
                    "color": HARING_COLORS["black"],
                    "marginTop": "10px",
                    "fontSize": "1.1rem",
                    "fontWeight": "700",
                    "fontFamily": FONT,
                }),
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


def map_tab():
    df = DATA.get("analysis", DATA["raw"])
    if "cluster" not in df.columns:
        df["cluster"] = 0
    fig = px.scatter_mapbox(
        df, lat="lat", lon="lon", color="cluster",
        center={"lat": -33.45, "lon": -70.66}, zoom=11,
        mapbox_style="carto-positron",
        title=f"MAPA DE ENTREGAS — {len(df):,} PUNTOS",
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
    fig.update_traces(marker=dict(size=10, line=dict(width=2, color=HARING_COLORS["black"])))
    return haring_card("MAPA DE ENTREGAS", dcc.Graph(figure=fig))


def density_tab():
    df = DATA.get("analysis", DATA["raw"])
    fig_density = px.density_mapbox(
        df, lat="lat", lon="lon", radius=8,
        center={"lat": -33.45, "lon": -70.66}, zoom=11,
        mapbox_style="carto-positron",
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
    return html.Div([
        haring_card("MAPA DE DENSIDAD", dcc.Graph(figure=fig_density)),
        haring_card("TOP 10 ZONAS", dcc.Graph(figure=fig_bar)),
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
        fig_bar = px.bar(cdf, x="id", y="count", title="ENTREGAS POR CLUSTER",
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
        )
        return html.Div([
            haring_card("CLUSTERS", dcc.Graph(figure=fig_scatter)),
            haring_card("DISTRIBUCIÓN POR CLUSTER", dcc.Graph(figure=fig_bar)),
        ])
    return haring_card("CLUSTERS", dcc.Graph(figure=fig_scatter))


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
