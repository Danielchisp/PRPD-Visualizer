import numpy as np
from scipy.stats import gaussian_kde
import plotly.graph_objects as go


import plotly.graph_objs as go


def create_scatter_layout():
    return go.Layout(
        title="",
        xaxis=dict(
            title=dict(text="Time (us)", font=dict(size=14)),
            tickfont=dict(size=12),
        ),
        yaxis=dict(
            title=dict(text="Voltage (V)", font=dict(size=14)),
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


def plot_time_fft_multiple(selected_data, xValue, yValue):
    
    labelDict = {
        'Energy': 'Energy (V^2)',
        'Vpp': 'Peak to Peak Voltage (V)',
        'Qapp': 'Apparent Charge (C)',
        'T2': 'Equivalent Time (s)',
        'W2': 'Equivalent Frequency (Hz)'}
    



    # Obtener las FFTs y sus tamaños
    fft_values = selected_data["fft_values"].tolist()
    fft_lengths = [len(fft) for fft in fft_values]

    # Verificar si hay FFTs de tamaños distintos
    unique_lengths = set(fft_lengths)

    if len(unique_lengths) > 1:  # Si hay tamaños distintos
        print("Warning: FFTs have different sizes. Plotting averages for each size.")

        # Separar las FFTs por tamaño
        fft_groups = {length: [] for length in unique_lengths}
        for fft, length in zip(fft_values, fft_lengths):
            fft_groups[length].append(fft)

        # Calcular el promedio de cada grupo
        fft_fig_data = []
        for length, group in fft_groups.items():
            fft_array = np.array(group)
            fft_average = np.mean(fft_array, axis=0) / max(
                abs(np.mean(fft_array, axis=0))
            )
            freqs = selected_data["freqs"].iloc[0][
                : len(fft_average)
            ]  # Ajustar frecuencias al tamaño
            fft_fig_data.append(
                go.Scatter(
                    x=freqs,
                    y=fft_average,
                    mode="lines",
                    name=f"Average FFT (Size {length})",
                )
            )

        # Crear el gráfico de FFT con las curvas promedio
        fft_fig = {
            "data": fft_fig_data,
            "layout": go.Layout(
                title=dict(
                    text="Frequency Resolved PD (Multiple Sizes)",
                    font=dict(size=14),
                ),
                xaxis=dict(
                    title="Frequency", range=[0, selected_data["fft_lim"].iloc[0]]
                ),
                yaxis=dict(title="(a.u)"),
            ),
        }
    else:  # Si todas las FFTs tienen el mismo tamaño
        fft_list = np.array(fft_values)
        fft_promedio = np.mean(fft_list, axis=0) / max(abs(np.mean(fft_list, axis=0)))
        fft_mas_distante = fft_list[
            np.argmax(np.sum((fft_list - fft_promedio) ** 2, axis=1))
        ]
        fft_mas_distante /= max(abs(fft_mas_distante))

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
                    font=dict(size=14),
                ),
                xaxis=dict(
                    title="Frequency", range=[0, selected_data["fft_lim"].iloc[0]]
                ),
                yaxis=dict(title="(a.u)"),
            ),
        }

    # Generar el gráfico de scatter (time_fig) siempre
    time_fig = {
        "data": [
            go.Scattergl(
                x=selected_data[xValue].tolist(),
                y=selected_data[yValue].tolist(),
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
                font=dict(size=16),
            ),
            xaxis=dict(title=labelDict[xValue]),
            yaxis=dict(title=labelDict[yValue]),
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

    # Calcular la densidad de puntos usando un histograma 2D

    xy = np.vstack([xValues, yValues])
    z = gaussian_kde(xy)(xy)

    # Normalizar la densidad para mapearla a la escala de colores
    z_norm = (z - z.min()) / (z.max() - z.min())

    PRPD_multiple_fig = {
        "data": [
            go.Scatter(
                x=xValues,
                y=yValues,
                mode="markers",
                marker=dict(
                    size=6,
                    color=z_norm,
                    colorscale="plasma",
                    colorbar=dict(
                        title="Density",
                        y=0.7,
                        yanchor="middle"
                    ),
                    showscale=False,  # Oculta la barra de escala de colores
                    opacity=0.8,
                    line=dict(width=0.5, color="DarkSlateGrey"),
                ),
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
    return PRPD_multiple_fig
