import tkinter as tk
from tkinter import *
from tkinter import messagebox, simpledialog, ttk
import matplotlib.pyplot as plt
import os
from multiprocessing import Process, freeze_support
from app import create_dash_app
from utils import get_folder
from data_processing import process_data, create_scatter_traces
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
    global status_label, ram_label, impulse_ave_final, spinbox_BPLowcut, spinbox_HPHighcut

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
    lowcut = float(spinbox_BPLowcut.get()) * 1e6  # Frecuencia de corte inferior en Hz
    highcut = float(spinbox_HPHighcut.get()) * 1e6  # Frecuencia de corte superior en Hz

    # Filtro pasaaltos para mainHFCTMainData
    b_hp, a_hp = butter(order, lowcut / (0.5 * fs), btype="high", analog=False)
    for col in range(1, mainHFCTMainData.shape[1], 2):
        mainHFCTMainData[col] = filtfilt(b_hp, a_hp, mainHFCTMainData[col].values)

    # Filtro pasabanda para reverseHFCTMainData
    b_bp, a_bp = butter(
        order, [lowcut / (0.5 * fs), highcut / (0.5 * fs)], btype="band", analog=False
    )
    for col in range(1, reverseHFCTMainData.shape[1], 2):
        reverseHFCTMainData[col] = filtfilt(b_bp, a_bp, reverseHFCTMainData[col].values)

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
    global df, scatter_traces, impulse_ave_final, time1, status_label, data_label, CHANNEL_DICT
    global impulseMainData, mainHFCTMainData, reverseHFCTMainData, antennaMainData, time1, time2, time3, time4
    global comboImpulse, comboHFCTMain, comboHFCTReverse, comboAntenna
    global folder
    global spinbox_BPLowcut

    CHANNEL_DICT["Impulse"] = comboImpulse.get()
    CHANNEL_DICT["Ferrite 1"] = comboHFCTMain.get()
    CHANNEL_DICT["Ferrite 2"] = comboHFCTReverse.get()
    CHANNEL_DICT["Antenna"] = comboAntenna.get()

    status_label.config(
        text="Searching for Measurement Folder...",
    )
    status_label.update()

    folder = get_folder()
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

    data_label.config(
        text=f"Data Loaded:\n{os.path.basename(folder)}\nHP Filter: {spinbox_BPLowcut.get()} MHz",
        foreground="green",
    )
    data_label.update()


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


def calculate_metadata():
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

    save_metadata()

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
    global root, visualize_btn, status_label, data_label
    global labelCH2Main, labelCH3Reverse, labelCH4Main
    global spinbox_timewindow_HFCT, spinbox_timewindow_antenna, spinbox_sampling_frequency
    global spinbox_mainPDinit, spinbox_mainPDend, spinbox_reversePDinit
    global ram_label, metadata_label
    global comboAntenna, comboHFCTMain, comboHFCTReverse, comboImpulse
    global logo_img  # Para evitar que el recolector de basura elimine la imagen
    global port_selection
    global spinbox_BPLowcut, spinbox_HPHighcut
    global tkinterAppDim

    root = tk.Tk()
    root.title("TRPD Analyzer & Viewer")
    root.geometry(tkinterAppDim)
    root.resizable(False, False)

    # Cargar y asignar el ícono de la aplicación
    if getattr(sys, "frozen", False):
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

    # Marco principal con grid compacto
    main_frame = ttk.Frame(root, padding="8")
    main_frame.pack(expand=True, fill=tk.BOTH)

    # --- Primera columna: Menú y estado ---
    left_frame = ttk.Frame(main_frame)
    left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), rowspan=2)

    ttk.Label(left_frame, text="Main Menu", font=("Arial", 10, "bold")).pack(
        pady=(0, 8)
    )

    # Botones principales
    menu_buttons = []
    for text, cmd in [
        ("1. Load Data (.csv)", load_app_data),
        ("2. Set Trigger Level", trigger_detection),
        ("3. Calculate TRPD Metadata", calculate_metadata),
        ("4. Save TRPD Metadata", save_metadata),
        ("5. Load TRPD Metadata", load_metadata),
        ("6. Visualize Data", visualize_data),
        ("7. Salir", exit_app),
    ]:
        btn = ttk.Button(left_frame, text=text, command=cmd)
        btn.pack(fill=tk.X, pady=2)
        btn.bind("<Enter>", lambda e, b=btn: b.config(cursor="hand2"))
        btn.bind("<Leave>", lambda e, b=btn: b.config(cursor=""))
        menu_buttons.append(btn)

    # --- DESACTIVADO: Vincular teclas numéricas a los botones del menú ---
    # def on_key_press(event):
    #     if event.char in "1234567":
    #         idx = int(event.char) - 1
    #         if 0 <= idx < len(menu_buttons):
    #             menu_buttons[idx].invoke()
    # root.bind("<Key>", on_key_press)
    # --- FIN DESACTIVADO ---

    ttk.Separator(left_frame, orient="horizontal").pack(fill=tk.X, pady=8)

    data_label = ttk.Label(left_frame, text="No Data Loaded", foreground="red")
    data_label.pack(pady=(2, 2))

    metadata_label = ttk.Label(
        left_frame, text="No Metadata Calculated", foreground="red"
    )
    metadata_label.pack(pady=(2, 2))

    ram_label = ttk.Label(
        left_frame,
        text="RAM Usage: 0.00 MB",
        font=("Arial", 8, "bold"),
        anchor="center",
    )
    ram_label.pack(pady=(2, 0))

    # --- Segunda columna: Parámetros principales ---
    param_frame = ttk.LabelFrame(
        main_frame, text="Trigger Detection Main Parameters", padding="8"
    )
    param_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10))

    def add_spinbox(label, from_, to, inc, default):
        ttk.Label(param_frame, text=label).pack(anchor="w", pady=(0, 1))
        sb = ttk.Spinbox(param_frame, from_=from_, to=to, increment=inc)
        sb.pack(fill=tk.X, pady=(0, 4))
        sb.set(default)
        return sb

    spinbox_timewindow_HFCT = add_spinbox("Time Window HFCT (us):", 0.01, 10, 0.1, 1)
    spinbox_timewindow_antenna = add_spinbox(
        "Time Window Antenna (us):", 0.01, 10, 0.1, 0.1
    )
    spinbox_sampling_frequency = add_spinbox(
        "Samplig Frequency (GHz):", 0.1, 10, 0.5, 5
    )
    spinbox_mainPDinit = add_spinbox("Main PD Time Init (us):", 0, 200, 5, 5)
    spinbox_mainPDend = add_spinbox("Main PD Time End (us):", 0, 200, 5, 50)
    spinbox_reversePDinit = add_spinbox("Reverse PD Time Init (us):", 0, 200, 5, 50)

    # --- Tercera columna: Trigger Settings ---
    trigger_frame = ttk.LabelFrame(main_frame, text="Trigger Settings", padding="8")
    trigger_frame.grid(row=0, column=2, sticky="nsew", padx=(0, 10))

    def add_trigger_label(frame, label, value, suffix):
        ttk.Label(frame, text=label, font=("Arial", 10, "bold")).pack(
            anchor="w", pady=(0, 2)
        )
        l = ttk.Label(frame, text=f"{value*1000} mV {suffix}", font=("Arial", 10))
        l.pack(fill=tk.X, pady=(0, 4))
        return l

    labelCH2Main = add_trigger_label(
        trigger_frame, "Main HFCT", TRIGGER_SETTINGS["mainHFCT"]["main"], "(Main)"
    )
    ttk.Separator(trigger_frame, orient="horizontal").pack(fill=tk.X, pady=4)
    labelCH3Reverse = add_trigger_label(
        trigger_frame,
        "Reverse HFCT",
        TRIGGER_SETTINGS["reverseHFCT"]["reverse"],
        "(Rev)",
    )
    ttk.Separator(trigger_frame, orient="horizontal").pack(fill=tk.X, pady=4)
    labelCH4Main = add_trigger_label(
        trigger_frame, "Antenna", TRIGGER_SETTINGS["antenna"]["main"], "(Main)"
    )

    # --- Cuarta columna: Asignación de canales ---
    channel_frame = ttk.LabelFrame(main_frame, text="Channel Assignment", padding="8")
    channel_frame.grid(row=0, column=3, sticky="nsew")

    ttk.Label(channel_frame, text="HFCTs Lowcut Freq. (MHz)").pack(
        anchor="w", pady=(0, 1)
    )
    spinbox_BPLowcut = ttk.Spinbox(channel_frame, from_=0.001, to=50, increment=1)
    spinbox_BPLowcut.pack(fill=tk.X, pady=(0, 4))
    spinbox_BPLowcut.set(5)

    ttk.Label(channel_frame, text="HFCTs Highcut Freq. (MHz)").pack(
        anchor="w", pady=(0, 1)
    )
    spinbox_HPHighcut = ttk.Spinbox(channel_frame, from_=0.001, to=50, increment=1)
    spinbox_HPHighcut.pack(fill=tk.X, pady=(0, 4))
    spinbox_HPHighcut.set(1000)

    def add_combo(label, values, default):
        ttk.Label(channel_frame, text=label).pack(anchor="w", pady=(0, 1))
        cb = ttk.Combobox(channel_frame, values=values)
        cb.pack(fill=tk.X, pady=(0, 4))
        cb.set(default)
        return cb

    comboImpulse = add_combo("Impulse", ["CH1", "CH2", "CH3", "CH4"], "CH1")
    comboHFCTMain = add_combo("Main HFCT", ["CH1", "CH2", "CH3", "CH4"], "CH2")
    comboHFCTReverse = add_combo("Reverse HFCT", ["CH1", "CH2", "CH3", "CH4"], "CH3")
    comboAntenna = add_combo("Antenna", ["CH1", "CH2", "CH3", "CH4"], "CH4")

    # --- Fila inferior: Estado y puerto ---
    bottom_frame = ttk.Frame(main_frame)
    bottom_frame.grid(row=1, column=1, columnspan=3, sticky="ew", pady=(10, 0))
    bottom_frame.columnconfigure(0, weight=3)
    bottom_frame.columnconfigure(1, weight=1)

    # Status label en la última fila, ocupando todas las columnas (columnspan=4)
    status_label = ttk.Label(
        main_frame, text="No data loaded", anchor="w", justify="left", padding="10"
    )
    status_label.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(10, 0))

    port_frame = ttk.Frame(bottom_frame)
    port_frame.grid(row=0, column=1, sticky="e", padx=(10, 0))
    ttk.Label(port_frame, text="Port Selection:", anchor="w", justify="left").grid(
        row=0, column=0, sticky="w", padx=(0, 5)
    )
    port_selection = ttk.Combobox(port_frame, values=availablePorts)
    port_selection.grid(row=0, column=1, sticky="w")
    port_selection.set(availablePorts[0])

    # Iniciar la actualización periódica de RAM
    update_ram_display()

    return root


def save_metadata():
    global df, impulse_ave_final, time1, folder
    global spinbox_timewindow_HFCT, spinbox_timewindow_antenna, spinbox_sampling_frequency
    global spinbox_mainPDinit, spinbox_mainPDend, spinbox_reversePDinit, spinbox_BPLowcut
    global comboImpulse, comboHFCTMain, comboHFCTReverse, comboAntenna
    global labelCH2Main, labelCH3Reverse, labelCH4Main
    global status_label
    try:
        impulse_ave_final_path = os.path.join(folder, "impulse_ave_final.npy")
        df_path = os.path.join(folder, "TRPD_metadata.pkl")
        time1_path = os.path.join(folder, "time1.npy")
        params_path = os.path.join(folder, "gui_params.json")

        # Guardar impulse_ave_final como npy (mantiene tipo y shape)

        status_label.config(
            text="Saving impulse reference... This may take a few seconds.",
        )
        status_label.update()
        np.save(impulse_ave_final_path, impulse_ave_final)

        status_label.config(text="Saving DataFrame... This may take a few seconds.")
        status_label.update()
        # Guardar df como pickle (mantiene DataFrame con tipos y estructura)
        df.to_pickle(df_path)

        status_label.config(
            text="Saving reference time... This may take a few seconds."
        )
        status_label.update()
        # Guardar time1 como npy
        np.save(time1_path, time1)

        # Guardar parámetros de la GUI
        gui_params = {}

        # Spinboxes
        gui_params["spinbox_timewindow_HFCT"] = spinbox_timewindow_HFCT.get()
        gui_params["spinbox_timewindow_antenna"] = spinbox_timewindow_antenna.get()
        gui_params["spinbox_sampling_frequency"] = spinbox_sampling_frequency.get()
        gui_params["spinbox_mainPDinit"] = spinbox_mainPDinit.get()
        gui_params["spinbox_mainPDend"] = spinbox_mainPDend.get()
        gui_params["spinbox_reversePDinit"] = spinbox_reversePDinit.get()
        gui_params["spinbox_BPLowcut"] = spinbox_BPLowcut.get()

        # Comboboxes
        gui_params["comboImpulse"] = comboImpulse.get()
        gui_params["comboHFCTMain"] = comboHFCTMain.get()
        gui_params["comboHFCTReverse"] = comboHFCTReverse.get()
        gui_params["comboAntenna"] = comboAntenna.get()

        # Trigger labels
        gui_params["labelCH2Main"] = labelCH2Main.cget("text")
        gui_params["labelCH3Reverse"] = labelCH3Reverse.cget("text")
        gui_params["labelCH4Main"] = labelCH4Main.cget("text")

        status_label.config(text="Saving parameters... This may take a few seconds.")
        status_label.update()

        # Guardar como JSON
        with open(params_path, "w", encoding="utf-8") as f:
            json.dump(gui_params, f, indent=2)

        status_label.config(text="Files saved successfully!")
        status_label.update()

        print(f"impulse_ave_final guardado en: {impulse_ave_final_path}")
        print(f"DF guardado en: {df_path}")
        print(f"time1 guardado en: {time1_path}")
        print(f"Parámetros GUI guardados en: {params_path}")
    except Exception as e:
        print(f"Error al guardar archivos: {e}")


def load_metadata():
    global df, impulse_ave_final, time1, scatter_traces, folder
    global spinbox_timewindow_HFCT, spinbox_timewindow_antenna, spinbox_sampling_frequency
    global spinbox_mainPDinit, spinbox_mainPDend, spinbox_reversePDinit, spinbox_BPLowcut
    global comboImpulse, comboHFCTMain, comboHFCTReverse, comboAntenna
    global labelCH2Main, labelCH3Reverse, labelCH4Main
    global status_label, metadata_label

    folder = get_folder()
    if folder is None:
        print("No folder selected.")
        return ""

    impulse_ave_final_path = os.path.join(folder, "impulse_ave_final.npy")
    df_path = os.path.join(folder, "TRPD_metadata.pkl")
    time1_path = os.path.join(folder, "time1.npy")
    params_path = os.path.join(folder, "gui_params.json")

    try:
        # Leer impulse_ave_final
        impulse_ave_final = np.load(impulse_ave_final_path)
        status_label.config(text="Impulse Ave Final loaded successfully.")
        status_label.update()
        print(f"impulse_ave_final cargado de: {impulse_ave_final_path}")
        # Leer df
        df = pd.read_pickle(df_path)
        status_label.config(text="DataFrame loaded successfully.")
        status_label.update()
        print(f"DF cargado de: {df_path}")
        # Leer time1
        time1 = np.load(time1_path)
        status_label.config(text="Reference Time loaded successfully.")

        scatter_traces = create_scatter_traces(df, impulse_ave_final, time1)

        status_label.config(text="Scatter traces created successfully.")
        status_label.update()
        print(f"time1 cargado de: {time1_path}")

        metadata_label.config(
            text=f"Metadata loaded:\n{os.path.basename(folder)}",
            foreground="green",
        )
        metadata_label.update()

        status_label.config(
            text="Metadata loaded successfully! Now you can visualize the data."
        )
        status_label.update()

        # Leer y aplicar parámetros GUI si existe el archivo
        if os.path.exists(params_path):
            with open(params_path, "r", encoding="utf-8") as f:
                gui_params = json.load(f)
            # Spinboxes
            spinbox_timewindow_HFCT.set(gui_params.get("spinbox_timewindow_HFCT", "1"))
            spinbox_timewindow_antenna.set(
                gui_params.get("spinbox_timewindow_antenna", "0.1")
            )
            spinbox_sampling_frequency.set(
                gui_params.get("spinbox_sampling_frequency", "5")
            )
            spinbox_mainPDinit.set(gui_params.get("spinbox_mainPDinit", "5"))
            spinbox_mainPDend.set(gui_params.get("spinbox_mainPDend", "50"))
            spinbox_reversePDinit.set(gui_params.get("spinbox_reversePDinit", "50"))
            spinbox_BPLowcut.set(gui_params.get("spinbox_BPLowcut", "5"))
            # Comboboxes
            comboImpulse.set(gui_params.get("comboImpulse", "CH1"))
            comboHFCTMain.set(gui_params.get("comboHFCTMain", "CH2"))
            comboHFCTReverse.set(gui_params.get("comboHFCTReverse", "CH3"))
            comboAntenna.set(gui_params.get("comboAntenna", "CH4"))
            # Trigger labels
            labelCH2Main.config(
                text=gui_params.get("labelCH2Main", labelCH2Main.cget("text"))
            )
            labelCH3Reverse.config(
                text=gui_params.get("labelCH3Reverse", labelCH3Reverse.cget("text"))
            )
            labelCH4Main.config(
                text=gui_params.get("labelCH4Main", labelCH4Main.cget("text"))
            )
            print(f"Parámetros GUI cargados de: {params_path}")
    except Exception as e:
        print(f"Error al cargar archivos: {e}")


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
