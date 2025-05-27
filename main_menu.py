import tkinter as tk
from tkinter import *
from tkinter import messagebox, simpledialog, ttk
import matplotlib.pyplot as plt
import os
from multiprocessing import Process, freeze_support
from app import create_dash_app
from utils import get_input_parameters
from data_processing import process_data
import psutil
import pandas as pd
import numpy as np
import sys
from scipy.signal import resample
from scipy.signal import butter, filtfilt
import json


from config import (
    TRIGGER_SETTINGS,
    WINDOW_SETTINGS,
    CHANNEL_DICT,
    impulseDownsample,
    host,
    port,
    availablePorts,
    tkinterAppDim,
)

folder = None
df = None
scatter_traces = None
impulse_ave_final = None
time1 = None
dash_process = None
root = None
impulseMainData, mainHFCTMainData, reverseHFCTMainData, antennaMainData = (
    None,
    None,
    None,
    None,
)
time1, time2, time3, time4 = None, None, None, None
ram_label, metadata_label = None, None
port_selection = None


def load_data(folder):
    global status_label, ram_label, impulse_ave_final, spinbox_HPFilter

    status_label.config(
        text="Loading CH1 data... This may take a while...",
    )
    status_label.update()
    impulseMainData = pd.read_csv(
        folder + "\\" + CHANNEL_DICT["Impulse"] + ".csv", header=None, skiprows=25
    )
    update_ram_display()
    status_label.config(text="CH1 loaded")
    status_label.update()

    print("CH1 loaded")

    status_label.config(
        text="Loading CH2 data... This may take a while...",
    )
    status_label.update()
    mainHFCTMainData = pd.read_csv(
        folder + "\\" + CHANNEL_DICT["Ferrite 1"] + ".csv", header=None, skiprows=25
    )

    update_ram_display()
    status_label.config(text="CH2 loaded")
    status_label.update()

    print("CH2 loaded")
    status_label.config(
        text="Loading CH3 data... This may take a while...",
    )
    status_label.update()

    reverseHFCTMainData = pd.read_csv(
        folder + "\\" + CHANNEL_DICT["Ferrite 2"] + ".csv", header=None, skiprows=25
    )

    update_ram_display()
    status_label.config(text="CH3 loaded")
    status_label.update()

    print("CH3 loaded")

    status_label.config(
        text="Loading CH4 data... This may take a while...",
    )
    status_label.update()
    antennaMainData = pd.read_csv(
        folder + "\\" + CHANNEL_DICT["Antenna"] + ".csv", header=None, skiprows=25
    )

    update_ram_display()
    status_label.config(text="CH4 loaded")
    status_label.update()

    print("CH4 loaded")

    status_label.config(
        text="Data loaded successfully! Now calculating time vectors..."
    )
    status_label.update()

    finalTime = int(len(impulseMainData) / 5000)
    time1 = np.linspace(0, finalTime, len(impulseMainData))
    time2 = np.linspace(0, finalTime, len(mainHFCTMainData))
    time3 = np.linspace(0, finalTime, len(reverseHFCTMainData))
    time4 = np.linspace(0, finalTime, len(antennaMainData))

    print("Data loaded successfully.")

    time1 = np.linspace(time1[0], time1[-1], impulseDownsample)

    status_label.config(
        text="Data loaded successfully! Now applying HP filters to ferrites..."
    )

    # Definir parámetros del filtro
    order = 3
    fs = 5e9  # Frecuencia de muestreo en Hz (ajusta si es necesario)
    cutoff = (
        float(spinbox_HPFilter.get()) * 1e6
    )  # Frecuencia de corte en Hz (ajusta si es necesario)

    # Calcular los coeficientes del filtro Butterworth pasa-altos
    b, a = butter(order, cutoff / (0.5 * fs), btype="high", analog=False)

    # Filtrar las columnas impares de mainHFCTMainData y reverseHFCTMainData
    for df_signal in [mainHFCTMainData, reverseHFCTMainData]:
        for col in range(1, df_signal.shape[1], 2):
            df_signal[col] = filtfilt(b, a, df_signal[col].values)

    status_label.config(
        text="Data loaded successfully! Now calculating impulse average..."
    )
    status_label.update()

    impulsesNum = int(len(impulseMainData.columns) / 2)
    impulses_list = [impulseMainData[2 * i + 1] for i in range(impulsesNum)]
    impulse_ave_final = pd.DataFrame([sum(x) / len(x) for x in zip(*impulses_list)])[0]
    impulse_ave_final = resample(impulse_ave_final, impulseDownsample)

    return (
        impulseMainData,
        mainHFCTMainData,
        reverseHFCTMainData,
        antennaMainData,
        time1,
        time2,
        time3,
        time4,
    )


def get_ram_usage():
    # Obtener el uso de memoria del proceso actual
    process = psutil.Process(os.getpid())
    ram_usage = process.memory_info().rss / (1024 * 1024)  # Convertir a MB
    return ram_usage


def update_ram_display():
    ram_used = get_ram_usage()
    if ram_used > 1000:
        ram_label.config(text=f"RAM Usage: {ram_used / 1024:.2f} GB")
    else:
        ram_label.config(text=f"RAM Usage: {ram_used:.2f} MB")
    root.after(1000, update_ram_display)  # Update every second


def adjust_trigger_interface(x, y, impulseAve, color):
    global time1
    fig, ax = plt.subplots()
    fig.canvas.manager.window.attributes(
        "-topmost", 1
    )  # Asegurar que la ventana esté en primer plano
    # fig.canvas.manager.full_screen_toggle()  # Activar pantalla completa
    # Convierte impulseAve a array de numpy para evitar el TypeError
    impulseAve = np.array(impulseAve)
    ax.plot(x, y, color=color)
    ax.plot(time1, impulseAve * max(y) / max(abs(impulseAve)), color="red")
    ax.set_title(
        "Drag the red line to set the trigger level.\n"
        f"WARNING! Ensure all items in the palette are deselected before moving the line. When done, press Enter."
    )

    # Crear línea horizontal inicial en y=0
    hline = ax.axhline(y=0, color="r", linestyle="--", linewidth=2, picker=5)

    # Añadir texto para mostrar el valor actual
    trigger_text = ax.text(
        0.02,
        0.95,
        "0 V",
        transform=ax.transAxes,
        fontsize=12,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    # Usar una clase o atributos de fig para evitar variables globales
    def on_pick(event):
        if event.artist == hline:
            fig.dragging = True  # Almacenar el estado en la figura

    def on_motion(event):
        if hasattr(fig, "dragging") and fig.dragging and event.ydata is not None:
            current_y = event.ydata
            hline.set_ydata([current_y, current_y])
            # Actualizar el texto con el valor actual y unidades
            trigger_text.set_text(f"{current_y:.4f} V")
            fig.canvas.draw()

    def on_release(event):
        if hasattr(fig, "dragging"):
            fig.dragging = False

    def on_key_press(event):
        if event.key == "enter":
            fig.final_y = hline.get_ydata()[0]  # Guarda el valor actual de y
            plt.close(fig)  # Cierra la ventana

    # Conectar eventos
    fig.canvas.mpl_connect("pick_event", on_pick)
    fig.canvas.mpl_connect("motion_notify_event", on_motion)
    fig.canvas.mpl_connect("button_release_event", on_release)
    fig.canvas.mpl_connect("key_press_event", on_key_press)

    plt.show()  # Bloquear hasta que se cierre la ventana

    return hline.get_ydata()[0]


def update_trigger_labels():
    """Actualiza las etiquetas de los triggers en la GUI"""
    labelCH2Main.config(
        text=f"{round(TRIGGER_SETTINGS['mainHFCT']['main']*1000,2)} mV (Main)"
    )
    # labelCH2Reverse.config(
    #     text=f"{round(TRIGGER_SETTINGS['mainHFCT']['reverse']*1000,2)} mV (Rev)"
    # )
    # labelCH3Main.config(
    #     text=f"{round(TRIGGER_SETTINGS['reverseHFCT']['main']*1000,2)} mV (Main)"
    # )
    labelCH3Reverse.config(
        text=f"{round(TRIGGER_SETTINGS['reverseHFCT']['reverse']*1000,2)} mV (Rev)"
    )
    labelCH4Main.config(
        text=f"{round(TRIGGER_SETTINGS['antenna']['main']*1000,2)} mV (Main)"
    )
    # labelCH4Reverse.config(
    #     text=f"{round(TRIGGER_SETTINGS['antenna']['reverse']*1000,2)} mV (Rev)"
    # )


def load_app_data():
    global df, scatter_traces, impulse_ave_final, time1, status_label, folder_label, CHANNEL_DICT
    global impulseMainData, mainHFCTMainData, reverseHFCTMainData, antennaMainData, time1, time2, time3, time4
    global comboImpulse, comboHFCTMain, comboHFCTReverse, comboAntenna
    global folder
    global spinbox_HPFilter

    CHANNEL_DICT["Impulse"] = comboImpulse.get()
    CHANNEL_DICT["Ferrite 1"] = comboHFCTMain.get()
    CHANNEL_DICT["Ferrite 2"] = comboHFCTReverse.get()
    CHANNEL_DICT["Antenna"] = comboAntenna.get()

    status_label.config(
        text="Searching for Measurement Folder...",
    )
    status_label.update()

    folder = get_input_parameters()
    if folder is None:

        messagebox.showerror("Error", "No folder selected.")
        status_label.config(
            text="No folder selected. In order to load the data, you need to select a folder.",
        )
        status_label.update()
        return

    status_label.config(text="Folder found! Loading data, this can take a while...")
    status_label.update()

    (
        impulseMainData,
        mainHFCTMainData,
        reverseHFCTMainData,
        antennaMainData,
        time1,
        time2,
        time3,
        time4,
    ) = load_data(folder)

    status_label.config(
        text="Data loaded successfully! Now you can set the trigger levels.",
    )
    status_label.update()

    folder_label.config(
        text=f"Data Loaded:\n{os.path.basename(folder)}\nHP Filter: {spinbox_HPFilter.get()} MHz",
        foreground="green",
    )
    folder_label.update()


def trigger_detection():
    global impulseMainData, mainHFCTMainData, reverseHFCTMainData, antennaMainData, time1, time2, time3, time4, impulse_ave_final
    global TRIGGER_SETTINGS, status_label
    IMPULSES_NUM = int(len(impulseMainData.columns) / 2)

    print(
        impulse_ave_final
    )  # -> impulse_ave_final es none. Esto debe procesarse una vez se cargan los datos.

    triggerSettingLoop = False

    while triggerSettingLoop == False:
        messagebox.showinfo(
            "Process Notification",
            f"The peak detection trigger adjustment process will now begin. A graph will open for each channel.\n"
            f"Drag the red line to set the trigger level.\n\n"
            f"WARNING! Ensure all items in the palette are deselected before moving the line.\n\n"
            f"Press Enter to confirm the value.",
        )

        status_label.config(
            text="Peak Detection Trigger Adjustment. Please select the signal to adjust"
        )

        status_label.update()

        signalPicked = simpledialog.askinteger(
            "Signal Selection",
            f"Select the signal number. Maximum value is {IMPULSES_NUM - 1}:",
            minvalue=0,
            maxvalue=IMPULSES_NUM - 1,
        )
        if signalPicked is None:
            messagebox.showerror("Error", "No signal selected. Process aborted.")

            status_label.config(
                text="No signal selected. Process aborted. Please select a signal to adjust the trigger level."
            )
            status_label.update()
            return

        signalNum = 2 * signalPicked + 1

        signalCH2 = mainHFCTMainData[signalNum]
        signalCH3 = reverseHFCTMainData[signalNum]
        signalCH4 = antennaMainData[signalNum]

        status_label.config(
            text=f"Adjusting Channel 2 trigger level. Drag the red line to set the trigger level.\n"
            f"WARNING! Ensure all items in the palette are deselected before moving the line."
        )
        status_label.update()
        TRIGGER_SETTINGS["mainHFCT"]["main"] = adjust_trigger_interface(
            time2, signalCH2, impulse_ave_final, "blue"
        )
        print(
            f"CH2 main trigger: {round(1000*TRIGGER_SETTINGS['mainHFCT']['main'],2)} mV"
        )

        status_label.config(
            text=f"Adjusting Channel 3 trigger level. Drag the red line to set the trigger level.\n"
            f"WARNING! Ensure all items in the palette are deselected before moving the line."
        )
        status_label.update()

        TRIGGER_SETTINGS["reverseHFCT"]["reverse"] = adjust_trigger_interface(
            time3, signalCH3, impulse_ave_final, "green"
        )
        print(
            f"CH3 reverse trigger: {round(1000*TRIGGER_SETTINGS['reverseHFCT']['reverse'],2)} mV"
        )

        status_label.config(
            text=f"Adjusting Channel 4 trigger level. Drag the red line to set the trigger level.\n"
            f"WARNING! Ensure all items in the palette are deselected before moving the line."
        )
        status_label.update()

        TRIGGER_SETTINGS["antenna"]["main"] = adjust_trigger_interface(
            time4, signalCH4, impulse_ave_final, "black"
        )
        print(
            f"CH4 main trigger: {round(1000*TRIGGER_SETTINGS['antenna']['main'],2)} mV"
        )

        response = messagebox.askokcancel(
            "Trigger Levels",
            f"CH2 Main: {round(TRIGGER_SETTINGS['mainHFCT']['main']*1000, 2)} mV\n"
            f"CH3 Reverse: {round(TRIGGER_SETTINGS['reverseHFCT']['reverse']*1000, 2)} mV\n"
            f"CH4 Main: {round(TRIGGER_SETTINGS['antenna']['main']*1000, 2)} mV\n\n"
            f"Do you want to proceed?\n"
            f"Press cancel to adjust again.",
            icon="info",
        )
        triggerSettingLoop = response

    update_trigger_labels()

    status_label.config(
        text="Trigger levels adjusted successfully! Now you can process the data."
    )
    status_label.update()


def process_data_GUI():
    global df, scatter_traces, impulse_ave_final, time1, status_label
    global impulseMainData, mainHFCTMainData, reverseHFCTMainData, antennaMainData, time1, time2, time3, time4
    global metadata_label
    global folder

    status_label.config(
        text="Processing data... This may take a few seconds.",
    )
    status_label.update()

    # Recoger los valores de los Spinbox
    get_spinbox_values()

    print("The following parameters have been set:")
    print(f"Window Antenna: {round(WINDOW_SETTINGS['window_antenna']/5000,2)} us")
    print(f"Window HFCT: {round(WINDOW_SETTINGS['window_HFCT']/5000,2)} us")
    print(f"Sampling Frequency: {WINDOW_SETTINGS['fs']} GHz")
    print(f"Main PD Time Init: {WINDOW_SETTINGS['main_time_init']} ns")
    print(f"Main PD Time End: {WINDOW_SETTINGS['main_time_fin']} ns")
    print(f"Reverse PD Time Init: {WINDOW_SETTINGS['reverse_time_init']} ns")

    # Procesar los datos
    df, scatter_traces, impulse_ave_final = process_data(
        impulseMainData,
        mainHFCTMainData,
        reverseHFCTMainData,
        antennaMainData,
        time1,
        time2,
        time3,
        time4,
        status_label,
        impulse_ave_final,
    )

    print("Data processed successfully!")
    # Actualizar la etiqueta de estado
    status_label.config(
        text="Metadata calculated successfully! Now you can visualize the data."
    )
    status_label.update()

    metadata_label.config(
        text=f"Metadata calculated:\n{os.path.basename(folder)}",
        foreground="green",
    )
    metadata_label.update()
    toggle_visualize_button(True)


def toggle_visualize_button(state):
    """Habilita/deshabilita el botón de visualización"""
    if "visualize_btn" in globals():
        new_state = tk.NORMAL if state else tk.DISABLED
        visualize_btn.config(state=new_state)


def run_dash_app(df, scatter_traces, time1, impulse_ave_final, port):
    # NOTA: Para evitar el KeyError: 'customdata' en app.py,
    # asegúrate de que el callback de Dash verifique si 'customdata' existe en clickData["points"][0]
    # Ejemplo en app.py:
    #   if "customdata" in clickData["points"][0]:
    #       selected_id = clickData["points"][0]["customdata"][3]
    #   else:
    #       selected_id = None
    create_dash_app(df, scatter_traces, time1, impulse_ave_final, host, port)


def visualize_data():
    global df, scatter_traces, time1, impulse_ave_final, dash_process, status_label, port_selection

    status_label.config(
        text="Starting visualization... This may take a few seconds.",
    )

    status_label.update()

    if dash_process and dash_process.is_alive():
        dash_process.terminate()
        dash_process.join()

    port = port_selection.get()

    # Crear nuevo proceso y pasar los datos como argumentos
    dash_process = Process(
        target=run_dash_app,
        args=(df, scatter_traces, time1, impulse_ave_final, port),
    )
    dash_process.start()

    status_label.config(text="Visualizing data...")
    status_label.update()

    # Create a clickable hyperlink in the status label using host and port
    status_label.config(
        text=f"Visualizing data... Click here to open: http://{host}:{port}",
        foreground="black",
        cursor="hand2",
    )
    status_label.bind("<Button-1>", lambda e: os.system(f"start http://{host}:{port}"))


def get_spinbox_values():
    global WINDOW_SETTINGS
    """Recoge los valores de los Spinbox y los devuelve en un diccionario."""

    WINDOW_SETTINGS["window_antenna"] = int(
        5000 * float(spinbox_timewindow_antenna.get())
    )
    WINDOW_SETTINGS["window_HFCT"] = int(5000 * float(spinbox_timewindow_HFCT.get()))
    WINDOW_SETTINGS["half_window_antenna"] = int(WINDOW_SETTINGS["window_antenna"] / 2)
    WINDOW_SETTINGS["half_window_HFCT"] = int(WINDOW_SETTINGS["window_HFCT"] / 2)
    WINDOW_SETTINGS["fs"] = float(spinbox_sampling_frequency.get()) * 1e9
    WINDOW_SETTINGS["main_time_init"] = 5000 * int(spinbox_mainPDinit.get())
    WINDOW_SETTINGS["main_time_fin"] = 5000 * int(spinbox_mainPDend.get())
    WINDOW_SETTINGS["reverse_time_init"] = 5000 * int(spinbox_reversePDinit.get())


def setup_gui():
    """Configura la interfaz gráfica de Tkinter"""
    global root, visualize_btn, status_label, folder_label
    global labelCH2Main, labelCH3Reverse, labelCH4Main
    global spinbox_timewindow_HFCT, spinbox_timewindow_antenna, spinbox_sampling_frequency
    global spinbox_mainPDinit, spinbox_mainPDend, spinbox_reversePDinit
    global ram_label, metadata_label
    global comboAntenna, comboHFCTMain, comboHFCTReverse, comboImpulse
    global logo_img  # Para evitar que el recolector de basura elimine la imagen
    global port_selection
    global spinbox_HPFilter
    global tkinterAppDim

    root = tk.Tk()
    root.title("TRPD Analyzer & Viewer")
    root.geometry(tkinterAppDim)  # Ajustar el tamaño de la ventana
    root.resizable(False, False)

    # Cargar y asignar el ícono de la aplicación

    if getattr(sys, "frozen", False):
        # Si está congelado por PyInstaller
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    logo_path = os.path.join(base_path, "assets", "logo.png")
    try:
        logo_img = tk.PhotoImage(file=logo_path)
        root.iconphoto(False, logo_img)
    except Exception as e:
        print(f"No se pudo cargar el logo: {e}")
        logo_img = None

    # Marco principal
    main_frame = ttk.Frame(root)
    main_frame.pack(expand=True, fill=tk.BOTH)

    columna1 = ttk.Frame(main_frame, padding="5")
    columna1.grid(row=0, column=0, sticky="nsew")

    # Título
    ttk.Label(columna1, text="Main Menu", font=("Arial", 10, "bold")).pack(pady=5)

    # Botones
    load_data_btn = ttk.Button(
        columna1,
        text="1. Load Data (.csv)",
        command=load_app_data,  # Llama directamente a load_app_data
    )
    load_data_btn.pack(fill=tk.X, pady=5)  # Usar todo el ancho del contenedor

    # Cambiar el cursor al pasar el mouse
    load_data_btn.bind("<Enter>", lambda e: load_data_btn.config(cursor="hand2"))
    load_data_btn.bind("<Leave>", lambda e: load_data_btn.config(cursor=""))

    set_trigger_btn = ttk.Button(
        columna1,
        text="2. Set Trigger Level",
        command=trigger_detection,
    )
    set_trigger_btn.pack(fill=tk.X, pady=5)
    set_trigger_btn.bind("<Enter>", lambda e: set_trigger_btn.config(cursor="hand2"))
    set_trigger_btn.bind("<Leave>", lambda e: set_trigger_btn.config(cursor=""))

    calculate_metadata_btn = ttk.Button(
        columna1,
        text="3. Calculate TRPD Metadata",
        command=process_data_GUI,
    )
    calculate_metadata_btn.pack(fill=tk.X, pady=5)
    calculate_metadata_btn.bind(
        "<Enter>", lambda e: calculate_metadata_btn.config(cursor="hand2")
    )
    calculate_metadata_btn.bind(
        "<Leave>", lambda e: calculate_metadata_btn.config(cursor="")
    )

    visualize_btn = ttk.Button(
        columna1,
        text="4. Visualize Data",
        command=visualize_data,
        state=tk.DISABLED,
    )
    visualize_btn.pack(fill=tk.X, pady=5)
    visualize_btn.bind("<Enter>", lambda e: visualize_btn.config(cursor="hand2"))
    visualize_btn.bind("<Leave>", lambda e: visualize_btn.config(cursor=""))

    exit_btn = ttk.Button(
        columna1,
        text="5. Salir",
        command=exit_app,
    )
    exit_btn.pack(fill=tk.X, pady=5)
    exit_btn.bind("<Enter>", lambda e: exit_btn.config(cursor="hand2"))
    exit_btn.bind("<Leave>", lambda e: exit_btn.config(cursor=""))

    # Etiqueta de estado
    # Crear un frame para status_label y port selection juntos en la misma fila
    bottom_frame = ttk.Frame(main_frame)
    bottom_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=10)
    bottom_frame.columnconfigure(0, weight=3)
    bottom_frame.columnconfigure(1, weight=1)

    status_label = ttk.Label(
        bottom_frame, text="No data loaded", anchor="w", justify="left", padding="10"
    )
    status_label.grid(row=0, column=0, sticky="ew")

    # Port selection (alineado a la derecha en la misma fila)
    port_frame = ttk.Frame(bottom_frame)
    port_frame.grid(row=0, column=1, sticky="e", padx=(10, 0))

    ttk.Label(port_frame, text="Port Selection:", anchor="w", justify="left").grid(
        row=0, column=0, sticky="w", padx=(0, 5)
    )
    port_selection = ttk.Combobox(port_frame, values=availablePorts)
    port_selection.grid(row=0, column=1, sticky="w")
    port_selection.set(availablePorts[0])

    folder_label = ttk.Label(columna1, text="No Folder Selected", foreground="red")
    folder_label.pack(pady=10)

    metadata_label = ttk.Label(
        columna1, text="No Metadata Calculated", foreground="red"
    )
    metadata_label.pack(pady=10)

    ram_label = ttk.Label(
        columna1, text="RAM Usage: 0.00 MB", font=("Arial", 8, "bold"), anchor="center"
    )
    ram_label.pack(pady=0)

    ttk.Separator(columna1, orient="horizontal").pack(fill=tk.X, pady=10)

    # Iniciar la actualización periódica
    update_ram_display()

    columna2 = ttk.Frame(main_frame, padding="5")
    columna2.grid(row=0, column=1, sticky="nsew")

    ttk.Label(
        columna2, text="Trigger Detection Main Parameters", font=("Arial", 10, "bold")
    ).pack(pady=5)

    ttk.Label(columna2, text="Time Window HFCT (us):").pack(anchor="w")
    spinbox_timewindow_HFCT = ttk.Spinbox(columna2, from_=0.01, to=10, increment=0.1)
    spinbox_timewindow_HFCT.pack(fill=tk.X, pady=5)
    spinbox_timewindow_HFCT.set(1)

    ttk.Label(columna2, text="Time Window Antenna (us):").pack(anchor="w")
    spinbox_timewindow_antenna = ttk.Spinbox(columna2, from_=0.01, to=10, increment=0.1)
    spinbox_timewindow_antenna.pack(fill=tk.X, pady=5)
    spinbox_timewindow_antenna.set(0.1)

    ttk.Label(columna2, text="Samplig Frequency (GHz):").pack(anchor="w")
    spinbox_sampling_frequency = ttk.Spinbox(columna2, from_=0.1, to=10, increment=0.5)
    spinbox_sampling_frequency.pack(fill=tk.X, pady=5)
    spinbox_sampling_frequency.set(5)

    ttk.Label(columna2, text="Main PD Time Init (us):").pack(anchor="w")
    spinbox_mainPDinit = ttk.Spinbox(columna2, from_=0, to=200, increment=5)
    spinbox_mainPDinit.pack(fill=tk.X, pady=5)
    spinbox_mainPDinit.set(5)

    ttk.Label(columna2, text="Main PD Time End (us):").pack(anchor="w")
    spinbox_mainPDend = ttk.Spinbox(columna2, from_=0, to=200, increment=5)
    spinbox_mainPDend.pack(fill=tk.X, pady=5)
    spinbox_mainPDend.set(50)

    ttk.Label(columna2, text="Reverse PD Time Init (us):").pack(anchor="w")
    spinbox_reversePDinit = ttk.Spinbox(columna2, from_=0, to=200, increment=5)
    spinbox_reversePDinit.pack(fill=tk.X, pady=5)
    spinbox_reversePDinit.set(50)

    columna3 = ttk.Frame(main_frame, padding="5")
    columna3.grid(row=0, column=2, sticky="nsew")

    ttk.Label(columna3, text="Trigger Settings", font=("Arial", 10, "bold")).pack(
        pady=5
    )

    ttk.Label(columna3, text="Main HFCT", font=("Arial", 10, "bold")).pack(anchor="w")
    labelCH2Main = ttk.Label(
        columna3,
        text=f"{TRIGGER_SETTINGS['mainHFCT']['main']*1000} mV (Main)",
        font=("Arial", 10),
    )
    labelCH2Main.pack(fill=tk.X, pady=5)

    # labelCH2Reverse = ttk.Label(
    #     columna3,
    #     text=f"{TRIGGER_SETTINGS['mainHFCT']['reverse']*1000} mV (Rev)",
    #     font=("Arial", 10),
    # )
    # labelCH2Reverse.pack(fill=tk.X, pady=5)

    ttk.Separator(columna3, orient="horizontal").pack(fill=tk.X, pady=10)

    ttk.Label(columna3, text="Reverse HFCT", font=("Arial", 10, "bold")).pack(
        anchor="w"
    )

    # labelCH3Main = ttk.Label(
    #     columna3,
    #     text=f"{TRIGGER_SETTINGS['reverseHFCT']['main']*1000} mV (Main)",
    #     font=("Arial", 10),
    # )
    # labelCH3Main.pack(fill=tk.X, pady=5)

    labelCH3Reverse = ttk.Label(
        columna3,
        text=f"{TRIGGER_SETTINGS['reverseHFCT']['reverse']*1000} mV (Rev)",
        font=("Arial", 10),
    )
    labelCH3Reverse.pack(fill=tk.X, pady=5)

    ttk.Separator(columna3, orient="horizontal").pack(fill=tk.X, pady=10)

    ttk.Label(columna3, text="Antenna", font=("Arial", 10, "bold")).pack(anchor="w")

    labelCH4Main = ttk.Label(
        columna3,
        text=f"{TRIGGER_SETTINGS['antenna']['main']*1000} mV (Main)",
        font=("Arial", 10),
    )
    labelCH4Main.pack(fill=tk.X, pady=5)

    # labelCH4Reverse = ttk.Label(
    #     columna3,
    #     text=f"{TRIGGER_SETTINGS['antenna']['reverse']*1000} mV (Reverse)",
    #     font=("Arial", 10),
    # )
    # labelCH4Reverse.pack(fill=tk.X, pady=5)

    ttk.Separator(columna3, orient="horizontal").pack(fill=tk.X, pady=10)

    columna4 = ttk.Frame(main_frame, padding="5")
    columna4.grid(row=0, column=3, sticky="nsew")

    ttk.Label(columna4, text="Channel Assignment", font=("Arial", 10, "bold")).pack(
        pady=5
    )

    ttk.Label(columna4, text="HFCTs HP Filter (MHz)").pack(anchor="w")

    spinbox_HPFilter = ttk.Spinbox(columna4, from_=0.001, to=50, increment=1)
    spinbox_HPFilter.pack(fill=tk.X, pady=5)
    spinbox_HPFilter.set(5)

    ttk.Label(columna4, text="Impulse").pack(anchor="w")

    comboImpulse = ttk.Combobox(columna4, values=["CH1", "CH2", "CH3", "CH4"])
    comboImpulse.pack(fill=tk.X, pady=5)
    comboImpulse.set("CH1")

    ttk.Label(columna4, text="Main HFCT").pack(anchor="w")

    comboHFCTMain = ttk.Combobox(columna4, values=["CH1", "CH2", "CH3", "CH4"])
    comboHFCTMain.pack(fill=tk.X, pady=5)
    comboHFCTMain.set("CH2")

    ttk.Label(columna4, text="Reverse HFCT").pack(anchor="w")

    comboHFCTReverse = ttk.Combobox(columna4, values=["CH1", "CH2", "CH3", "CH4"])
    comboHFCTReverse.pack(fill=tk.X, pady=5)
    comboHFCTReverse.set("CH3")

    ttk.Label(columna4, text="Antenna").pack(anchor="w")
    comboAntenna = ttk.Combobox(columna4, values=["CH1", "CH2", "CH3", "CH4"])
    comboAntenna.pack(fill=tk.X, pady=5)
    comboAntenna.set("CH4")

    return root


def check_dash_process():
    """Verifica si el hilo de Dash sigue activo"""
    global dash_process

    if dash_process.is_alive():
        root.after(100, check_dash_process)
    else:
        toggle_visualize_button(True)


def exit_app():
    global dash_process
    if dash_process and dash_process.is_alive():
        dash_process.terminate()
        dash_process.join()
    root.quit()
    root.destroy()  # Asegura destrucción completa de la ventana


def main():
    """Función principal"""
    freeze_support()
    window = setup_gui()
    window.mainloop()


if __name__ == "__main__":
    # Para compatibilidad con Windows
    main()
