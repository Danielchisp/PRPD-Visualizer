import tkinter as tk
from tkinter import *
from tkinter import messagebox, simpledialog, ttk
import matplotlib.pyplot as plt
import os
from multiprocessing import Process, freeze_support


from app import create_dash_app
from utils import get_input_parameters
from data_processing import process_data, load_data

from config import TRIGGER_SETTINGS, WINDOW_SETTINGS

df = None
scatter_traces = None
impulse_ave_final = None
time1 = None
dash_process = None
root = None
ch1, ch2, ch3, ch4 = None, None, None, None
time1, time2, time3, time4 = None, None, None, None


def adjust_trigger_interface(x, y, color):
    fig, ax = plt.subplots()
    fig.canvas.manager.window.attributes(
        "-topmost", 1
    )  # Asegurar que la ventana esté en primer plano
    fig.canvas.manager.full_screen_toggle()  # Activar pantalla completa
    ax.plot(x, y, color=color)
    ax.set_title(
        "Drag the horizontal line to adjust the trigger. When done, press Enter."
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
        text=f"{round(TRIGGER_SETTINGS['CH2']['main']*1000,2)} mV (Main)"
    )
    labelCH2Reverse.config(
        text=f"{round(TRIGGER_SETTINGS['CH2']['reverse']*1000,2)} mV (Rev)"
    )
    labelCH3Main.config(
        text=f"{round(TRIGGER_SETTINGS['CH3']['main']*1000,2)} mV (Main)"
    )
    labelCH3Reverse.config(
        text=f"{round(TRIGGER_SETTINGS['CH3']['reverse']*1000,2)} mV (Rev)"
    )
    labelCH4Main.config(
        text=f"{round(TRIGGER_SETTINGS['CH4']['main']*1000,2)} mV (Main)"
    )
    labelCH4Reverse.config(
        text=f"{round(TRIGGER_SETTINGS['CH4']['reverse']*1000,2)} mV (Rev)"
    )


def load_app_data():
    global df, scatter_traces, impulse_ave_final, time1, status_label, folder_label
    global ch1, ch2, ch3, ch4, time1, time2, time3, time4

    status_label.config(
        text="Searching for Measurement Folder \nCH1.csv - CH2.csv - CH3.csv - CH4.csv",
    )
    status_label.update()

    folder = get_input_parameters()
    if folder is None:
        messagebox.showerror("Error", "No folder selected.")
        return

    status_label.config(text="Folder found!\nLoading data, this can take a while...")
    status_label.update()

    ch1, ch2, ch3, ch4, time1, time2, time3, time4 = load_data(folder)

    status_label.config(
        text="Data loaded successfully!\nNow you can set the trigger levels.",
    )
    status_label.update()

    folder_label.config(
        text=f"Folder Selected:\n{os.path.basename(folder)}",
        foreground="green",
    )
    folder_label.update()


def trigger_detection():
    global ch1, ch2, ch3, ch4, time1, time2, time3, time4
    global TRIGGER_SETTINGS, status_label
    IMPULSES_NUM = int(len(ch1.columns) / 2)

    triggerSettingLoop = False

    while triggerSettingLoop == False:
        messagebox.showinfo(
            "Process Notification",
            "The peak detection trigger adjustment process will now begin. A graph will be displayed for the selected signal.",
        )

        status_label.config(
            text="Peak Detection Trigger Adjustment\nSelect the signal to adjust"
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
            return

        signalNum = 2 * signalPicked + 1

        signalCH2 = ch2[signalNum]
        signalCH3 = ch3[signalNum]
        signalCH4 = ch4[signalNum]

        TRIGGER_SETTINGS["CH2"]["main"] = adjust_trigger_interface(
            time2, signalCH2, "blue"
        )
        print(f"CH2 main trigger: {TRIGGER_SETTINGS['CH2']['main']} V")
        TRIGGER_SETTINGS["CH3"]["reverse"] = adjust_trigger_interface(
            time3, signalCH3, "green"
        )
        print(f"CH3 reverse trigger: {TRIGGER_SETTINGS['CH3']['reverse']} V")
        TRIGGER_SETTINGS["CH4"]["main"] = adjust_trigger_interface(
            time4, signalCH4, "red"
        )
        print(f"CH4 main trigger: {TRIGGER_SETTINGS['CH4']['main']} V")

        response = messagebox.askokcancel(
            "Trigger Adjustment Confirmation",
            "Do you want to confirm the trigger adjustments?",
        )
        triggerSettingLoop = response

    update_trigger_labels()

    status_label.config(
        text="Trigger levels adjusted successfully!\nNow you can process the data."
    )

    # Confirmación para habilitar el visor web


def process_data_GUI():
    global df, scatter_traces, impulse_ave_final, time1, status_label
    global ch1, ch2, ch3, ch4, time1, time2, time3, time4

    status_label.config(
        text="Processing data...\nThis may take a few seconds.",
    )
    status_label.update()

    # Recoger los valores de los Spinbox
    get_spinbox_values()

    print("Window settings:", WINDOW_SETTINGS)

    # Procesar los datos
    df, scatter_traces, impulse_ave_final = process_data(
        ch1,
        ch2,
        ch3,
        ch4,
        time1,
        time2,
        time3,
        time4,
    )

    print("Data processed successfully!")
    # Actualizar la etiqueta de estado
    status_label.config(
        text="Metadata calculated successfully!\nNow you can visualize the data."
    )
    status_label.update()
    toggle_visualize_button(True)


def toggle_visualize_button(state):
    """Habilita/deshabilita el botón de visualización"""
    if "visualize_btn" in globals():
        new_state = tk.NORMAL if state else tk.DISABLED
        visualize_btn.config(state=new_state)


def run_dash_app(df, scatter_traces, time1, impulse_ave_final):

    create_dash_app(df, scatter_traces, time1, impulse_ave_final)


def visualize_data():
    global df, scatter_traces, time1, impulse_ave_final, dash_process, status_label

    status_label.config(
        text="Starting visualization...\nThis may take a few seconds.",
    )

    status_label.update()

    if dash_process and dash_process.is_alive():
        dash_process.terminate()
        dash_process.join()

    # Crear nuevo proceso y pasar los datos como argumentos
    dash_process = Process(
        target=run_dash_app,
        args=(df, scatter_traces, time1, impulse_ave_final),
    )
    dash_process.start()

    status_label.config(text="Visualizing data...")
    status_label.update()


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
    global labelCH2Main, labelCH2Reverse, labelCH3Main, labelCH3Reverse, labelCH4Main, labelCH4Reverse
    global spinbox_timewindow_HFCT, spinbox_timewindow_antenna, spinbox_sampling_frequency
    global spinbox_mainPDinit, spinbox_mainPDend, spinbox_reversePDinit

    root = tk.Tk()
    root.title("Main Menu")
    root.geometry("800x400")  # Ajustar el tamaño de la ventana
    root.resizable(False, False)

    # Marco principal
    main_frame = ttk.Frame(root)
    main_frame.pack(expand=True, fill=tk.BOTH)

    columna1 = ttk.Frame(main_frame, padding="5")
    columna1.grid(row=0, column=0, sticky="nsew")

    # Título
    ttk.Label(columna1, text="TRPD Analyzer & Viewer", font=("Arial", 10, "bold")).pack(
        pady=5
    )

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

    visualize_btn = tk.Button(
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
    status_label = ttk.Label(columna1, text="No data loaded")
    status_label.pack(pady=10)

    folder_label = ttk.Label(columna1, text="No Folder Selected", foreground="red")
    folder_label.pack(pady=10)

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

    ttk.Label(columna3, text="CH2", font=("Arial", 10, "bold")).pack(anchor="w")
    labelCH2Main = ttk.Label(
        columna3,
        text=f"{TRIGGER_SETTINGS['CH2']['main']*1000} mV (Main)",
        font=("Arial", 10),
    )
    labelCH2Main.pack(fill=tk.X, pady=5)

    labelCH2Reverse = ttk.Label(
        columna3,
        text=f"{TRIGGER_SETTINGS['CH2']['reverse']*1000} mV (Rev)",
        font=("Arial", 10),
    )
    labelCH2Reverse.pack(fill=tk.X, pady=5)

    ttk.Separator(columna3, orient="horizontal").pack(fill=tk.X, pady=10)

    ttk.Label(columna3, text="CH3", font=("Arial", 10, "bold")).pack(anchor="w")

    labelCH3Main = ttk.Label(
        columna3,
        text=f"{TRIGGER_SETTINGS['CH3']['main']*1000} mV (Main)",
        font=("Arial", 10),
    )
    labelCH3Main.pack(fill=tk.X, pady=5)
    # Separador horizontal

    labelCH3Reverse = ttk.Label(
        columna3,
        text=f"{TRIGGER_SETTINGS['CH3']['reverse']*1000} mV (Rev)",
        font=("Arial", 10),
    )
    labelCH3Reverse.pack(fill=tk.X, pady=5)

    ttk.Separator(columna3, orient="horizontal").pack(fill=tk.X, pady=10)

    ttk.Label(columna3, text="CH4", font=("Arial", 10, "bold")).pack(anchor="w")

    labelCH4Main = ttk.Label(
        columna3,
        text=f"{TRIGGER_SETTINGS['CH4']['main']*1000} mV (Main)",
        font=("Arial", 10),
    )
    labelCH4Main.pack(fill=tk.X, pady=5)

    labelCH4Reverse = ttk.Label(
        columna3,
        text=f"{TRIGGER_SETTINGS['CH4']['reverse']*1000} mV (Reverse)",
        font=("Arial", 10),
    )
    labelCH4Reverse.pack(fill=tk.X, pady=5)

    columna4 = ttk.Frame(main_frame, padding="5")
    columna4.grid(row=0, column=3, sticky="nsew")

    ttk.Label(columna4, text="Channel Assignment", font=("Arial", 10, "bold")).pack(
        pady=5
    )

    ttk.Label(columna4, text="Impulse").pack(anchor="w")

    combo = ttk.Combobox(columna4, values=["CH1", "CH2", "CH3", "CH4"])
    combo.pack(fill=tk.X, pady=5)
    combo.set("CH1")

    ttk.Label(columna4, text="Main HFCT").pack(anchor="w")

    combo = ttk.Combobox(columna4, values=["CH1", "CH2", "CH3", "CH4"])
    combo.pack(fill=tk.X, pady=5)
    combo.set("CH2")

    ttk.Label(columna4, text="Reverse HFCT").pack(anchor="w")

    combo = ttk.Combobox(columna4, values=["CH1", "CH2", "CH3", "CH4"])
    combo.pack(fill=tk.X, pady=5)
    combo.set("CH3")

    ttk.Label(columna4, text="Antenna").pack(anchor="w")
    combo = ttk.Combobox(columna4, values=["CH1", "CH2", "CH3", "CH4"])
    combo.pack(fill=tk.X, pady=5)
    combo.set("CH4")

    return root


def stop_dash():
    """Detiene la aplicación Dash"""
    os._exit(0)


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
    window = setup_gui()
    window.mainloop()


if __name__ == "__main__":
    freeze_support()  # Para compatibilidad con Windows
    main()
