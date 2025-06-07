from tkinter import Tk, filedialog, messagebox

import numpy as np
import pandas as pd
from scipy import signal

from config import WINDOW_SETTINGS


def get_folder():
    """
    Muestra un diálogo para seleccionar un directorio.
    Si el usuario cancela, pregunta si desea reintentar.

    Returns:
        str: Ruta del directorio seleccionado o None si se cancela
    """
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    while True:
        folder = filedialog.askdirectory(title="Select Folder")

        # Si se seleccionó un directorio, retornarlo
        if folder:
            return folder

        # Si se cancela, preguntar si quiere reintentar
        retry = messagebox.askretrycancel(
            "Selección requerida",
            "Debe seleccionar un directorio. ¿Desea intentarlo de nuevo?",
        )

        # Si cancela el reintento, retornar None
        if not retry:
            return None


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def time_power(x):
    return np.sum(x**2)


def find_near_index(array, valores):
    indices = []
    for valor in valores:
        diferencias = np.abs(array - valor)
        indice = np.argmin(diferencias)
        indices.append(indice)
    return indices


def impulse_metrics(impulse):

    max_index = np.argmax(impulse)
    delta_90 = np.argmin(np.abs(impulse - 0.9 * impulse[max_index])[0:max_index])
    delta_30 = np.argmin(np.abs(impulse - 0.3 * impulse[max_index])[0:max_index])
    delta_50 = (
        np.argmin(np.abs(impulse - 0.5 * impulse[max_index])[max_index:-1]) + max_index
    )

    m = (impulse[delta_90] - impulse[delta_30]) / (delta_90 - delta_30)
    tmax = int((impulse[max_index] - impulse[delta_90]) / m + delta_90)
    t0 = int((-1 * impulse[delta_90]) / m + delta_90)

    metrics = {
        "tmax": max_index,
        "t90": delta_90,
        "t50": delta_50,
        "t30": delta_30,
        "tmax_linear": tmax,
        "t0_linear": t0,
    }

    return metrics


def calculate_time_corrections(impulseMainData):
    fs = WINDOW_SETTINGS["fs"]
    cutoff = 5e6

    b, a = signal.butter(4, cutoff / (0.5 * fs), btype="low")
    filtered_signals = [
        signal.filtfilt(b, a, impulseMainData[2 * i + 1])
        for i in range(int(len(impulseMainData.columns) / 2))
    ]
    impulse_params = [impulse_metrics(sig) for sig in filtered_signals]
    mean_signal = np.mean(np.stack(filtered_signals), axis=0)
    mean_params = impulse_metrics(mean_signal)
    return [(mean_params["tmax"] - p["tmax"]) * 1e6 / fs for p in impulse_params]


def build_export_dataframe(filtered_df, value_key):
    """
    Construye un DataFrame para exportar, con la primera columna como nombres de parámetros
    y las siguientes columnas como los valores de cada señal seleccionada.
    value_key: 'signal' o 'fft_values'
    """
    # Extraer los datos de cada señal
    values_list = filtered_df[value_key].tolist()
    values_clean = [np.array(v) for v in values_list]

    # Extraer los parámetros
    vpp_list = filtered_df["Vpp"].tolist()
    t_peak_list = filtered_df["x"].tolist()
    v_peak_list = filtered_df["y"].tolist()
    id_list = filtered_df["id"].tolist()

    # Construir la matriz de salida: cada columna es una señal
    data_matrix = []
    # Fila 0: Peak to Peak Voltage
    data_matrix.append(["Peak to Peak Voltage"] + vpp_list)
    # Fila 1: t_peak
    data_matrix.append(["t_peak"] + t_peak_list)
    # Fila 2: V_peak
    data_matrix.append(["V_peak"] + v_peak_list)
    # Fila 3: id
    data_matrix.append(["id"] + id_list)

    # Ahora, para los datos de la señal/fft, cada fila será un punto de la señal
    max_len = max(len(arr) for arr in values_clean) if values_clean else 0
    for i in range(max_len):
        row = [f"point_{i}"]
        for arr in values_clean:
            if i < len(arr):
                row.append(arr[i])
            else:
                row.append("")
        data_matrix.append(row)

    # Construir DataFrame
    col_names = ["Parameter"] + [f"ID: {i}" for i in id_list]
    outputDF = pd.DataFrame(data_matrix, columns=col_names)

    return outputDF
