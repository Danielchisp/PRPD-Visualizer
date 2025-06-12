from dash.dependencies import Input, Output, State
from dash import dcc
import plotly.graph_objects as go  # Used for detailed graph customization
import numpy as np
import dash
from utils import build_export_dataframe
import pandas as pd
from config import (
    MODERN_PLOTLY_COLORS,
)  # Configuration settings imported from the 'config' module


from plotting import (  # Custom plotting functions imported from the 'plotting' module
    plot_class_map,
    plot_time_fft_single,
    plot_time_fft_multiple,
    plot_selected_PRPD_single,
    plot_selected_PRPD_multiple,
)


def register_callbacks(app, df, time, impulse, folder):

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

                elif (
                    triggered_id == "scatter-plot.selectedData" and selectedDataScatter
                ):
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

                elif (
                    triggered_id == "class-map-graph.selectedData" and selectedDataClass
                ):
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
        [Input("refresh-button", "refresh"), Input("division-dropdown", "value")],
    )
    def update_extra_plot_1(refresh, num_bins):
        num_bins = int(num_bins)  # Convert to integer

        # Leer los IDs seleccionados desde el archivo "Reverse HFCT"
        try:
            reverse_hfct_df = pd.read_csv(folder + "\\" + "Reverse HFCT.csv")
            if "id" in reverse_hfct_df.columns:
                selected_ids = reverse_hfct_df["id"].tolist()
                filtered_df = df[df["id"].isin(selected_ids)]
            else:
                filtered_df = df
        except Exception as e:
            print(f"Error reading 'Reverse HFCT': {e}")
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
        num_signals_norm = (
            num_signals / num_signals_max if num_signals_max else num_signals
        )

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=bin_centers,
                y=vpp_norm,
                mode="lines+markers",
                marker=dict(color=MODERN_PLOTLY_COLORS[0], size=8),
                line=dict(color=MODERN_PLOTLY_COLORS[0], width=2),
                name=(
                    f"Mean Vpp (mV) (max={vpp_max:.2f})" if vpp_max else "Mean Vpp (mV)"
                ),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=bin_centers,
                y=energy_norm,
                mode="lines+markers",
                marker=dict(color=MODERN_PLOTLY_COLORS[1], size=8),
                line=dict(color=MODERN_PLOTLY_COLORS[1], width=2),
                name=(
                    f"Mean Energy (mV²) (max={energy_max:.2f})"
                    if energy_max
                    else "Mean Energy (mV²)"
                ),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=bin_centers,
                y=num_signals_norm,
                mode="lines+markers",
                marker=dict(color=MODERN_PLOTLY_COLORS[2], size=8),
                line=dict(color=MODERN_PLOTLY_COLORS[2], width=2),
                name=(
                    f"Num. of Discharges (max={num_signals_max})"
                    if num_signals_max
                    else "Num. of Discharges"
                ),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y_norm,
                mode="markers",
                marker=dict(color="black", size=4),
                line=dict(color="black", width=2),
                name=f"Signal Data (max={y_max:.2f})" if y_max else "Signal Data",
            )
        )
        # Añadir eje secundario para el número de descargas
        fig.update_layout(
            yaxis=dict(title="Normalized Metrics"),
            title="",
            xaxis_title="Time (us)",
            template="simple_white",
            margin=dict(l=40, r=20, t=50, b=40),
            height=400,
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
            Output("download-data-0", "data"),
            Output("download-data-1", "data"),
            Output("download-data-2", "data"),
            Output("download-data-3", "data"),
            Output("download-data-4", "data"),
        ],
        [
            Input("button-0", "n_clicks"),
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
        btn0, btn1, btn2, btn3, btn4, scatter_selected, upper_selected
    ):
        ctx = dash.callback_context
        if not ctx.triggered:
            return [None, None, None, None, None]
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        # Download only IDs from class map selection
        if button_id == "button-0" and btn0:
            if (
                upper_selected
                and "points" in upper_selected
                and upper_selected["points"]
            ):
                ids = [pt["customdata"][0] for pt in upper_selected["points"]]
                # Ensure ids is always a list
                if not isinstance(ids, list):
                    ids = [ids]
                filtered_df = df[df["id"].isin(ids)]
                # Determinar el canal dominante
                if "channel" in filtered_df.columns and not filtered_df.empty:
                    channel_counts = filtered_df["channel"].value_counts(normalize=True)
                    main_channel = channel_counts.idxmax()
                    main_channel_ratio = channel_counts.max()
                    if main_channel_ratio >= 0.9:
                        filename = f"{main_channel}.csv"
                    else:
                        filename = "class_map_selected_ids.csv"
                else:
                    filename = "class_map_selected_ids.csv"
                outputDF = pd.DataFrame({"id": ids})
                return [
                    dcc.send_data_frame(outputDF.to_csv, filename, index=False),
                    None,
                    None,
                    None,
                    None,
                ]
            return [None, None, None, None, None]

        # Download Selected TRPD Temporal Signals
        if button_id == "button-1" and btn1:
            if scatter_selected:
                ids = [pt["customdata"][3] for pt in scatter_selected["points"]]
                filtered_df = df[df["id"].isin(ids)]
                outputDF = build_export_dataframe(filtered_df, "signal")
                return [
                    None,
                    dcc.send_data_frame(
                        outputDF.to_csv, "TRPD_graph_selected_data.csv", index=False
                    ),
                    None,
                    None,
                    None,
                ]
            return [None, None, None, None, None]

        # Download Selected Class. Map Temporal Signals
        if button_id == "button-2" and btn2:
            if upper_selected:
                ids = [pt["customdata"][0] for pt in upper_selected["points"]]
                filtered_df = df[df["id"].isin(ids)]
                outputDF = build_export_dataframe(filtered_df, "signal")
                return [
                    None,
                    None,
                    dcc.send_data_frame(
                        outputDF.to_csv, "TF_Map_selected_data.csv", index=False
                    ),
                    None,
                    None,
                ]
            return [None, None, None, None, None]

        # Download Selected TRPD FFT
        if button_id == "button-3" and btn3:
            if scatter_selected:
                ids = [pt["customdata"][3] for pt in scatter_selected["points"]]
                filtered_df = df[df["id"].isin(ids)]
                outputDF = build_export_dataframe(filtered_df, "fft_values")
                return [
                    None,
                    None,
                    None,
                    dcc.send_data_frame(
                        outputDF.to_csv, "TRPD_graph_selected_fft.csv", index=False
                    ),
                    None,
                ]
            return [None, None, None, None, None]

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
                    None,
                    dcc.send_data_frame(
                        outputDF.to_csv, "TF_Map_selected_fft.csv", index=False
                    ),
                ]
            return [None, None, None, None, None]

        return [None, None, None, None, None]

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
