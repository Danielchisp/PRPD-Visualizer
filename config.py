# Los primeros 10 colores por defecto de Plotly:
MODERN_PLOTLY_COLORS = [
    "#636EFA",  # Azul claro intenso (el que ves en scatter)
    "#EF553B",  # Rojo anaranjado
    "#00CC96",  # Verde esmeralda
    "#AB63FA",  # Morado claro
    "#FFA15A",  # Naranja pastel
    "#19D3F3",  # Cyan brillante
    "#FF6692",  # Rosa
    "#B6E880",  # Verde lima
    "#FF97FF",  # Rosa neón
    "#FECB52",  # Amarillo dorado
]

# Configuración de canales
CHANNEL_DICT = {
    "Impulse": "CH1",
    "Ferrite 1": "CH2",
    "Ferrite 2": "CH3",
    "Antenna": "CH4",
}

# Configuración de triggers
TRIGGER_SETTINGS = {
    "CH2": {"main": 0.02, "reverse": 100},
    "CH3": {"main": 100, "reverse": 0.002},
    "CH4": {"main": 0.01, "reverse": 100},
}

window = 1500


# Configuración de ventanas
WINDOW_SETTINGS = {
    "window": window,
    "half_window": int(window / 2),
    "main_time_init": 1 * 5000,
    "main_time_fin": 40 * 5000,
    "reverse_time_init": 40 * 5000,
    "trigger_width": 1.5,
}

# Configuración de colores para los canales
CHANNEL_COLORS = {
    "CH2": "blue",  # MODERN_PLOTLY_COLORS[0],  # Azul (#1f77b4)
    "CH3": "green",  # MODERN_PLOTLY_COLORS[1],  # Naranjo (#ff7f0e)
    "CH4": "red",  # MODERN_PLOTLY_COLORS[2]   # Verde (#2ca02c)
}

# Límites FFT
FFT_LIMITS = {"CH2": 250e6, "CH3": 250e6, "CH4": 2000e6}

# Frecuencia de muestreo
FS = 5e9
