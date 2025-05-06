from tkinter import Tk, filedialog

import numpy as np


def get_input_parameters():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder = filedialog.askdirectory(title="Select Folder")

    return folder


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
