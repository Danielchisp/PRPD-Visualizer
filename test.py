import matplotlib.pyplot as plt
import numpy as np

# Datos de ejemplo
x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_title("Drag the horizontal line to adjust the trigger. When done, press Enter.")
ax.set_xlabel("Time (us)")

# Crear línea horizontal inicial en y=0
hline = ax.axhline(
    y=0, color="r", linestyle="--", linewidth=2, picker=5
)  # 'picker' permite seleccionar la línea

# Variable para saber si la línea está siendo arrastrada
dragging = False


def on_pick(event):
    global dragging
    if event.artist == hline:
        dragging = True


def on_motion(event):
    if dragging and event.ydata is not None:  # Solo si el ratón está sobre el gráfico
        hline.set_ydata([event.ydata, event.ydata])  # Actualiza la posición y
        fig.canvas.draw()  # Redibuja el gráfico


def on_release(event):
    global dragging
    dragging = False


# Conectar eventos
fig.canvas.mpl_connect("pick_event", on_pick)
fig.canvas.mpl_connect("motion_notify_event", on_motion)
fig.canvas.mpl_connect("button_release_event", on_release)

plt.show()
