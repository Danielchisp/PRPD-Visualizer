from tkinter import Tk, filedialog, messagebox

import numpy as np


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
