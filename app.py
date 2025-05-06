from main_data import df, scatter_traces

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State


# from data_processing import process_data
from plotting import (
    create_scatter_layout,
    plot_time_fft_multiple,
    plot_time_fft_single,
    plot_selected_PRPD_single,
    plot_selected_PRPD_multiple,
)
import plotly.graph_objects as go


# Inicialización de la aplicación
app = dash.Dash(__name__, title="TRPD Visualizer")


# Layout de la aplicación
app.layout = html.Div(
    [
        dcc.Store(id="scatter-selected-zoom-data"),
        html.Div(
            [  # Todo el contenido de la app
                html.Div(  # Títulos
                    [
                        html.Div(
                            [
                                html.H1(
                                    "TRPD Interactive Interface",
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
                                            "V0.1 | LIDAT",
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
                        "background": "linear-gradient(90deg, #03396c, #6497b1)",
                        "borderRadius": "10px 10px 0 0",
                        "marginBottom": "20px",
                        "height": "90px",
                        "boxShadow": "0 4px 12px rgba(0,0,0,0.2)",
                        "position": "relative",
                    },
                ),
                html.Div(  # Gráficos
                    [  # Tabs
                        dcc.Tabs(
                            [  # Tabs
                                dcc.Tab(  # PD Data Analyzer
                                    label="PD Data Analyzer",
                                    children=[
                                        html.Div(
                                            [  # Todos los gráficos
                                                html.Div(  # Scatter Plot
                                                    [
                                                        html.Div(  # Scatter Plot Principal
                                                            [
                                                                dcc.Graph(
                                                                    id="scatter-plot",
                                                                    figure={
                                                                        "data": scatter_traces,
                                                                        "layout": create_scatter_layout(),
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
                                                        html.Div(  # Scatter Plot Detalle
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
                                                        "display": "block",  # Cambiado de inline-block a block para independencia
                                                        "marginLeft": "2%",  # Espacio para separación
                                                    },
                                                ),
                                                html.Div(  # Time Series and FFT Plots
                                                    [
                                                        html.Div(  # Time Plot
                                                            [
                                                                dcc.Graph(
                                                                    id="time-series",
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
                                                        html.Div(  # FFT Plot
                                                            [
                                                                dcc.Graph(
                                                                    id="fft-plot",
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
                                                    ],
                                                    style={
                                                        "width": "50%",
                                                        "display": "block",  # Cambiado de inline-block a block para independencia
                                                        "marginLeft": "2%",  # Espacio para separación
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
                            ]
                        )
                    ]
                ),
            ],
            style={"maxWidth": "1400px", "margin": "0 auto", "padding": "20px"},
        ),
    ]
)


@app.callback(
    [Output("time-series", "figure"), Output("fft-plot", "figure")],
    [Input("scatter-plot", "clickData"), Input("scatter-plot", "selectedData")],
)
def update_plots(clickData, selectedData):
    ctx = dash.callback_context
    selected_PRPD_fig, fft_fig = [], []

    if not ctx.triggered:
        selected_id = df["id"].iloc[0]
        selected_data = df[df["id"] == selected_id].iloc[0]
        selected_PRPD_fig, fft_fig = plot_time_fft_single(selected_data)
    else:
        triggered_id = ctx.triggered[0]["prop_id"]

        if "clickData" in triggered_id and clickData:
            selected_id = clickData["points"][0]["customdata"][3]
            selected_data = df[df["id"] == selected_id].iloc[0]
            selected_PRPD_fig, fft_fig = plot_time_fft_single(selected_data)

        elif "selectedData" in triggered_id and selectedData:
            selected_ids = [pt["customdata"][3] for pt in selectedData["points"]]
            print(selected_ids)
            selected_data = df[df["id"].isin(selected_ids)]
            selected_PRPD_fig, fft_fig = plot_time_fft_multiple(selected_data)

        else:
            selected_id = df["id"].iloc[0]
            selected_data = df[df["id"] == selected_id].iloc[0]
            selected_PRPD_fig, fft_fig = plot_time_fft_single(selected_data)

    return selected_PRPD_fig, fft_fig


@app.callback(
    Output("scatter-plot-selected", "figure"),
    Input("time-series", "clickData"),
    Input("time-series", "selectedData"),
    State("scatter-plot-selected", "relayoutData"),
)
def update_scatter_plot_selected(clickData, selectedData, relayoutData):
    ctx = dash.callback_context
    selected_PRPD_fig = [], []

    if relayoutData and "xaxis.range[0]" in relayoutData:
        stored_layout = go.Layout(
            title=f"PRPD",
            titlefont=dict(size=14),
            xaxis=dict(title="Time (us)"),
            yaxis=dict(title="Voltage (V)"),
            xaxis_range=[
                relayoutData["xaxis.range[0]"],
                relayoutData["xaxis.range[1]"],
            ],
            yaxis_range=[
                relayoutData["yaxis.range[0]"],
                relayoutData["yaxis.range[1]"],
            ],
            uirevision=True,
        )

    else:
        stored_layout = go.Layout(
            title=f"PRPD",
            titlefont=dict(size=14),
            xaxis=dict(title="Time (us)"),
            yaxis=dict(title="Voltage (V)"),
            uirevision=True,
        )

    if not ctx.triggered:
        selected_id = df["id"].iloc[0]
        selected_data = df[df["id"] == selected_id].iloc[0]
        selected_PRPD_fig = plot_selected_PRPD_single(selected_data, stored_layout)
    else:
        triggered_id = ctx.triggered[0]["prop_id"]

        if "clickData" in triggered_id and clickData:
            selected_id = clickData["points"][0]["customdata"][0]
            selected_data = df[df["id"] == selected_id].iloc[0]
            selected_PRPD_fig = plot_selected_PRPD_single(selected_data, stored_layout)

        elif "selectedData" in triggered_id and selectedData:
            selected_ids = [pt["customdata"][0] for pt in selectedData["points"]]
            selected_data = df[df["id"].isin(selected_ids)]
            selected_PRPD_fig = plot_selected_PRPD_multiple(
                selected_data, stored_layout
            )

        else:
            selected_id = df["id"].iloc[0]
            selected_data = df[df["id"] == selected_id].iloc[0]
            selected_PRPD_fig = plot_selected_PRPD_single(selected_data, stored_layout)

    return selected_PRPD_fig


if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8002
    print(f"Dash app is running on: http://{host}:{port}/")
    app.run(debug=False, host=host, port=port)
