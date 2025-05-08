# Importing required modules and functions
# from main_data import df, scatter_traces  # Custom data and traces for plotting

import dash
from dash import dcc, html  # Dash components for creating the layout
from dash.dependencies import (
    Input,
    Output,
    State,
)  # For handling callbacks and interactivity

# Commented out import for data processing, likely unused
# from data_processing import process_data
from plotting import (  # Custom plotting functions imported from the 'plotting' module
    create_scatter_layout,
    plot_time_fft_multiple,
    plot_time_fft_single,
    plot_selected_PRPD_single,
    plot_selected_PRPD_multiple,
)
import plotly.graph_objects as go  # Used for detailed graph customization


def create_dash_app(df, scatter_traces, time, impulse):

    # Initialization of the Dash application
    app = dash.Dash(__name__, title="TRPD Visualizer")

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
                            "background": "linear-gradient(90deg, #03396c, #6497b1)",  # Gradient background
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
                                    dcc.Tab(
                                        label="PD Data Analyzer",
                                        children=[
                                            html.Div(
                                                [
                                                    html.Button(
                                                        "Download Selected Data TRPD",
                                                        id="button-1",
                                                        style={
                                                            "margin-left": "20px",
                                                            "cursor": "pointer",
                                                        },
                                                    ),
                                                    dcc.Download(id="download-data-1"),
                                                    html.Button(
                                                        "Download Selected Data Classification Map",
                                                        id="button-2",
                                                        style={
                                                            "margin-left": "20px",
                                                            "cursor": "pointer",
                                                        },
                                                    ),
                                                    dcc.Download(id="download-data-2"),
                                                    html.Button(
                                                        "Button 3",
                                                        id="button-3",
                                                        style={
                                                            "margin-left": "20px",
                                                            "cursor": "pointer",
                                                        },
                                                    ),
                                                    dcc.Download(id="download-data-3"),
                                                ],
                                                style={
                                                    "marginBottom": "20px",
                                                    "borderRadius": "8px",
                                                    "padding": "15px",
                                                    "backgroundColor": "#fefefe",
                                                    "border": "1px solid #ccc",
                                                    "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
                                                    "textAlign": "center",
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
                                                                    )
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
                                                            # Time Series Plot
                                                            html.Div(
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
                                                            # FFT Plot
                                                            html.Div(
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
                                        label="User Manual",
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
        [Output("time-series", "figure"), Output("fft-plot", "figure")],
        [Input("scatter-plot", "clickData"), Input("scatter-plot", "selectedData")],
    )
    def update_plots(clickData, selectedData):
        ctx = dash.callback_context  # Get trigger context
        selected_PRPD_fig, fft_fig = [], []

        if not ctx.triggered:
            # Default selection logic
            selected_id = df["id"].iloc[0]
            selected_data = df[df["id"] == selected_id].iloc[0]
            selected_PRPD_fig, fft_fig = plot_time_fft_single(selected_data)
        else:
            triggered_id = ctx.triggered[0]["prop_id"]

            if "clickData" in triggered_id and clickData:
                # Handle click interaction
                selected_id = clickData["points"][0]["customdata"][3]
                selected_data = df[df["id"] == selected_id].iloc[0]
                selected_PRPD_fig, fft_fig = plot_time_fft_single(selected_data)

            elif "selectedData" in triggered_id and selectedData:
                # Handle selection box interaction
                selected_ids = [pt["customdata"][3] for pt in selectedData["points"]]
                selected_data = df[df["id"].isin(selected_ids)]
                selected_PRPD_fig, fft_fig = plot_time_fft_multiple(selected_data)

            else:
                # Default fallback
                selected_id = df["id"].iloc[0]
                selected_data = df[df["id"] == selected_id].iloc[0]
                selected_PRPD_fig, fft_fig = plot_time_fft_single(selected_data)

        return selected_PRPD_fig, fft_fig

    # Callback for updating the scatter plot based on time-series interaction
    @app.callback(
        Output("scatter-plot-selected", "figure"),
        Input("time-series", "clickData"),
        Input("time-series", "selectedData"),
        State("scatter-plot-selected", "relayoutData"),
    )
    def update_scatter_plot_selected(clickData, selectedData, relayoutData):
        ctx = dash.callback_context  # Get trigger context
        selected_PRPD_fig = [], []

        # Handle zoom or relayout data
        if relayoutData and "xaxis.range[0]" in relayoutData:
            stored_layout = go.Layout(
                title=dict(text="PRPD", font=dict(size=14)),
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
            # Default layout
            stored_layout = go.Layout(
                title=dict(text="PRPD", font=dict(size=14)),
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
        Output("download-data-1", "data"),
        Input("button-1", "n_clicks"),
        State("scatter-plot", "selectedData"),
    )
    def download_selected_data_TRPD(button1, scatterSelectedData):
        if button1:
            if scatterSelectedData:
                scatterSelectedIds = [
                    point["customdata"][3] for point in scatterSelectedData["points"]
                ]
                filtered_df = df[df["id"].isin(scatterSelectedIds)]
                return dcc.send_data_frame(filtered_df.to_csv, "selected_data.csv")
            else:
                return None

    # if __name__ == "__main__":
    host = "127.0.0.1"  # Host address for the app
    port = 8002  # Port for the app
    print(f"Dash app is running on: http://{host}:{port}/")  # Print app URL
    app.run(
        debug=False, host=host, port=port, use_reloader=False
    )  # Start the server without debug mode
