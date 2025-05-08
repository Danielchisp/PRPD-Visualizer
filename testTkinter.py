import tkinter as tk
from tkinter import ttk


def mostrar_valores():
    resultado = f"""
    Valores seleccionados:
    - Texto: {entrada_texto.get()}
    - Número: {spinbox.get()}
    - Slider: {slider.get()}
    - Checkbox 1: {'Activado' if var_check1.get() else 'Desactivado'}
    - Checkbox 2: {'Activado' if var_check2.get() else 'Desactivado'}
    - Radio: {var_radio.get()}
    - Lista: {combo.get()}
    """
    etiqueta_resultado.config(text=resultado)


# Crear ventana principal
root = tk.Tk()
root.title("Interfaz con 3 Columnas")
root.geometry("800x600")

# Variables para controles
var_check1 = tk.BooleanVar()
var_check2 = tk.BooleanVar(value=True)
var_radio = tk.StringVar(value="Opción 1")

# Marco para organizar las 3 columnas
marco_principal = ttk.Frame(root, padding="10")
marco_principal.pack(fill=tk.BOTH, expand=True)

# Columna 1 - Controles Básicos
columna1 = ttk.Frame(marco_principal, padding="5")
columna1.grid(row=0, column=0, sticky="nsew")

ttk.Label(
    columna1, text="Peak Detector Main Parameters", font=("Arial", 10, "bold")
).pack(pady=5)

# Casilla de texto
ttk.Label(columna1, text="Entrada de texto:").pack(anchor="w")
entrada_texto = ttk.Entry(columna1)
entrada_texto.pack(fill=tk.X, pady=5)
entrada_texto.insert(0, "Texto de ejemplo")

# Spinbox (casilla numérica)
ttk.Label(columna1, text="Entrada numérica:").pack(anchor="w")
spinbox = ttk.Spinbox(columna1, from_=0, to=100, increment=5)
spinbox.pack(fill=tk.X, pady=5)
spinbox.set(50)

# Slider
ttk.Label(columna1, text="Control deslizante:").pack(anchor="w")
slider = ttk.Scale(columna1, from_=0, to=100, orient=tk.HORIZONTAL)
slider.pack(fill=tk.X, pady=5)
slider.set(75)

# Columna 2 - Botones y Opciones
columna2 = ttk.Frame(marco_principal, padding="5")
columna2.grid(row=0, column=1, sticky="nsew")

ttk.Label(columna2, text="Columna 2 - Botones", font=("Arial", 10, "bold")).pack(pady=5)

# Botones normales
ttk.Button(
    columna2, text="Botón Simple", command=lambda: print("Botón simple presionado")
).pack(fill=tk.X, pady=5)

ttk.Button(columna2, text="Botón con Estilo", style="Accent.TButton").pack(
    fill=tk.X, pady=5
)

# Checkbuttons
ttk.Label(columna2, text="Opciones:").pack(anchor="w")
ttk.Checkbutton(columna2, text="Opción 1", variable=var_check1).pack(anchor="w")
ttk.Checkbutton(columna2, text="Opción 2", variable=var_check2).pack(anchor="w")

# Radiobuttons
ttk.Label(columna2, text="Selección única:").pack(anchor="w")
ttk.Radiobutton(columna2, text="Opción A", variable=var_radio, value="Opción 1").pack(
    anchor="w"
)
ttk.Radiobutton(columna2, text="Opción B", variable=var_radio, value="Opción 2").pack(
    anchor="w"
)
ttk.Radiobutton(columna2, text="Opción C", variable=var_radio, value="Opción 3").pack(
    anchor="w"
)

# Columna 3 - Controles Adicionales
columna3 = ttk.Frame(marco_principal, padding="5")
columna3.grid(row=0, column=2, sticky="nsew")

ttk.Label(columna3, text="Columna 3 - Varios", font=("Arial", 10, "bold")).pack(pady=5)

# Combobox (lista desplegable)
ttk.Label(columna3, text="Lista desplegable:").pack(anchor="w")
combo = ttk.Combobox(columna3, values=["Item 1", "Item 2", "Item 3", "Item 4"])
combo.pack(fill=tk.X, pady=5)
combo.set("Item 1")

# Botón para mostrar valores
ttk.Button(columna3, text="Mostrar Valores", command=mostrar_valores).pack(
    fill=tk.X, pady=10
)

# Área de resultados
etiqueta_resultado = ttk.Label(
    columna3, text="", relief=tk.SUNKEN, padding="5", wraplength=200
)
etiqueta_resultado.pack(fill=tk.BOTH, expand=True, pady=10)

# Configurar el peso de las columnas
marco_principal.columnconfigure(0, weight=1)
marco_principal.columnconfigure(1, weight=1)
marco_principal.columnconfigure(2, weight=1)
marco_principal.rowconfigure(0, weight=1)

# Estilo para botón acentuado
style = ttk.Style()
style.configure("Accent.TButton", foreground="white", background="#0078d7")

# Ejecutar la aplicación
root.mainloop()
