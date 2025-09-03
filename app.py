import dash
import signal
import os
from dash import dcc, html
import dash_bootstrap_components as dbc  # NUEVO: Bootstrap components

# from data_processing import process_data
from plotting import (  # Custom plotting functions imported from the 'plotting' module
    create_scatter_layout,
)
from UserManual import USER_MANUAL_MD  # Importa el manual de usuario

from callbacks import register_callbacks

dash_server_process = None

classMapVariables = [
    {"label": "Peak to Peak Voltage", "value": "Vpp"},
    {"label": "Energy", "value": "Energy"},
    {"label": "Apparent Charge", "value": "Qapp"},
    {"label": "Equivalent Time", "value": "T2"},
    {"label": "Equivalent Frequency", "value": "W2"},
    {"label": "Time of Occurrence", "value": "x"},
]


def create_dash_app(df, scatter_traces, time, impulse, host, port, folder):

    global dash_server_process

    if dash_server_process:
        os.kill(dash_server_process.pid, signal.SIGTERM)
        dash_server_process = None
        time.sleep(1)  # Espera a que el puerto se libere

    # Initialization of the Dash application
    app = dash.Dash(
        __name__,
        title="TRPD App",
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
                                        "Transient - Resolved Partial Discharge Analyzer App",
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
                                                "PD Classification Tool",
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
                                            "right": "20px",  # Cambiado de left a right
                                            "bottom": "10px",
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
                    # html.Div([html.(id="button-1"), html.Button(id="button-2")]),
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
                                                dbc.Row(
                                                    dcc.Markdown(
                                                        folder
                                                    )
                                                ),
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
                                                    # Botón negro, estilo similar a los otros
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    dbc.Button(
                                                                        "Download ID Class. Map",
                                                                        id="button-0",
                                                                        color="dark",
                                                                        outline=True,
                                                                        size="sm",
                                                                        className="mb-1 me-1",
                                                                        style={
                                                                            "width": "100%",
                                                                            "borderRadius": "20px",
                                                                            "backgroundColor": "#e3e3e3",
                                                                            "color": "#222",
                                                                            "border": "1.5px solid #222",
                                                                            "fontWeight": "500",
                                                                            "fontFamily": "Roboto, monospace",
                                                                            "boxShadow": "0 2px 8px rgba(34,34,34,0.07)",
                                                                            "padding": "2px 8px",
                                                                            "fontSize": "13px",
                                                                        },
                                                                    ),
                                                                    dcc.Download(
                                                                        id="download-data-0"
                                                                    ),
                                                                ],
                                                                width="auto",
                                                            ),
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
                                    dcc.Tab(
                                        label="Voltage-Dependent Metrics",
                                        children=[
                                            html.Div(
                                                [
                                                    html.Div(
                                                        dcc.Slider(
                                                            id="voltage-slider-1",
                                                            min=0,
                                                            max=1,
                                                            step=0.01,
                                                            value=0.4,
                                                            marks={i: f"{i:.2f}" for i in [0, 0.5, 1, 1.5, 2]},
                                                            tooltip={"placement": "bottom", "always_visible": False},
                                                            updatemode="mouseup",  # Solo ejecuta el callback al soltar el slider
                                                            included=True,
                                                        ),
                                                        style={"marginBottom": "20px"},
                                                    ),
                                                    dbc.Button(
                                                        "Refresh",
                                                        id="refresh-button-multi-voltage",
                                                    ),
                                                    dcc.Graph(
                                                        id="voltage-dep-1",
                                                        figure={
                                                            "data": [],
                                                            "layout": [],
                                                        },
                                                        config={
                                                            "displayModeBar": True,
                                                            "toImageButtonOptions": {
                                                                "format": "png",
                                                                "filename": "voltage-dep-1",
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
                                                [                                                    html.Div(
                                                        dcc.Slider(
                                                            id="voltage-slider-2",
                                                            min=0,
                                                            max=1,
                                                            step=0.001,
                                                            value=0.005,
                                                            marks={i: f"{i:.2f}" for i in [0, 0.5, 1, 1.5, 2]},
                                                            tooltip={"placement": "bottom", "always_visible": False},
                                                            updatemode="mouseup",  # Solo ejecuta el callback al soltar el slider
                                                            included=True,
                                                        ),
                                                        style={"marginBottom": "20px"},
                                                    ),
                                                    dcc.Graph(
                                                        id="voltage-dep-2",
                                                        figure={
                                                            "data": [],
                                                            "layout": [],
                                                        },
                                                        config={
                                                            "displayModeBar": True,
                                                            "toImageButtonOptions": {
                                                                "format": "png",
                                                                "filename": "voltage-dep-2",
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
                                    ),
                                    dcc.Tab(  # Métricas y Gráficos Extra
                                        label="Time-Dependent Metrics",
                                        children=[
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [

                                                            dbc.Button(
                                                                "Refresh",
                                                                id="refresh-button-single-voltage",
                                                            ),
                                                            dcc.Dropdown(
                                                                id="division-dropdown",
                                                                options=[
                                                                    {
                                                                        "label": str(i),
                                                                        "value": str(i),
                                                                    }
                                                                    for i in range(
                                                                        1, 21
                                                                    )
                                                                ],
                                                                value="5",
                                                                clearable=False,
                                                            ),
                                                            dcc.Graph(
                                                                id="extra-plot-1",
                                                                figure={
                                                                    "data": [],
                                                                    "layout": [],
                                                                },
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
                                                                figure={
                                                                    "data": [],
                                                                    "layout": [],
                                                                },
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
                                                    html.Div(
                                                        [
                                                            dcc.Graph(
                                                                id="extra-plot-3",
                                                                figure={
                                                                    "data": [],
                                                                    "layout": [],
                                                                },
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
    register_callbacks(app, df, time, impulse, folder)

    print(f"Dash app is running on: http://{host}:{port}/")  # Print app URL
    app.run(
        debug=False, host=host, port=port, use_reloader=False
    )  # Start the server without debug mode
