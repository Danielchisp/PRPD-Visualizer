import dash
import signal
import pandas as pd
import numpy as np
import os
from dash import dcc, html  # Dash components for creating the layout
from dash.dependencies import (
    Input,
    Output,
    State,
)  # For handling callbacks and interactivity

# from data_processing import process_data
from plotting import (  # Custom plotting functions imported from the 'plotting' module
    create_scatter_layout,
    plot_time_fft_multiple,
    plot_time_fft_single,
    plot_selected_PRPD_single,
    plot_selected_PRPD_multiple,
)
import plotly.graph_objects as go  # Used for detailed graph customization

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
                                        "TRPD Analysys Interface",
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
                                    dcc.Tab(  # PD Data Analyzer
                                        label="PD Data Analyzer",
                                        children=[
                                            html.Div( # Buttons for downloading data
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
                                                                    # DataTable with summary statistics
                                                                    dash.dash_table.DataTable(
                                                                        id='selected-values-metrics-table',
                                                                        columns=[
                                                                            {"name": "Vpp (mV)", "id": "Vpp"},
                                                                            {"name": "Energy (mV^2)", "id": "Energy"},
                                                                            {"name": "Qapp (-)", "id": "Qapp"},
                                                                            {"name": "Average\nTime (us)", "id": "Average Time"},
                                                                            {"name": "Number of Signals", "id": "Number of Signals"},
                                                                        ],
                                                                        data=[
                                                                            {
                                                                                "Vpp": round(df["Vpp"].mean()*1000,2) if not df.empty else "",
                                                                                "Energy": round(df["Energy"].mean(),2) if not df.empty else "",
                                                                                "Qapp": round(df["Qapp"].mean(),2) if not df.empty else "",
                                                                                "Average Time": round(df["x"].mean(),2) if not df.empty else "",
                                                                                "Number of Signals": round(len(df.columns)/2,2) if not df.empty else "",
                                                                            }
                                                                        ],
                                                                        style_table={"marginBottom": "20px"},
                                                                        style_cell={"textAlign": "center"},
                                                                        style_header={
                                                                            "fontWeight": "bold",
                                                                            "textAlign": "center"
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
                                                            # Time Series Plot with Dropdowns
                                                            html.Div(
                                                                [
                                                                    # First Dropdown (generic options)
                                                                    dcc.Dropdown(
                                                                        id="dropdown-x-axis",
                                                                        options=classMapVariables,
                                                                        value='Vpp',
                                                                        placeholder="x-axis",
                                                                        style={
                                                                            "marginBottom": "10px"
                                                                        },
                                                                    ),
                                                                    # Second Dropdown (generic options)
                                                                    dcc.Dropdown(
                                                                        id="dropdown-y-axis",
                                                                        options=classMapVariables,
                                                                        value='Energy',
                                                                        placeholder="y-axis",
                                                                        style={
                                                                            "marginBottom": "20px"
                                                                        },
                                                                    ),
                                                                    dcc.Graph(
                                                                        id="upper-right-graph",
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
                                                            # FFT Plot
                                                            html.Div(
                                                                [
                                                                    dcc.Graph(
                                                                        id="lower-right-graph",
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
                                    dcc.Tab(  # User Manual
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
        [Output("upper-right-graph", "figure"), Output("lower-right-graph", "figure")],
        [Input("scatter-plot", "clickData"), Input("scatter-plot", "selectedData"),
         Input("dropdown-x-axis", "value"), Input("dropdown-y-axis", "value")],
    )
    def update_plots(clickData, selectedData, x_axis, y_axis):
        
        ctx = dash.callback_context  # Get trigger context
        selected_PRPD_fig, fft_fig = [], []

        if not ctx.triggered:
            # Default selection logic
            selected_id = df["id"].iloc[0]
            # print(f"Default selected id: {selected_id}")
            selected_data = df[df["id"] == selected_id].iloc[0]
            # print(f"Default selected data: {selected_data}")
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
                selected_PRPD_fig, fft_fig = plot_time_fft_multiple(selected_data, x_axis, y_axis)

            elif "dropdown-x-axis" in triggered_id or "dropdown-y-axis" in triggered_id:
                # Handle dropdown axis change
                # Use the current selection if available, otherwise default
                if selectedData and "points" in selectedData and selectedData["points"]:
                    selected_ids = [pt["customdata"][3] for pt in selectedData["points"]]
                    selected_data = df[df["id"].isin(selected_ids)]
                    selected_PRPD_fig, fft_fig = plot_time_fft_multiple(selected_data, x_axis, y_axis)
                elif clickData and "points" in clickData and clickData["points"]:
                    selected_id = clickData["points"][0]["customdata"][3]
                    selected_data = df[df["id"] == selected_id].iloc[0]
                    selected_PRPD_fig, fft_fig = plot_time_fft_single(selected_data)
                else:
                    selected_id = df["id"].iloc[0]
                    selected_data = df[df["id"] == selected_id].iloc[0]
                    selected_PRPD_fig, fft_fig = plot_time_fft_single(selected_data)
                
            else:
                # Default fallback
                selected_id = df["id"].iloc[0]
                selected_data = df[df["id"] == selected_id].iloc[0]
                selected_PRPD_fig, fft_fig = plot_time_fft_single(selected_data)

        return selected_PRPD_fig, fft_fig

    # Callback for updating the scatter plot based on time-series interaction
    @app.callback(
        Output("scatter-plot-selected", "figure"),
        Input("upper-right-graph", "clickData"),
        Input("upper-right-graph", "selectedData"),
        State("scatter-plot-selected", "relayoutData"),
    )
    def update_scatter_plot_selected(clickData, selectedData, relayoutData):
        ctx = dash.callback_context  # Get trigger context
        selected_PRPD_fig = [], []

        # Handle zoom or relayout data
        if relayoutData and "xaxis.range[0]" in relayoutData and "xaxis.range[1]" in relayoutData \
        and "yaxis.range[0]" in relayoutData and "yaxis.range[1]" in relayoutData:
            stored_layout = go.Layout(
                title=dict(text="Selected Signals from TF Map", font=dict(size=14)),
                xaxis=dict(
                    title="Time (us)",
                    range=[
                        relayoutData["xaxis.range[0]"],
                        relayoutData["xaxis.range[1]"],
                    ]
                ),
                yaxis=dict(
                    title="Voltage (V)",
                    range=[
                        relayoutData["yaxis.range[0]"],
                        relayoutData["yaxis.range[1]"],
                    ]
                ),
                uirevision=True,
            )
        else:
            # Default layout
            stored_layout = go.Layout(
                title=dict(text="Selected Signals from TF Map", font=dict(size=14)),
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

                # Suponiendo que cada valor en 'signal' es una Serie o array
                signals_raw = filtered_df["signal"].tolist()

                # Convertimos todos a np.arrays limpios, sin índice
                signals_clean = [np.array(s) for s in signals_raw]

                # Creamos un DataFrame a partir de listas
                outputDF = pd.DataFrame(
                    signals_clean
                ).T  # Transponemos para que cada columna sea una señal

                # Renombramos columnas
                outputDF.columns = [f"ID: " + str(i) for i in scatterSelectedIds]

                # Exportamos CSV
                return dcc.send_data_frame(
                    outputDF.to_csv, "TRPD_graph_selected_data.csv", index=False
                )

            else:
                return None
    # Callback for downloading selected data from the TF Map
    @app.callback(
        Output("download-data-2", "data"),
        Input("button-2", "n_clicks"),
        State("upper-right-graph", "selectedData"),
    )
    def download_selected_data_TF_Map(button2, scatterSelectedData):
        if button2:
            if scatterSelectedData:
                scatterSelectedIds = [
                    point["customdata"][0] for point in scatterSelectedData["points"]
                ]
                filtered_df = df[df["id"].isin(scatterSelectedIds)]

                # Suponiendo que cada valor en 'signal' es una Serie o array
                signals_raw = filtered_df["signal"].tolist()

                # Convertimos todos a np.arrays limpios, sin índice
                signals_clean = [np.array(s) for s in signals_raw]

                # Creamos un DataFrame a partir de listas
                outputDF = pd.DataFrame(
                    signals_clean
                ).T  # Transponemos para que cada columna sea una señal

                # Renombramos columnas
                outputDF.columns = [f"ID: " + str(i) for i in scatterSelectedIds]

                # Exportamos CSV
                return dcc.send_data_frame(
                    outputDF.to_csv, "TF_Map_selected_data.csv", index=False
                )

            else:
                return None

    # Supón que tienes un DataTable con id='summary-table'
    @app.callback(
        Output('selected-values-metrics-table', 'data'),
        [
            Input('scatter-plot', 'selectedData'),
            Input('scatter-plot', 'clickData'),
            Input('upper-right-graph', 'selectedData'),
            Input('upper-right-graph', 'clickData'),
        ]
    )
    def update_table(scatter_selected, scatter_click, upper_selected, upper_click):
        ctx = dash.callback_context

        # Default: use all data
        filtered_df = df

        if ctx.triggered:
            triggered_id = ctx.triggered[0]['prop_id']
            if "upper-right-graph.selectedData" in triggered_id and upper_selected and "points" in upper_selected:
                selected_ids = [pt["customdata"][0] for pt in upper_selected["points"]]
                filtered_df = df[df["id"].isin(selected_ids)]
            elif "upper-right-graph.clickData" in triggered_id and upper_click and "points" in upper_click:
                selected_id = upper_click["points"][0]["customdata"][0]
                filtered_df = df[df["id"] == selected_id]
            elif "scatter-plot.selectedData" in triggered_id and scatter_selected and "points" in scatter_selected:
                selected_ids = [pt["customdata"][3] for pt in scatter_selected["points"]]
                filtered_df = df[df["id"].isin(selected_ids)]
            elif "scatter-plot.clickData" in triggered_id and scatter_click and "points" in scatter_click:
                selected_id = scatter_click["points"][0]["customdata"][3]
                filtered_df = df[df["id"] == selected_id]

        # Calculate metrics
        if not filtered_df.empty:
            vpp = round(filtered_df["Vpp"].mean() * 1e3, 2)
            energy = round(filtered_df["Energy"].mean()*1e3, 2)
            qapp = round(filtered_df["Qapp"].mean(), 2)
            avg_time = round(filtered_df["x"].mean(), 2)
            num_signals = int(filtered_df.shape[0])
        else:
            vpp = energy = qapp = avg_time = num_signals = ""

        new_data = [
            {
                "Vpp": vpp,
                "Energy": energy,
                "Qapp": qapp,
                "Average Time": avg_time,
                "Number of Signals": num_signals
            }
        ]
        return new_data



    # This block is not necessary if the Dash app is being run as a subprocess
    # from a main application like Tkinter. Instead, ensure the `create_dash_app`
    # function is called with the appropriate parameters from the main application.
    print(f"Dash app is running on: http://{host}:{port}/")  # Print app URL
    app.run(
        debug=False, host=host, port=port, use_reloader=False
    )  # Start the server without debug mode
