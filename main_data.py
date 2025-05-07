from utils import get_input_parameters
from data_processing import process_data, load_data
from tkinter import *
from tkinter import messagebox, simpledialog
from config import TRIGGER_SETTINGS
import matplotlib.pyplot as plt


# def adjust_trigger_interface(x, y, color):
#     fig, ax = plt.subplots()
#     ax.plot(x, y, color=color)
#     ax.set_title(
#         "Drag the horizontal line to adjust the trigger. When done, press Enter."
#     )

#     # Crear línea horizontal inicial en y=0
#     hline = ax.axhline(y=0, color="r", linestyle="--", linewidth=2, picker=5)

#     # Añadir texto para mostrar el valor actual
#     trigger_text = ax.text(
#         0.02,
#         0.95,
#         "0 V",
#         transform=ax.transAxes,
#         fontsize=12,
#         verticalalignment="top",
#         bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
#     )

#     # Usar una clase o atributos de fig para evitar variables globales
#     def on_pick(event):
#         if event.artist == hline:
#             fig.dragging = True  # Almacenar el estado en la figura

#     def on_motion(event):
#         if hasattr(fig, "dragging") and fig.dragging and event.ydata is not None:
#             current_y = event.ydata
#             hline.set_ydata([current_y, current_y])
#             # Actualizar el texto con el valor actual y unidades
#             trigger_text.set_text(f"{current_y:.4f} V")
#             fig.canvas.draw()

#     def on_release(event):
#         if hasattr(fig, "dragging"):
#             fig.dragging = False

#     def on_key_press(event):
#         if event.key == "enter":
#             fig.final_y = hline.get_ydata()[0]  # Guarda el valor actual de y
#             plt.close(fig)  # Cierra la ventana

#     # Conectar eventos
#     fig.canvas.mpl_connect("pick_event", on_pick)
#     fig.canvas.mpl_connect("motion_notify_event", on_motion)
#     fig.canvas.mpl_connect("button_release_event", on_release)
#     fig.canvas.mpl_connect("key_press_event", on_key_press)

#     plt.show()

#     return hline.get_ydata()[0]


# folder = get_input_parameters()

# ch1, ch2, ch3, ch4, time1, time2, time3, time4 = load_data(folder)

# IMPULSES_NUM = int(len(ch1.columns) / 2)

# enableWebViewer = False

# root = Tk()
# root.withdraw()

# while enableWebViewer == False:
#     messagebox.showinfo(
#         "Active Process",
#         "The peak detection trigger will be adjusted. A graph will be displayed for a specific signal.",
#     )

#     signalPicked = simpledialog.askinteger(
#         "Signal Selection",
#         f"Select the signal number. Maximum value is {IMPULSES_NUM - 1}:",
#         minvalue=0,
#         maxvalue=IMPULSES_NUM - 1,
#     )

#     signalNum = 2 * signalPicked + 1

#     signalCH1 = ch1[signalNum]
#     signalCH2 = ch2[signalNum]
#     signalCH3 = ch3[signalNum]
#     signalCH4 = ch4[signalNum]

#     TRIGGER_SETTINGS["CH2"]["main"] = adjust_trigger_interface(time2, signalCH2, "blue")
#     print(f"CH2 main trigger: {TRIGGER_SETTINGS['CH2']['main']} V")
#     TRIGGER_SETTINGS["CH3"]["reverse"] = adjust_trigger_interface(
#         time3, signalCH3, "green"
#     )
#     print(f"CH3 reverse trigger: {TRIGGER_SETTINGS['CH3']['reverse']} V")
#     TRIGGER_SETTINGS["CH4"]["main"] = adjust_trigger_interface(time4, signalCH4, "red")
#     print(f"CH4 main trigger: {TRIGGER_SETTINGS['CH4']['main']} V")

#     enableWebViewer = messagebox.askyesno(
#         "Trigger Setting", "Do you want to proceed with TRPD calculation?"
#     )

# df, scatter_traces, impulse_ave_final, time1 = process_data(
#     ch1, ch2, ch3, ch4, time1, time2, time3, time4
# )
