from dash.dependencies import Input, Output, State
from dash import dcc
import plotly.graph_objects as go  # Used for detailed graph customization
import numpy as np
import dash
from utils import build_export_dataframe, impulse_metrics
import pandas as pd
import os
import pickle
from config import (
    CHANNEL_COLORS,
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
        [
            Output("extra-plot-1", "figure"),
            Output("extra-plot-2", "figure"),
            Output("extra-plot-3", "figure"),
        ],
        [
            Input("refresh-button-single-voltage", "n_clicks"),
            Input("division-dropdown", "value"),
        ],
    )
    def update_extra_plots(n_clicks, num_bins):
        # ----------- Plot 1: Reverse Metrics -----------
        num_bins = int(num_bins) if num_bins is not None else 10
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

        y_col = "y" if "y" in filtered_df.columns else filtered_df.columns[0]
        y = np.array(filtered_df[y_col].values)
        y_max = np.max(np.abs(y)) if y.size > 0 else 0
        y_norm = y / y_max if y.size > 0 and y_max != 0 else y
        time_dps = "x" if "x" in filtered_df.columns else None
        x = np.array(filtered_df[time_dps].values) if time_dps else np.arange(len(filtered_df))
        bins = np.linspace(np.min(x), np.max(x), num_bins + 1) if x.size > 0 else np.linspace(0, 1, num_bins + 1)
        bin_centers, vpp_means, energy_means, num_signals = [], [], [], []
        for i in range(num_bins):
            bin_mask = (x >= bins[i]) & (x < bins[i + 1])
            bin_df = filtered_df[bin_mask]
            bin_centers.append((bins[i] + bins[i + 1]) / 2)
            if not bin_df.empty:
                vpp_means.append(bin_df["Vpp"].mean() * 1e3)
                energy_means.append(bin_df["Energy"].mean())
                num_signals.append(len(bin_df))
            else:
                vpp_means.append(0)
                energy_means.append(0)
                num_signals.append(0)
        bin_centers = np.array(bin_centers)
        vpp_means = np.array(vpp_means)
        energy_means = np.array(energy_means)
        num_signals = np.array(num_signals)
        vpp_max = np.max(vpp_means) if np.any(vpp_means) else 0
        energy_max = np.max(energy_means) if np.any(energy_means) else 0
        num_signals_max = np.max(num_signals) if np.any(num_signals) else 0
        vpp_norm = vpp_means / vpp_max if vpp_max else vpp_means
        energy_norm = energy_means / energy_max if energy_max else energy_means
        num_signals_norm = num_signals / num_signals_max if num_signals_max else num_signals
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=bin_centers, y=vpp_norm, mode="lines+markers",
                                  marker=dict(color=MODERN_PLOTLY_COLORS[0], size=8),
                                  line=dict(color=MODERN_PLOTLY_COLORS[0], width=2),
                                  name=f"Mean Vpp (mV) (max={vpp_max:.2f})" if vpp_max else "Mean Vpp (mV)"))
        fig1.add_trace(go.Scatter(x=bin_centers, y=energy_norm, mode="lines+markers",
                                  marker=dict(color=MODERN_PLOTLY_COLORS[1], size=8),
                                  line=dict(color=MODERN_PLOTLY_COLORS[1], width=2),
                                  name=f"Mean Energy (mV²) (max={energy_max:.2f})" if energy_max else "Mean Energy (mV²)"))
        fig1.add_trace(go.Scatter(x=bin_centers, y=num_signals_norm, mode="lines+markers",
                                  marker=dict(color="black", size=8),
                                  line=dict(color="black", width=2),
                                  name=f"Num. of Discharges (max={num_signals_max})" if num_signals_max else "Num. of Discharges"))
        fig1.add_trace(go.Scatter(x=x, y=y_norm, mode="markers",
                                  marker=dict(color=CHANNEL_COLORS["CH3"], size=4),
                                  line=dict(color=CHANNEL_COLORS["CH3"], width=2),
                                  name=f"Signal Data (max={y_max:.2f})" if y_max else "Signal Data"))
        fig1.update_layout(
            yaxis=dict(title="Normalized Metrics"),
            title="",
            xaxis_title="Time (us)",
            template="simple_white",
            margin=dict(l=40, r=20, t=50, b=40),
            height=400,
        )

        # ----------- Plot 2: FFT Comparison -----------
        try:
            reverse_hfct_df = pd.read_csv(folder + "\\" + "Reverse HFCT.csv")
            main_hfct_df = pd.read_csv(folder + "\\" + "Main HFCT.csv")
            reverse_ids = reverse_hfct_df["id"].tolist() if "id" in reverse_hfct_df.columns else []
            main_ids = main_hfct_df["id"].tolist() if "id" in main_hfct_df.columns else []
            reverse_filtered = df[df["id"].isin(reverse_ids)] if reverse_ids else pd.DataFrame()
            main_filtered = df[df["id"].isin(main_ids)] if main_ids else pd.DataFrame()
        except Exception as e:
            print(f"Error reading HFCT files: {e}")
            reverse_filtered = pd.DataFrame()
            main_filtered = pd.DataFrame()
        def get_fft_mean(filtered):
            fft_list = []
            for _, row in filtered.iterrows():
                fft_val = row.get("fft_values", None)
                if isinstance(fft_val, (list, np.ndarray)):
                    fft_list.append(np.array(fft_val))
            if fft_list:
                fft_matrix = np.vstack(fft_list)
                fft_mean = np.mean(fft_matrix, axis=0)
                max_val = np.max(np.abs(fft_mean))
                if max_val != 0:
                    fft_mean = fft_mean / max_val
                return fft_mean
            else:
                return None
        reverse_fft_mean = get_fft_mean(reverse_filtered)
        main_fft_mean = get_fft_mean(main_filtered)
        freq = None
        if not reverse_filtered.empty and "fft_freq" in reverse_filtered.columns:
            freq = reverse_filtered.iloc[0]["fft_freq"]
        elif not main_filtered.empty and "fft_freq" in main_filtered.columns:
            freq = main_filtered.iloc[0]["fft_freq"]
        if isinstance(freq, str):
            try:
                freq = eval(freq)
            except Exception:
                freq = None
        fig2 = go.Figure()
        if reverse_fft_mean is not None:
            fig2.add_trace(go.Scatter(
                x=freq if freq is not None else np.arange(len(reverse_fft_mean)),
                y=reverse_fft_mean,
                mode="lines",
                line=dict(color=MODERN_PLOTLY_COLORS[0], width=3),
                name="Reverse HFCT (mean, normalized)",
            ))
        if main_fft_mean is not None:
            fig2.add_trace(go.Scatter(
                x=freq if freq is not None else np.arange(len(main_fft_mean)),
                y=main_fft_mean,
                mode="lines",
                line=dict(color=MODERN_PLOTLY_COLORS[1], width=3),
                name="Main HFCT (mean, normalized)",
            ))
        fig2.update_layout(
            title="FFT Mean Comparison (Reverse/Main HFCT, Normalized)",
            xaxis_title="Frequency (MHz)" if freq is not None else "Frequency (MHz)",
            yaxis_title="Normalized FFT Magnitude",
            template="simple_white",
            height=400,
            margin=dict(l=40, r=20, t=50, b=40),
            xaxis=dict(range=[0, 100]),
        )

        # ----------- Plot 3: Impulse Basis Metrics -----------
        def get_impulse_vpp(filtered):
            if (
                filtered.empty
                or "impulseNum" not in filtered.columns
                or "Vpp" not in filtered.columns
            ):
                return pd.DataFrame(columns=["impulseNum", "Vpp_mean"])
            grouped = (
                filtered.groupby("impulseNum")
                .agg(Vpp_mean=("Vpp", "mean"))
                .reset_index()
            )
            grouped["Vpp_mean"] = grouped["Vpp_mean"] * 1e3  # mV
            return grouped
        def get_impulse_mean_time(filtered):
            if (
                filtered.empty
                or "impulseNum" not in filtered.columns
                or "x" not in filtered.columns
            ):
                return pd.DataFrame(columns=["impulseNum", "min_time"])
            grouped = (
                filtered.groupby("impulseNum").agg(min_time=("x", "min")).reset_index()
            )
            return grouped
        df_rev = get_impulse_vpp(reverse_filtered)
        df_main = get_impulse_vpp(main_filtered)
        df_rev_time = get_impulse_mean_time(reverse_filtered)
        fig3 = go.Figure()
        if not df_main.empty:
            fig3.add_trace(go.Scatter(
                x=df_main["impulseNum"],
                y=df_main["Vpp_mean"]/max(df_main["Vpp_mean"]),
                mode="lines+markers",
                marker=dict(color=MODERN_PLOTLY_COLORS[0], size=8),
                line=dict(color=MODERN_PLOTLY_COLORS[0], width=2),
                name="Main HFCT Vpp Mean",
                yaxis="y1",
            ))
        if not df_rev.empty:
            fig3.add_trace(go.Scatter(
                x=df_rev["impulseNum"],
                y=df_rev["Vpp_mean"]/max(df_rev["Vpp_mean"]),
                mode="lines+markers",
                marker=dict(color=MODERN_PLOTLY_COLORS[1], size=8),
                line=dict(color=MODERN_PLOTLY_COLORS[1], width=2),
                name="Reverse HFCT Vpp Mean",
                yaxis="y1",
            ))
        if not df_rev_time.empty:
            fig3.add_trace(go.Scatter(
                x=df_rev_time["impulseNum"],
                y=df_rev_time["min_time"],
                mode="lines+markers",
                marker=dict(color="black", size=8, symbol="diamond"),
                line=dict(color="black", width=2),
                name="Reverse HFCT Min Time (us)",
                yaxis="y2",
            ))
        fig3.update_layout(
            title="Vpp Mean by Impulse Number (Main & Reverse HFCT) and Min Reverse Time",
            xaxis_title="Impulse Number",
            yaxis=dict(
                title="Vpp Mean (mV)",
                side="left",
                showgrid=True,
            ),
            yaxis2=dict(
                title="Min Reverse Time (us)",
                overlaying="y",
                side="right",
                showgrid=False,
            ),
            template="simple_white",
            height=400,
            margin=dict(l=40, r=20, t=50, b=40),
            legend=dict(
                x=0.01,
                y=0.99,
                title=""
            ),
        )
        return [fig1, fig2, fig3]

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

    @app.callback(
        Output("voltage-dep-1", "figure"),
        [
            Input("refresh-button-multi-voltage", "n_clicks"),
            Input("voltage-slider-1", "value"),
        ],
    )
    def update_voltage_dependent_graph_1(n_clicks, gain1):
        parent_folder = os.path.dirname(folder)
        cache_file = os.path.join(parent_folder, "impulse_data_cache_1.pkl")
        subfolders = [f for f in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, f))]
        fig1 = go.Figure()

        # Intentar cargar datos cacheados
        impulse_data = None
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "rb") as f:
                    impulse_data = pickle.load(f)
            except Exception as e:
                print(f"Error loading cache file {cache_file}: {e}")
                impulse_data = None

        # Si no hay cache, calcular y guardar
        if impulse_data is None:
            impulse_data = []
            for sub in subfolders:
                sub_path = os.path.join(parent_folder, sub)
                impulse_ave_path = os.path.join(sub_path, "impulse_ave_final.npy")
                if os.path.exists(impulse_ave_path):
                    try:
                        impulse_ave = np.load(impulse_ave_path)
                        metrics = impulse_metrics(impulse_ave)
                        t0_linear = metrics.get("t0_linear", 0)
                        impulse_data.append({
                            "sub": sub,
                            "impulse_ave": impulse_ave,
                            "t0_linear": t0_linear,
                            "path": sub_path
                        })
                    except Exception as e:
                        print(f"Error loading {impulse_ave_path}: {e}")
            # Guardar cache
            try:
                with open(cache_file, "wb") as f:
                    pickle.dump(impulse_data, f)
            except Exception as e:
                print(f"Error saving cache file {cache_file}: {e}")

        if not impulse_data:
            fig1.update_layout(title="No impulse_ave_final.npy found in subfolders")
            return fig1

        max_t0 = max(d["t0_linear"] for d in impulse_data)

        for i, data in enumerate(impulse_data):
            sub = data["sub"]
            impulse_ave = data["impulse_ave"]
            t0_linear = data["t0_linear"]
            sub_path = data["path"]
            color = MODERN_PLOTLY_COLORS[i % len(MODERN_PLOTLY_COLORS)]

            delay_samples = int(round(max_t0 - t0_linear))
            sample_us = 200.0 / len(impulse_ave)
            delay_us = delay_samples * sample_us

            x_full = np.arange(0, 200, 0.002)
            n_full = len(x_full)
            y_aligned = np.full(n_full, np.nan)
            start_idx = delay_samples
            end_idx = min(start_idx + len(impulse_ave), n_full)
            if start_idx < n_full:
                y_aligned[start_idx:end_idx] = impulse_ave[:end_idx - start_idx]
            x_resampled = np.arange(0, 200, 0.1)
            y_resampled = np.interp(x_resampled, x_full, y_aligned * gain1)

            fig1.add_trace(go.Scattergl(
                x=x_resampled,
                y=y_resampled,
                mode="lines",
                line=dict(color=color, width=2),
                name=f"{sub} impulse_ave"
            ))

            # Graficar Main HFCT en fig1
            main_hfct_path = os.path.join(sub_path, "Main HFCT.csv")
            trpd_metadata_path = os.path.join(sub_path, "TRPD_metadata.pkl")
            if os.path.exists(main_hfct_path) and os.path.exists(trpd_metadata_path):
                try:
                    main_hfct_df = pd.read_csv(main_hfct_path)
                    if "id" in main_hfct_df.columns and not main_hfct_df.empty:
                        trpd_metadata_df = pd.read_pickle(trpd_metadata_path)
                        all_x = []
                        all_y = []
                        for main_id in main_hfct_df["id"]:
                            row = trpd_metadata_df[trpd_metadata_df["id"] == main_id]
                            if not row.empty:
                                x = row.iloc[0].get("x")
                                y = row.iloc[0].get("y")
                                if isinstance(x, str):
                                    try: x = eval(x)
                                    except: x = None
                                if isinstance(y, str):
                                    try: y = eval(y)
                                    except: y = None
                                if x is not None and not isinstance(x, (list, np.ndarray, pd.Series)):
                                    x = [x]
                                if y is not None and not isinstance(y, (list, np.ndarray, pd.Series)):
                                    y = [y]
                                if x is not None and y is not None and len(x) == len(y):
                                    x_corr = np.array(x, dtype=float) + delay_us
                                    all_x.extend(x_corr)
                                    all_y.extend(y)
                        if all_x and all_y and len(all_x) == len(all_y):
                            fig1.add_trace(go.Scattergl(
                                x=all_x,
                                y=all_y,
                                mode="markers",
                                marker=dict(size=4, color=color),
                                name=f"{sub} Main HFCT"
                            ))
                except Exception as e:
                    print(f"Error loading Main HFCT for {sub}: {e}")

        fig1.update_layout(
            title="Impulse Average Final for All Subfolders<br>Aligned by t0_linear (delayed to max)",
            xaxis_title="Time (us)",
            yaxis_title="Amplitude",
            template="simple_white",
            xaxis=dict(range=[0, 30])
        )
        return fig1

    @app.callback(
        Output("voltage-dep-2", "figure"),
        [
            Input("refresh-button-multi-voltage", "n_clicks"),
            Input("voltage-slider-1", "value"),
            Input("voltage-slider-2", "value"),
        ],
    )
    def update_voltage_dependent_graph_2(n_clicks, gain1, gain2):
        parent_folder = os.path.dirname(folder)
        cache_file = os.path.join(parent_folder, "impulse_data_cache_2.pkl")
        subfolders = [f for f in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, f))]
        fig2 = go.Figure()

        # Intentar cargar datos cacheados
        impulse_data = None
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "rb") as f:
                    impulse_data = pickle.load(f)
            except Exception as e:
                print(f"Error loading cache file {cache_file}: {e}")
                impulse_data = None

        # Si no hay cache, calcular y guardar
        if impulse_data is None:
            impulse_data = []
            for sub in subfolders:
                sub_path = os.path.join(parent_folder, sub)
                impulse_ave_path = os.path.join(sub_path, "impulse_ave_final.npy")
                if os.path.exists(impulse_ave_path):
                    try:
                        impulse_ave = np.load(impulse_ave_path)
                        metrics = impulse_metrics(impulse_ave)
                        t0_linear = metrics.get("t0_linear", 0)
                        impulse_data.append({
                            "sub": sub,
                            "impulse_ave": impulse_ave,
                            "t0_linear": t0_linear,
                            "path": sub_path
                        })
                    except Exception as e:
                        print(f"Error loading {impulse_ave_path}: {e}")
            # Guardar cache
            try:
                with open(cache_file, "wb") as f:
                    pickle.dump(impulse_data, f)
            except Exception as e:
                print(f"Error saving cache file {cache_file}: {e}")

        if not impulse_data:
            fig2.update_layout(title="No impulse_ave_final.npy found in subfolders")
            return fig2

        max_t0 = max(d["t0_linear"] for d in impulse_data)

        for i, data in enumerate(impulse_data):
            sub = data["sub"]
            impulse_ave = data["impulse_ave"]
            t0_linear = data["t0_linear"]
            sub_path = data["path"]
            color = MODERN_PLOTLY_COLORS[i % len(MODERN_PLOTLY_COLORS)]

            delay_samples = int(round(max_t0 - t0_linear))
            sample_us = 200.0 / len(impulse_ave)
            delay_us = delay_samples * sample_us

            x_full = np.arange(0, 200, 0.002)
            n_full = len(x_full)
            y_aligned = np.full(n_full, np.nan)
            start_idx = delay_samples
            end_idx = min(start_idx + len(impulse_ave), n_full)
            if start_idx < n_full:
                y_aligned[start_idx:end_idx] = impulse_ave[:end_idx - start_idx]
            x_resampled = np.arange(0, 200, 0.1)
            # Solo aquí se usa gain2 para impulse_ave
            y_resampled = np.interp(x_resampled, x_full, y_aligned * gain2)

            fig2.add_trace(go.Scattergl(
                x=x_resampled,
                y=y_resampled,
                mode="lines",
                line=dict(color=color, width=2),
                name=f"{sub} impulse_ave"
            ))

            # Graficar Reverse HFCT en fig2
            reverse_hfct_path = os.path.join(sub_path, "Reverse HFCT.csv")
            trpd_metadata_path = os.path.join(sub_path, "TRPD_metadata.pkl")
            if os.path.exists(reverse_hfct_path) and os.path.exists(trpd_metadata_path):
                try:
                    reverse_hfct_df = pd.read_csv(reverse_hfct_path)
                    if "id" in reverse_hfct_df.columns and not reverse_hfct_df.empty:
                        trpd_metadata_df = pd.read_pickle(trpd_metadata_path)
                        all_x = []
                        all_y = []
                        for reverse_id in reverse_hfct_df["id"]:
                            row = trpd_metadata_df[trpd_metadata_df["id"] == reverse_id]
                            if not row.empty:
                                x = row.iloc[0].get("x")
                                y = row.iloc[0].get("y")
                                if isinstance(x, str):
                                    try: x = eval(x)
                                    except: x = None
                                if isinstance(y, str):
                                    try: y = eval(y)
                                    except: y = None
                                if x is not None and not isinstance(x, (list, np.ndarray, pd.Series)):
                                    x = [x]
                                if y is not None and not isinstance(y, (list, np.ndarray, pd.Series)):
                                    y = [y]
                                if x is not None and y is not None and len(x) == len(y):
                                    x_corr = np.array(x, dtype=float) + delay_us
                                    all_x.extend(x_corr)
                                    all_y.extend(y)
                        if all_x and all_y and len(all_x) == len(all_y):
                            fig2.add_trace(go.Scattergl(
                                x=all_x,
                                y=all_y,
                                mode="markers",
                                marker=dict(size=4, color=color),
                                name=f"{sub} Reverse HFCT",
                                opacity=0.7  # Transparencia
                            ))
                except Exception as e:
                    print(f"Error loading Reverse HFCT for {sub}: {e}")

        fig2.update_layout(
            title="Impulse Average Final for All Subfolders<br>Aligned by t0_linear (delayed to max)",
            xaxis_title="Time (us)",
            yaxis_title="Amplitude",
            template="simple_white"
        )
        return fig2