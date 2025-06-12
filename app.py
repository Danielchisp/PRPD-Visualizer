import dash
import signal
import pandas as pd
import numpy as np
import os
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc  # NUEVO: Bootstrap components

# from data_processing import process_data
from plotting import (  # Custom plotting functions imported from the 'plotting' module
    create_scatter_layout,
    plot_class_map,
    plot_time_fft_single,
    plot_time_fft_multiple,
    plot_selected_PRPD_single,
    plot_selected_PRPD_multiple,
)
import plotly.graph_objects as go  # Used for detailed graph customization
from UserManual import USER_MANUAL_MD  # Importa el manual de usuario

from utils import build_export_dataframe

dash_server_process = None

classMapVariables = [
    {"label": "Peak to Peak Voltage", "value": "Vpp"},
    {"label": "Energy", "value": "Energy"},
    {"label": "Apparent Charge", "value": "Qapp"},
    {"label": "Equivalent Time", "value": "T2"},
    {"label": "Equivalent Frequency", "value": "W2"},
]


def create_dash_app(df, scatter_traces, time, impulse, host, port):

    global dash_server_process

    if dash_server_process:
        os.kill(dash_server_process.pid, signal.SIGTERM)
        dash_server_process = None
        time.sleep(1)  # Espera a que el puerto se libere

    # Initialization of the Dash application
    app = dash.Dash(
        __name__,
        title="TRPD Visualizer",
        external_stylesheets=[dbc.themes.BOOTSTRAP],  # NUEVO: Bootstrap theme
    )

    # Application layout
    app.layout = html.Div(
        [
            # A hidden store for storing zoom data from scatter plots
            dcc.Store(id="scatter-selected-zoom-data"),
            html.Div(
                [  # Main content of the app
                    html.Div(  # Title section
                        [
                            html.Div(
                                [
                                    # Main title of the application
                                    html.H1(
                                        "TRPD Pattern Visualizer",
                                        style={
                                            "textAlign": "left",
                                            "fontFamily": "Roboto, sans-serif",
                                            "color": "white",
                                            "margin": "0",
                                            "padding": "0",
                                            "fontSize": "35px",
                                            "fontWeight": "500",
                                            "letterSpacing": "1px",
                                            "flex": "1",
                                        },
                                    ),
                                    # Subtitle and version information
                                    html.Div(
                                        [
                                            html.Div(
                                                "Time-Resolved Partial Discharge Analyzer",
                                                style={
                                                    "textAlign": "right",
                                                    "color": "white",
                                                    "fontSize": "16px",
                                                    "paddingTop": "10px",
                                                    "fontWeight": "400",
                                                },
                                            ),
                                            html.Div(
                                                "2025 - V1.0",
                                                style={
                                                    "textAlign": "right",
                                                    "color": "white",
                                                    "fontSize": "12px",
                                                    "fontWeight": "400",
                                                },
                                            ),
                                        ],
                                        style={
                                            "position": "absolute",
                                            "right": "20px",
                                            "bottom": "50px",
                                        },
                                    ),
                                ],
                                style={
                                    "position": "relative",
                                    "height": "100%",
                                    "padding": "20px",
                                },
                            )
                        ],
                        style={
                            "background": "#03396c",  # "linear-gradient(90deg, #03396c, #6497b1)",  # Gradient background
                            "borderRadius": "10px 10px 0 0",  # Rounded corners
                            "marginBottom": "20px",
                            "height": "90px",
                            "boxShadow": "0 4px 12px rgba(0,0,0,0.2)",  # Shadow effect
                            "position": "relative",
                        },
                    ),
                    # html.Div([html.Button(id="button-1"), html.Button(id="button-2")]),
                    html.Div(  # Graphs section
                        [
                            # Tabs for switching between different views
                            dcc.Tabs(
                                [
                                    # Tab for the PD Data Analyzer
                                    dcc.Tab(  # Graphs
                                        label="PD Data Analyzer",
                                        children=[
                                            html.Div(
                                                [
                                                    # Botones con estética científica, colores sutiles y bordes redondeados
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    dbc.Button(
                                                                        "Download Selected TRPD Temporal Signals",
                                                                        id="button-1",
                                                                        color="primary",
                                                                        outline=True,
                                                                        size="sm",  # Cambiado a pequeño
                                                                        className="mb-1 me-1",  # Menos margen
                                                                        style={
                                                                            "width": "100%",
                                                                            "borderRadius": "20px",
                                                                            "backgroundColor": "#e3f0fc",
                                                                            "color": "#185a9d",
                                                                            "border": "1.5px solid #185a9d",
                                                                            "fontWeight": "500",
                                                                            "fontFamily": "Roboto, monospace",
                                                                            "boxShadow": "0 2px 8px rgba(24,90,157,0.07)",
                                                                            "padding": "2px 8px",  # Menos padding
                                                                            "fontSize": "13px",  # Más pequeño
                                                                        },
                                                                    ),
                                                                    dcc.Download(
                                                                        id="download-data-1"
                                                                    ),
                                                                ],
                                                                width="auto",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Button(
                                                                        "Download Selected Class. Map Temporal Signals",
                                                                        id="button-2",
                                                                        color="primary",
                                                                        outline=True,
                                                                        size="sm",
                                                                        className="mb-1 me-1",
                                                                        style={
                                                                            "width": "100%",
                                                                            "borderRadius": "20px",
                                                                            "backgroundColor": "#e3f0fc",
                                                                            "color": "#185a9d",
                                                                            "border": "1.5px solid #185a9d",
                                                                            "fontWeight": "500",
                                                                            "fontFamily": "Roboto, monospace",
                                                                            "boxShadow": "0 2px 8px rgba(24,90,157,0.07)",
                                                                            "padding": "2px 8px",
                                                                            "fontSize": "13px",
                                                                        },
                                                                    ),
                                                                    dcc.Download(
                                                                        id="download-data-2"
                                                                    ),
                                                                ],
                                                                width="auto",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Button(
                                                                        "Download Selected TRPD FFT",
                                                                        id="button-3",
                                                                        color="danger",
                                                                        outline=True,
                                                                        size="sm",
                                                                        className="mb-1 me-1",
                                                                        style={
                                                                            "width": "100%",
                                                                            "borderRadius": "20px",
                                                                            "backgroundColor": "#fbeaea",
                                                                            "color": "#b71c1c",
                                                                            "border": "1.5px solid #b71c1c",
                                                                            "fontWeight": "500",
                                                                            "fontFamily": "Roboto, monospace",
                                                                            "boxShadow": "0 2px 8px rgba(183,28,28,0.07)",
                                                                            "padding": "2px 8px",
                                                                            "fontSize": "13px",
                                                                        },
                                                                    ),
                                                                    dcc.Download(
                                                                        id="download-data-3"
                                                                    ),
                                                                ],
                                                                width="auto",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dbc.Button(
                                                                        "Download Selected Class. Map FFT",
                                                                        id="button-4",
                                                                        color="danger",
                                                                        outline=True,
                                                                        size="sm",
                                                                        className="mb-1",
                                                                        style={
                                                                            "width": "100%",
                                                                            "borderRadius": "20px",
                                                                            "backgroundColor": "#fbeaea",
                                                                            "color": "#b71c1c",
                                                                            "border": "1.5px solid #b71c1c",
                                                                            "fontWeight": "500",
                                                                            "fontFamily": "Roboto, monospace",
                                                                            "boxShadow": "0 2px 8px rgba(183,28,28,0.07)",
                                                                            "padding": "2px 8px",
                                                                            "fontSize": "13px",
                                                                        },
                                                                    ),
                                                                    dcc.Download(
                                                                        id="download-data-4"
                                                                    ),
                                                                ],
                                                                width="auto",
                                                            ),
                                                        ],
                                                        justify="center",
                                                        className="g-1",  # Menos espacio entre columnas
                                                        style={
                                                            "marginBottom": "0px"
                                                        },  # Menos margen inferior
                                                    ),
                                                ],
                                                style={
                                                    "marginBottom": "20px",
                                                    "borderRadius": "8px",
                                                    "padding": "10px",  # Menos padding
                                                    "backgroundColor": "#f8fafc",
                                                    "border": "1px solid #cfd8dc",
                                                    "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.04)",
                                                    "textAlign": "center",
                                                    "display": "flex",
                                                    "justifyContent": "center",
                                                    "alignItems": "center",
                                                },
                                            ),
                                            html.Div(
                                                [
                                                    # Scatter Plot Section
                                                    html.Div(
                                                        [
                                                            # Main Scatter Plot
                                                            html.Div(
                                                                [
                                                                    # DataTable with summary statistics
                                                                    dash.dash_table.DataTable(
                                                                        id="selected-values-metrics-table",
                                                                        columns=[
                                                                            {
                                                                                "name": "Vpp (mV)",
                                                                                "id": "Vpp",
                                                                            },
                                                                            {
                                                                                # Use Unicode superscript 2 for squared
                                                                                "name": "Energy (mV²)",
                                                                                "id": "Energy",
                                                                            },
                                                                            {
                                                                                "name": "Average\nTime (us)",
                                                                                "id": "t_mean",
                                                                            },
                                                                            {
                                                                                "name": "Time Range (us)",
                                                                                "id": "time_range",
                                                                            },
                                                                            {
                                                                                "name": "First PD (us)",
                                                                                "id": "first_pd",
                                                                            },
                                                                            {
                                                                                "name": "Npd",
                                                                                "id": "Npd",
                                                                            },
                                                                        ],
                                                                        data=[
                                                                            {
                                                                                "Vpp": (
                                                                                    round(
                                                                                        df[
                                                                                            "Vpp"
                                                                                        ].mean()
                                                                                        * 1000,
                                                                                        2,
                                                                                    )
                                                                                    if not df.empty
                                                                                    else ""
                                                                                ),
                                                                                "Energy": (
                                                                                    round(
                                                                                        df[
                                                                                            "Energy"
                                                                                        ].mean(),
                                                                                        2,
                                                                                    )
                                                                                    if not df.empty
                                                                                    else ""
                                                                                ),
                                                                                "t_mean": (
                                                                                    round(
                                                                                        df[
                                                                                            "x"
                                                                                        ].mean(),
                                                                                        2,
                                                                                    )
                                                                                    if not df.empty
                                                                                    else ""
                                                                                ),
                                                                                "Npd": (
                                                                                    round(
                                                                                        len(
                                                                                            df.columns
                                                                                        )
                                                                                        / 2,
                                                                                        2,
                                                                                    )
                                                                                    if not df.empty
                                                                                    else ""
                                                                                ),
                                                                                "time_range": (
                                                                                    f"{round(df['x'].min(), 2)} - {round(df['x'].max(), 2)}"
                                                                                    if not df.empty
                                                                                    else ""
                                                                                ),
                                                                                "first_pd": (
                                                                                    round(
                                                                                        df[
                                                                                            "x"
                                                                                        ].min(),
                                                                                        2,
                                                                                    )
                                                                                    if not df.empty
                                                                                    else ""
                                                                                ),
                                                                            }
                                                                        ],
                                                                        style_table={
                                                                            "marginBottom": "20px"
                                                                        },
                                                                        style_cell={
                                                                            "textAlign": "center"
                                                                        },
                                                                        style_header={
                                                                            "fontWeight": "bold",
                                                                            "textAlign": "center",
                                                                        },
                                                                    ),
                                                                    dcc.Graph(
                                                                        id="scatter-plot",
                                                                        figure={
                                                                            "data": scatter_traces,
                                                                            "layout": create_scatter_layout(),
                                                                        },
                                                                        config={
                                                                            "displayModeBar": True,  # Enable toolbar
                                                                            "toImageButtonOptions": {
                                                                                "format": "png",  # Export as PNG
                                                                                "filename": "scatter_plot",
                                                                                "height": 600,
                                                                                "width": 1000,
                                                                                "scale": 1,
                                                                            },
                                                                        },
                                                                    ),
                                                                ],
                                                                style={
                                                                    "marginBottom": "20px",
                                                                    "borderRadius": "8px",  # Rounded corners
                                                                    "padding": "15px",
                                                                    "backgroundColor": "#fefefe",
                                                                    "border": "1px solid #ccc",
                                                                    "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
                                                                },
                                                            ),
                                                            # Scatter Plot for detailed view
                                                            html.Div(
                                                                [
                                                                    dcc.Graph(
                                                                        id="scatter-plot-selected",
                                                                        figure={
                                                                            "data": [],
                                                                            "layout": [],
                                                                        },
                                                                        config={
                                                                            "displayModeBar": True,
                                                                            "toImageButtonOptions": {
                                                                                "format": "png",
                                                                                "filename": "scatter_plot",
                                                                                "height": 600,
                                                                                "width": 1000,
                                                                                "scale": 1,
                                                                            },
                                                                        },
                                                                    )
                                                                ],
                                                                style={
                                                                    "marginBottom": "20px",
                                                                    "borderRadius": "8px",
                                                                    "padding": "15px",
                                                                    "backgroundColor": "#fefefe",
                                                                    "border": "1px solid #ccc",
                                                                    "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
                                                                },
                                                            ),
                                                        ],
                                                        style={
                                                            "width": "50%",
                                                            "display": "block",
                                                            "marginLeft": "2%",
                                                        },
                                                    ),
                                                    # Time Series and FFT Plots Section
                                                    html.Div(
                                                        [
                                                            dcc.Tabs(
                                                                [
                                                                    dcc.Tab(  # Temporal Signal Tab
                                                                        label="Temporal Signal",
                                                                        children=html.Div(
                                                                            [
                                                                                dcc.Graph(
                                                                                    id="temporal-tab-graph",
                                                                                    figure={
                                                                                        "data": [],
                                                                                        "layout": [],
                                                                                    },
                                                                                    config={
                                                                                        "displayModeBar": True,
                                                                                        "toImageButtonOptions": {
                                                                                            "format": "png",
                                                                                            "filename": "fft",
                                                                                            "height": 600,
                                                                                            "width": 1000,
                                                                                            "scale": 1,
                                                                                        },
                                                                                    },
                                                                                )
                                                                            ],
                                                                            style={
                                                                                "marginBottom": "20px",
                                                                                "borderRadius": "8px",
                                                                                "padding": "15px",
                                                                                "backgroundColor": "#fefefe",
                                                                                "border": "1px solid #ccc",
                                                                                "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
                                                                            },
                                                                        ),
                                                                    ),
                                                                    dcc.Tab(  # FFT Tab
                                                                        label="FFT",
                                                                        children=html.Div(
                                                                            [
                                                                                dcc.Graph(
                                                                                    id="fft-tab-graph",
                                                                                    figure={
                                                                                        "data": [],
                                                                                        "layout": [],
                                                                                    },
                                                                                    config={
                                                                                        "displayModeBar": True,
                                                                                        "toImageButtonOptions": {
                                                                                            "format": "png",
                                                                                            "filename": "fft",
                                                                                            "height": 600,
                                                                                            "width": 1000,
                                                                                            "scale": 1,
                                                                                        },
                                                                                    },
                                                                                )
                                                                            ],
                                                                            style={
                                                                                "marginBottom": "20px",
                                                                                "borderRadius": "8px",
                                                                                "padding": "15px",
                                                                                "backgroundColor": "#fefefe",
                                                                                "border": "1px solid #ccc",
                                                                                "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
                                                                            },
                                                                        ),
                                                                    ),
                                                                ]
                                                            ),
                                                            # Class Map
                                                            html.Div(
                                                                [
                                                                    # First Dropdown (generic options)
                                                                    dcc.Dropdown(
                                                                        id="dropdown-x-axis",
                                                                        options=classMapVariables,
                                                                        value="Vpp",
                                                                        placeholder="x-axis",
                                                                        style={
                                                                            "marginBottom": "10px"
                                                                        },
                                                                    ),
                                                                    # Second Dropdown (generic options)
                                                                    dcc.Dropdown(
                                                                        id="dropdown-y-axis",
                                                                        options=classMapVariables,
                                                                        value="Energy",
                                                                        placeholder="y-axis",
                                                                        style={
                                                                            "marginBottom": "20px"
                                                                        },
                                                                    ),
                                                                    dcc.Graph(
                                                                        id="class-map-graph",
                                                                        figure={
                                                                            "data": [],
                                                                            "layout": [],
                                                                        },
                                                                        config={
                                                                            "displayModeBar": True,
                                                                            "toImageButtonOptions": {
                                                                                "format": "png",
                                                                                "filename": "time_series",
                                                                                "height": 600,
                                                                                "width": 1000,
                                                                                "scale": 1,
                                                                            },
                                                                        },
                                                                    ),
                                                                ],
                                                                style={
                                                                    "marginBottom": "20px",
                                                                    "borderRadius": "8px",
                                                                    "padding": "15px",
                                                                    "backgroundColor": "#fefefe",
                                                                    "border": "1px solid #ccc",
                                                                    "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
                                                                },
                                                            ),
                                                            # Time & FFT Plot
                                                        ],
                                                        style={
                                                            "width": "50%",
                                                            "display": "block",
                                                            "marginLeft": "2%",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "fontFamily": "Roboto, sans-serif",
                                                    "flexDirection": "row",
                                                    "justifyContent": "space-between",
                                                },
                                            ),
                                        ],
                                    ),
                                    
                                    dcc.Tab(# Métricas y Gráficos Extra
                                        label="Plots & Metrics",
                                        children=[
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            dcc.Dropdown(
                                                                id="division-dropdown",
                                                                options=[
                                                                    {'label': str(i), 'value': str(i)} for i in range(1, 21)
                                                                ],
                                                                value='5',
                                                                clearable=False
                                                            ),
                                                            dcc.Graph(
                                                                id="extra-plot-1",
                                                                figure={"data": [], "layout": []},
                                                                config={
                                                                    "displayModeBar": True,
                                                                    "toImageButtonOptions": {
                                                                        "format": "png",
                                                                        "filename": "extra_plot_1",
                                                                        "height": 600,
                                                                        "width": 1000,
                                                                        "scale": 1,
                                                                    },
                                                                },
                                                            ),
                                                        ],
                                                        style={
                                                            "marginBottom": "20px",
                                                            "borderRadius": "8px",
                                                            "padding": "15px",
                                                            "backgroundColor": "#fefefe",
                                                            "border": "1px solid #ccc",
                                                            "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
                                                            "width": "70%",
                                                            "boxSizing": "border-box",
                                                            "marginLeft": "auto",
                                                            "marginRight": "auto",
                                                        },
                                                    ),
                                                    html.Div(
                                                        [
                                                            dcc.Graph(
                                                                id="extra-plot-2",
                                                                figure={"data": [], "layout": []},
                                                                config={
                                                                    "displayModeBar": True,
                                                                    "toImageButtonOptions": {
                                                                        "format": "png",
                                                                        "filename": "extra_plot_2",
                                                                        "height": 600,
                                                                        "width": 1000,
                                                                        "scale": 1,
                                                                    },
                                                                },
                                                            ),
                                                        ],
                                                        style={
                                                            "marginBottom": "20px",
                                                            "borderRadius": "8px",
                                                            "padding": "15px",
                                                            "backgroundColor": "#fefefe",
                                                            "border": "1px solid #ccc",
                                                            "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
                                                            "width": "70%",
                                                            "boxSizing": "border-box",
                                                            "marginLeft": "auto",
                                                            "marginRight": "auto",
                                                        },
                                                    ),
                                                ],
                                                style={
                                                    "display": "flex",
                                                    "flexDirection": "column",
                                                    "alignItems": "stretch",
                                                    "fontFamily": "Roboto, sans-serif",
                                                    "width": "100%",
                                                },
                                            )
                                        ],
                                    ),
                                    dcc.Tab(  # User Manual
                                        label="User Manual",
                                        children=[
                                            html.Div(
                                                [
                                                    dcc.Markdown(
                                                        USER_MANUAL_MD,
                                                        style={
                                                            "whiteSpace": "pre-line",
                                                            "padding": "20px",
                                                        },
                                                    )
                                                ],
                                                style={
                                                    "backgroundColor": "#fefefe",
                                                    "border": "1px solid #ccc",
                                                    "borderRadius": "8px",
                                                    "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
                                                    "margin": "30px",
                                                    "fontFamily": "Roboto, sans-serif",
                                                },
                                            )
                                        ],
                                    ),
                                ]
                            )
                        ]
                    ),
                ],
                style={"maxWidth": "1400px", "margin": "0 auto", "padding": "20px"},
            ),
        ]
    )

    # Callback for updating time-series and FFT plots
    @app.callback(
        [Output("temporal-tab-graph", "figure"), Output("fft-tab-graph", "figure")],
        [
            Input("scatter-plot", "clickData"),
            Input("scatter-plot", "selectedData"),
            Input("dropdown-x-axis", "value"),
            Input("dropdown-y-axis", "value"),
            Input("class-map-graph", "clickData"),
            Input("class-map-graph", "selectedData"),
        ],
    )
    def update_temporal_fft_plots(
        clickDataScatter,
        selectedDataScatter,
        x_axis,
        y_axis,
        clickDataClass,
        selectedDataClass,
    ):
        ctx = dash.callback_context  # Get trigger context
        temporal_fig, fft_fig = [], []

        try:
            if not ctx.triggered:
                # Default selection logic
                selected_id = df["id"].iloc[0]
                selected_data = df[df["id"] == selected_id].iloc[0]
                temporal_fig, fft_fig = plot_time_fft_single(selected_data)
            else:
                triggered_id = ctx.triggered[0]["prop_id"]

                if triggered_id == "scatter-plot.clickData" and clickDataScatter:
                    # Handle click interaction
                    selected_id = clickDataScatter["points"][0]["customdata"][3]
                    selected_data = df[df["id"] == selected_id].iloc[0]
                    temporal_fig, fft_fig = plot_time_fft_single(selected_data)

                elif triggered_id == "scatter-plot.selectedData" and selectedDataScatter:
                    # Handle selection box interaction on scatter plot
                    selected_ids = [
                        pt["customdata"][3] for pt in selectedDataScatter["points"]
                    ]
                    if len(selected_ids) == 1:
                        selected_data = df[df["id"] == selected_ids[0]].iloc[0]
                        temporal_fig, fft_fig = plot_time_fft_single(selected_data)
                    elif len(selected_ids) > 1:
                        selected_data = df[df["id"].isin(selected_ids)]
                        temporal_fig, fft_fig = plot_time_fft_multiple(
                            selected_data.to_dict("records")
                        )
                    else:
                        selected_id = df["id"].iloc[0]
                        selected_data = df[df["id"] == selected_id].iloc[0]
                        temporal_fig, fft_fig = plot_time_fft_single(selected_data)

                elif triggered_id == "class-map-graph.clickData" and clickDataClass:
                    # Handle click interaction on class map
                    selected_id = clickDataClass["points"][0]["customdata"][0]
                    selected_data = df[df["id"] == selected_id].iloc[0]
                    temporal_fig, fft_fig = plot_time_fft_single(selected_data)

                elif triggered_id == "class-map-graph.selectedData" and selectedDataClass:
                    # Handle selection box interaction on class map
                    selected_ids = [
                        pt["customdata"][0] for pt in selectedDataClass["points"]
                    ]
                    if len(selected_ids) == 1:
                        selected_data = df[df["id"] == selected_ids[0]].iloc[0]
                        temporal_fig, fft_fig = plot_time_fft_single(selected_data)
                    elif len(selected_ids) > 1:
                        selected_data = df[df["id"].isin(selected_ids)]
                        temporal_fig, fft_fig = plot_time_fft_multiple(
                            selected_data.to_dict("records")
                        )
                    else:
                        selected_id = df["id"].iloc[0]
                        selected_data = df[df["id"] == selected_id].iloc[0]
                        temporal_fig, fft_fig = plot_time_fft_single(selected_data)

                else:
                    # Default fallback
                    selected_id = df["id"].iloc[0]
                    selected_data = df[df["id"] == selected_id].iloc[0]
                    temporal_fig, fft_fig = plot_time_fft_single(selected_data)

            # Asegura que siempre se retorna una tupla de dos elementos (figuras)
            if not isinstance(temporal_fig, (list, dict)):
                temporal_fig = []
            if not isinstance(fft_fig, (list, dict)):
                fft_fig = []
            return temporal_fig, fft_fig
        except Exception as e:
            print(f"Error in update_temporal_fft_plots: {e}")
            # Devuelve figuras vacías para evitar errores en Dash
            return {}, {}

    @app.callback(
        Output("extra-plot-1", "figure"),
        [Input("class-map-graph", "selectedData"), Input("division-dropdown", "value")],
    )
    def update_extra_plot_1(selectedData, num_bins):
        num_bins = int(num_bins)  # Convert to integer
        # Si no hay selección, usar todos los datos
        if selectedData and "points" in selectedData and selectedData["points"]:
            selected_ids = [pt["customdata"][0] for pt in selectedData["points"]]
            filtered_df = df[df["id"].isin(selected_ids)]
        else:
            filtered_df = df

        # Verifica que la columna sea 'Vpp'
        y_col = "y" if "y" in filtered_df.columns else filtered_df.columns[0]
        y = np.array(filtered_df[y_col].values)
        y_max = np.max(np.abs(y)) if y.size > 0 else 0
        if y.size > 0 and y_max != 0:
            y_norm = y / y_max
        else:
            y_norm = y
        time_dps = "x" if "x" in filtered_df.columns else None

        # Si no existe la columna 'impulse', usar el índice como número de impulso
        if time_dps:
            x = np.array(filtered_df[time_dps].values)
        else:
            x = np.arange(len(filtered_df))

        # Definir el número de bins (puedes hacerlo configurable)

        # Calcular los límites de los bins
        if x.size > 0:
            x_min, x_max = np.min(x), np.max(x)
            bins = np.linspace(x_min, x_max, num_bins + 1)
        else:
            bins = np.linspace(0, 1, num_bins + 1)

        # Inicializar listas para las métricas por bin
        bin_centers = []
        vpp_means = []
        energy_means = []
        num_signals = []

        # Para cada bin, calcular métricas
        for i in range(num_bins):
            bin_mask = (x >= bins[i]) & (x < bins[i + 1])
            bin_df = filtered_df[bin_mask]
            if not bin_df.empty:
                bin_centers.append((bins[i] + bins[i + 1]) / 2)
                vpp_means.append(bin_df["Vpp"].mean() * 1e3)  # mV
                energy_means.append(bin_df["Energy"].mean())  # mV^2
                num_signals.append(len(bin_df))
            else:
                bin_centers.append((bins[i] + bins[i + 1]) / 2)
                vpp_means.append(0)
                energy_means.append(0)
                num_signals.append(0)

        # Convertir a np.array para graficar
        bin_centers = np.array(bin_centers)
        vpp_means = np.array(vpp_means)
        energy_means = np.array(energy_means)
        num_signals = np.array(num_signals)

        # Normalizar para graficar si no son todos ceros y obtener máximos
        vpp_max = np.max(vpp_means) if np.any(vpp_means) else 0
        energy_max = np.max(energy_means) if np.any(energy_means) else 0
        num_signals_max = np.max(num_signals) if np.any(num_signals) else 0

        vpp_norm = vpp_means / vpp_max if vpp_max else vpp_means
        energy_norm = energy_means / energy_max if energy_max else energy_means
        num_signals_norm = num_signals / num_signals_max if num_signals_max else num_signals

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=bin_centers,
            y=vpp_norm,
            mode="lines+markers",
            marker=dict(color="#185a9d", size=8),
            line=dict(color="#185a9d", width=2),
            name=f"Mean Vpp (mV) (max={vpp_max:.2f})" if vpp_max else "Mean Vpp (mV)"
        ))
        fig.add_trace(go.Scatter(
            x=bin_centers,
            y=energy_norm,
            mode="lines+markers",
            marker=dict(color="#b71c1c", size=8),
            line=dict(color="#b71c1c", width=2),
            name=f"Mean Energy (mV²) (max={energy_max:.2f})" if energy_max else "Mean Energy (mV²)"
        ))
        fig.add_trace(go.Scatter(
            x=bin_centers,
            y=num_signals_norm,
            mode='lines+markers',
            marker=dict(color="green", size=8),
            line=dict(color="green", width=2),
            name=f"Num. of Discharges (max={num_signals_max})" if num_signals_max else "Num. of Discharges",
        ))
        fig.add_trace(go.Scatter(
            x=x,
            y=y_norm,
            mode='markers',
            marker=dict(color="black", size=8),
            line=dict(color="black", width=2),
            name=f"Signal Data (max={y_max:.2f})" if y_max else "Signal Data",
        ))
        # Añadir eje secundario para el número de descargas
        fig.update_layout(
            yaxis=dict(title="Normalized Metrics"),
            title="",
            xaxis_title="Time (us)",
            template="simple_white",
            margin=dict(l=40, r=20, t=50, b=40),
            height=400
        )
        return fig
    
    @app.callback(
        [Output("class-map-graph", "figure")],
        [
            Input("scatter-plot", "clickData"),
            Input("scatter-plot", "selectedData"),
            Input("dropdown-x-axis", "value"),
            Input("dropdown-y-axis", "value"),
        ],
    )
    def update_class_map_graph(clickData, selectedData, x_axis, y_axis):
        ctx = dash.callback_context  # Get trigger context

        if not ctx.triggered:
            # Default selection logic
            selected_id = df["id"].iloc[0]
            selected_data = df[df["id"] == selected_id]
            class_map_fig, _ = plot_class_map(selected_data, x_axis, y_axis)
        else:
            triggered_id = ctx.triggered[0]["prop_id"]

            if "clickData" in triggered_id and clickData:
                selected_id = clickData["points"][0]["customdata"][3]
                selected_data = df[df["id"] == selected_id]
                class_map_fig, _ = plot_class_map(selected_data, x_axis, y_axis)
            elif "selectedData" in triggered_id and selectedData:
                selected_ids = [pt["customdata"][3] for pt in selectedData["points"]]
                selected_data = df[df["id"].isin(selected_ids)]
                class_map_fig, _ = plot_class_map(selected_data, x_axis, y_axis)
            elif "dropdown-x-axis" in triggered_id or "dropdown-y-axis" in triggered_id:
                if selectedData and "points" in selectedData and selectedData["points"]:
                    selected_ids = [
                        pt["customdata"][3] for pt in selectedData["points"]
                    ]
                    selected_data = df[df["id"].isin(selected_ids)]
                    class_map_fig, _ = plot_class_map(selected_data, x_axis, y_axis)
                elif clickData and "points" in clickData and clickData["points"]:
                    selected_id = clickData["points"][0]["customdata"][3]
                    selected_data = df[df["id"] == selected_id]
                    class_map_fig, _ = plot_class_map(selected_data, x_axis, y_axis)
                else:
                    selected_id = df["id"].iloc[0]
                    selected_data = df[df["id"] == selected_id]
                    class_map_fig, _ = plot_class_map(selected_data, x_axis, y_axis)
            else:
                selected_id = df["id"].iloc[0]
                selected_data = df[df["id"] == selected_id]
                class_map_fig, _ = plot_class_map(selected_data, x_axis, y_axis)

        return [class_map_fig]

    @app.callback(
        Output("scatter-plot-selected", "figure"),
        Input("class-map-graph", "clickData"),
        Input("class-map-graph", "selectedData"),
        State("scatter-plot-selected", "relayoutData"),
    )
    def update_scatter_plot_selected(clickData, selectedData, relayoutData):
        ctx = dash.callback_context  # Get trigger context
        selected_PRPD_fig = [], []

        # Handle zoom or relayout data
        if (
            relayoutData
            and "xaxis.range[0]" in relayoutData
            and "xaxis.range[1]" in relayoutData
            and "yaxis.range[0]" in relayoutData
            and "yaxis.range[1]" in relayoutData
        ):
            stored_layout = go.Layout(
                title=dict(text="Selected Signals from Class. Map", font=dict(size=14)),
                xaxis=dict(
                    title="Time (us)",
                    range=[
                        relayoutData["xaxis.range[0]"],
                        relayoutData["xaxis.range[1]"],
                    ],
                ),
                yaxis=dict(
                    title="Voltage (V)",
                    range=[
                        relayoutData["yaxis.range[0]"],
                        relayoutData["yaxis.range[1]"],
                    ],
                ),
                uirevision=True,
            )
        else:
            # Default layout
            stored_layout = go.Layout(
                title=dict(text="Selected Signals from Class. Map", font=dict(size=14)),
                xaxis=dict(title="Time (us)"),
                yaxis=dict(title="Voltage (V)"),
                uirevision=True,
            )

        if not ctx.triggered:
            # Default selection logic
            selected_id = df["id"].iloc[0]
            selected_data = df[df["id"] == selected_id].iloc[0]
            selected_PRPD_fig = plot_selected_PRPD_single(
                selected_data, stored_layout, time, impulse
            )
        else:
            triggered_id = ctx.triggered[0]["prop_id"]

            if "clickData" in triggered_id and clickData:
                # Handle click interaction
                selected_id = clickData["points"][0]["customdata"][0]
                selected_data = df[df["id"] == selected_id].iloc[0]
                selected_PRPD_fig = plot_selected_PRPD_single(
                    selected_data, stored_layout, time, impulse
                )

            elif "selectedData" in triggered_id and selectedData:
                # Handle selection box interaction
                selected_ids = [pt["customdata"][0] for pt in selectedData["points"]]
                selected_data = df[df["id"].isin(selected_ids)]
                selected_PRPD_fig = plot_selected_PRPD_multiple(
                    selected_data, stored_layout, time, impulse
                )
            else:
                # Default fallback
                selected_id = df["id"].iloc[0]
                selected_data = df[df["id"] == selected_id].iloc[0]
                selected_PRPD_fig = plot_selected_PRPD_single(
                    selected_data, stored_layout, time, impulse
                )

        return selected_PRPD_fig

    @app.callback(
        [
            Output("download-data-1", "data"),
            Output("download-data-2", "data"),
            Output("download-data-3", "data"),
            Output("download-data-4", "data"),
        ],
        [
            Input("button-1", "n_clicks"),
            Input("button-2", "n_clicks"),
            Input("button-3", "n_clicks"),
            Input("button-4", "n_clicks"),
        ],
        [
            State("scatter-plot", "selectedData"),
            State("class-map-graph", "selectedData"),
        ],
    )
    def download_selected_data(
        btn1, btn2, btn3, btn4, scatter_selected, upper_selected
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return [None, None, None, None]
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Download Selected TRPD Temporal Signals
        if button_id == "button-1" and btn1:
            if scatter_selected:
                ids = [pt["customdata"][3] for pt in scatter_selected["points"]]
                filtered_df = df[df["id"].isin(ids)]
                outputDF = build_export_dataframe(filtered_df, "signal")
                return [
                    dcc.send_data_frame(
                        outputDF.to_csv, "TRPD_graph_selected_data.csv", index=False
                    ),
                    None,
                    None,
                    None,
                ]
            return [None, None, None, None]

        # Download Selected Class. Map Temporal Signals
        if button_id == "button-2" and btn2:
            if upper_selected:
                ids = [pt["customdata"][0] for pt in upper_selected["points"]]
                filtered_df = df[df["id"].isin(ids)]
                outputDF = build_export_dataframe(filtered_df, "signal")
                return [
                    None,
                    dcc.send_data_frame(
                        outputDF.to_csv, "TF_Map_selected_data.csv", index=False
                    ),
                    None,
                    None,
                ]
            return [None, None, None, None]

        # Download Selected TRPD FFT
        if button_id == "button-3" and btn3:
            if scatter_selected:
                ids = [pt["customdata"][3] for pt in scatter_selected["points"]]
                filtered_df = df[df["id"].isin(ids)]
                outputDF = build_export_dataframe(filtered_df, "fft_values")
                return [
                    None,
                    None,
                    dcc.send_data_frame(
                        outputDF.to_csv, "TRPD_graph_selected_fft.csv", index=False
                    ),
                    None,
                ]
            return [None, None, None, None]

        # Download Selected Class. Map FFT
        if button_id == "button-4" and btn4:
            if upper_selected:
                ids = [pt["customdata"][0] for pt in upper_selected["points"]]
                filtered_df = df[df["id"].isin(ids)]
                outputDF = build_export_dataframe(filtered_df, "fft_values")
                return [
                    None,
                    None,
                    None,
                    dcc.send_data_frame(
                        outputDF.to_csv, "TF_Map_selected_fft.csv", index=False
                    ),
                ]
            return [None, None, None, None]

        return [None, None, None, None]

    @app.callback(
        Output("selected-values-metrics-table", "data"),
        [
            Input("scatter-plot", "selectedData"),
            Input("scatter-plot", "clickData"),
            Input("class-map-graph", "selectedData"),
            Input("class-map-graph", "clickData"),
        ],
    )
    def update_table(scatter_selected, scatter_click, upper_selected, upper_click):
        ctx = dash.callback_context

        # Default: use all data
        filtered_df = df

        if ctx.triggered:
            triggered_id = ctx.triggered[0]["prop_id"]
            if (
                "class-map-graph.selectedData" in triggered_id
                and upper_selected
                and "points" in upper_selected
            ):
                selected_ids = [pt["customdata"][0] for pt in upper_selected["points"]]
                filtered_df = df[df["id"].isin(selected_ids)]
            elif (
                "class-map-graph.clickData" in triggered_id
                and upper_click
                and "points" in upper_click
            ):
                selected_id = upper_click["points"][0]["customdata"][0]
                filtered_df = df[df["id"] == selected_id]
            elif (
                "scatter-plot.selectedData" in triggered_id
                and scatter_selected
                and "points" in scatter_selected
            ):
                selected_ids = [
                    pt["customdata"][3] for pt in scatter_selected["points"]
                ]
                filtered_df = df[df["id"].isin(selected_ids)]
            elif (
                "scatter-plot.clickData" in triggered_id
                and scatter_click
                and "points" in scatter_click
            ):
                selected_id = scatter_click["points"][0]["customdata"][3]
                filtered_df = df[df["id"] == selected_id]

        # Calculate metrics
        if not filtered_df.empty:
            vpp = round(filtered_df["Vpp"].mean() * 1e3, 2)
            energy = round(filtered_df["Energy"].mean() * 1e3, 2)
            qapp = round(filtered_df["Qapp"].mean(), 2)
            avg_time = round(filtered_df["x"].mean(), 2)
            num_signals = int(filtered_df.shape[0])
            t_range = round(max(filtered_df["x"]) - min(filtered_df["x"]), 2)
            first_pd = round(min(filtered_df["x"]), 2)
        else:
            vpp = energy = qapp = avg_time = num_signals = t_range = first_pd = ""

        new_data = [
            {
                "Vpp": vpp,
                "Energy": energy,
                "Qapp": qapp,
                "t_mean": avg_time,
                "Npd": num_signals,
                "time_range": t_range,
                "first_pd": first_pd,
            }
        ]
        return new_data

    print(f"Dash app is running on: http://{host}:{port}/")  # Print app URL
    app.run(
        debug=False, host=host, port=port, use_reloader=False
    )  # Start the server without debug mode
