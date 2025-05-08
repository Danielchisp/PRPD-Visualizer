import numpy as np
import plotly.graph_objects as go

# from main_data import impulse_ave_final, time1


import plotly.graph_objs as go


def create_scatter_layout():
    return go.Layout(
        title="",
        xaxis=dict(
            title=dict(text="X-Axis Label", font=dict(size=14)),
            tickfont=dict(size=12),
        ),
        yaxis=dict(
            title=dict(text="Y-Axis Label", font=dict(size=14)),
            tickfont=dict(size=12),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )


def plot_time_fft_single(selected_data):
    freqs = selected_data["freqs"]
    fft_values = selected_data["fft_values"] / max(abs(selected_data["fft_values"]))
    timeSignal = selected_data["signal"] / max(abs(selected_data["signal"]))

    time_fig = {
        "data": [
            go.Scatter(
                x=selected_data["t"],
                y=timeSignal,
                mode="lines",
                line=dict(color="blue"),
            )
        ],
        "layout": go.Layout(
            title=dict(
                text="Time Resolved PD",  # Título del gráfico
                font=dict(size=16),  # Tamaño de la fuente
            ),
            xaxis=dict(title="Time (us)"),
            yaxis=dict(title="(a.u)"),
        ),
    }

    fft_fig = {
        "data": [
            go.Scatter(x=freqs, y=fft_values, mode="lines", line=dict(color="red"))
        ],
        "layout": go.Layout(
            title=dict(
                text=f"Frequency Resolved PD",  # Título del gráfico
                font=dict(size=16),  # Tamaño de la fuente
            ),
            xaxis=dict(title="Frequency", range=[0, selected_data["fft_lim"]]),
            yaxis=dict(title="(a.u)"),
        ),
    }

    return time_fig, fft_fig


def plot_time_fft_multiple(selected_data):
    eqTimeList, eqFFTList = np.array(selected_data["T2"].tolist()), np.array(
        selected_data["W2"].tolist()
    )

    fft_list = np.array(selected_data["fft_values"].tolist())
    fft_promedio = np.mean(fft_list, axis=0) / max(abs(np.mean(fft_list, axis=0)))
    fft_mas_distante = fft_list[
        np.argmax(np.sum((fft_list - fft_promedio) ** 2, axis=1))
    ]
    fft_mas_distante /= max(abs(fft_mas_distante))

    time_fig = {
        "data": [
            go.Scattergl(
                x=eqTimeList,
                y=eqFFTList,
                mode="markers",
                marker=dict(
                    size=5,
                    color="black",
                    opacity=0.8,
                    line=dict(width=0.5, color="DarkSlateGrey"),
                ),
                customdata=np.stack(
                    (selected_data["id"],),
                    axis=-1,
                ),
                hovertemplate="<b>ID:</b> %{customdata[0]}<br>",
                name="Selected Data",
            )
        ],
        "layout": go.Layout(
            title=dict(
                text="Classification Map",
                font=dict(size=16),  # Define el tamaño de la fuente aquí
            ),
            xaxis=dict(title="Time (s)"),
            yaxis=dict(title="Equivalent Frequency (Hz)"),
        ),
    }

    freqs = selected_data["freqs"].iloc[0]
    fft_fig = {
        "data": [
            go.Scatter(
                x=freqs,
                y=fft_promedio,
                mode="lines",
                line=dict(color="red"),
                name="Average",
            ),
            go.Scatter(
                x=freqs,
                y=fft_mas_distante,
                mode="lines",
                line=dict(color="black", dash="dot"),
                name="Reference",
            ),
        ],
        "layout": go.Layout(
            title=dict(
                text="Frequency Resolved PD",
                font=dict(size=14),  # Define el tamaño de la fuente aquí
            ),
            xaxis=dict(title="Frequency", range=[0, selected_data["fft_lim"].iloc[0]]),
            yaxis=dict(title="(a.u)"),
        ),
    }

    return time_fig, fft_fig


def plot_selected_PRPD_single(selected_data, stored_layout, time, impulse):
    xValues = np.array(selected_data["x"].tolist())
    yValues = np.array(selected_data["y"].tolist())

    PRPD_single_fig = {
        "data": [
            go.Scatter(
                x=xValues,
                y=yValues,
                mode="markers",
                line=dict(color="blue"),
                name="Selected Data",
            ),
            go.Scatter(
                x=time,
                y=impulse,
                mode="lines",
                line=dict(color="black", width=2.5),
                name="Impulse",
                hoverinfo="none",
            ),
        ],
        "layout": stored_layout,
    }
    return PRPD_single_fig


def plot_selected_PRPD_multiple(selected_data, stored_layout, time, impulse):
    xValues = np.array(selected_data["x"].tolist())
    yValues = np.array(selected_data["y"].tolist())

    PRPD_multiple_fig = {
        "data": [
            go.Scatter(
                x=xValues,
                y=yValues,
                mode="markers",
                line=dict(color="blue"),
            ),
            go.Scatter(
                x=time,
                y=impulse,
                mode="lines",
                line=dict(color="black", width=2.5),
                name="Impulse",
                hoverinfo="none",
            ),
        ],
        "layout": stored_layout,
    }
    return PRPD_multiple_fig
