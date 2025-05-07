import tkinter as tk
from tkinter import *
from tkinter import messagebox, simpledialog, ttk
import matplotlib.pyplot as plt
import os
import threading

from app import create_dash_app
from utils import get_input_parameters
from data_processing import process_data, load_data

from config import TRIGGER_SETTINGS, FFT_LIMITS

df = None
scatter_traces = None
impulse_ave_final = None
time1 = None
dash_thread = None
root = None


def adjust_trigger_interface(x, y, color):
    fig, ax = plt.subplots()
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


def load_app_data():
    global df, scatter_traces, impulse_ave_final, time1, status_label

    folder = get_input_parameters()

    ch1, ch2, ch3, ch4, time1, time2, time3, time4 = load_data(folder)

    IMPULSES_NUM = int(len(ch1.columns) / 2)

    enableWebViewer = False

    while enableWebViewer == False:
        messagebox.showinfo(
            "Active Process",
            "The peak detection trigger will be adjusted. A graph will be displayed for a specific signal.",
        )

        signalPicked = simpledialog.askinteger(
            "Signal Selection",
            f"Select the signal number. Maximum value is {IMPULSES_NUM - 1}:",
            minvalue=0,
            maxvalue=IMPULSES_NUM - 1,
        )

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

        enableWebViewer = messagebox.askyesno(
            "Trigger Setting", "Do you want to proceed with TRPD calculation?"
        )

    df, scatter_traces, impulse_ave_final, time1 = process_data(
        ch1, ch2, ch3, ch4, time1, time2, time3, time4
    )
    # Desbloquear el botón de visualización
    visualize_btn.config(state=tk.NORMAL)
    status_label.config(text="Data loaded succesfully!", fg="green")


def toggle_visualize_button(state):
    """Habilita/deshabilita el botón de visualización"""
    if "visualize_btn" in globals():
        new_state = tk.NORMAL if state else tk.DISABLED
        visualize_btn.config(state=new_state)


def run_dash_app():
    create_dash_app(df, scatter_traces, time1, impulse_ave_final)


def visualize_data():
    global df, scatter_traces, dash_thread, status_label
    # Crear un hilo para ejecutar Dash
    dash_thread = threading.Thread(target=run_dash_app, daemon=True)
    dash_thread.start()

    # Verificar el estado del hilo de Dash
    check_dash_thread()

    status_label.config(text="Visualizing data...", fg="blue")


def setup_gui():
    """Configura la interfaz gráfica de Tkinter"""
    global root, visualize_btn, status_label

    root = tk.Tk()
    root.title("Main Menu")
    root.geometry("400x400")  # Ajustar el tamaño de la ventana
    root.resizable(False, False)

    # Marco principal
    main_frame = tk.Frame(root, padx=20, pady=20)
    main_frame.pack(expand=True, fill=tk.BOTH)

    # Título
    tk.Label(main_frame, text="TRPD Analyzer & Viewer", font=("Arial", 16)).pack(
        pady=10
    )

    # Botones
    tk.Button(
        main_frame,
        text="1. Load Data (.CSV)",
        command=load_app_data,  # Llama directamente a load_app_data
        width=20,
        height=2,
    ).pack(pady=5)

    visualize_btn = tk.Button(
        main_frame,
        text="2. Visualize Data",
        command=visualize_data,
        width=20,
        height=2,
        state=tk.DISABLED,
    )
    visualize_btn.pack(pady=5)

    tk.Button(main_frame, text="3. Salir", command=root.quit, width=20, height=2).pack(
        pady=5
    )

    # Etiqueta de estado
    status_label = tk.Label(main_frame, text="No data loaded", fg="red")
    status_label.pack(pady=10)

    return root


def stop_dash():
    """Detiene la aplicación Dash"""
    os._exit(0)


def check_dash_thread():
    """Verifica si el hilo de Dash sigue activo"""
    global dash_thread

    if dash_thread.is_alive():
        root.after(100, check_dash_thread)
    else:
        toggle_visualize_button(True)


def main():
    """Función principal"""
    window = setup_gui()
    window.mainloop()


if __name__ == "__main__":
    main()
