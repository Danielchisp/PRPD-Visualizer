# Los primeros 10 colores por defecto de Plotly:
import matplotlib.pyplot as plt

MODERN_PLOTLY_COLORS = plt.rcParams["axes.prop_cycle"].by_key()["color"][:10]

availablePorts = [8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8010]

# Configuración de canales
CHANNEL_DICT = {
    "Impulse": "CH1",
    "Ferrite 1": "CH2",
    "Ferrite 2": "CH3",
    "Antenna": "CH4",
}

# Configuración de colores para los canales
CHANNEL_COLORS = {
    "CH2": "blue",  # MODERN_PLOTLY_COLORS[0],  # Azul (#1f77b4)
    "CH3": "green",  # MODERN_PLOTLY_COLORS[1],  # Naranjo (#ff7f0e)
    "CH4": "red",  # MODERN_PLOTLY_COLORS[2]   # Verde (#2ca02c)
}

# Límites FFT
FFT_LIMITS = {"CH2": 250e6, "CH3": 250e6, "CH4": 2000e6}

# Configuración de triggers
TRIGGER_SETTINGS = {
    "mainHFCT": {"main": 0.02, "reverse": 100},
    "reverseHFCT": {"main": 100, "reverse": 0.002},
    "antenna": {"main": 0.01, "reverse": 100},
}

# Configuración de ventanas
window_antenna = 500
window_HFCT = 5000

WINDOW_SETTINGS = {
    "window_antenna": window_antenna,
    "window_HFCT": window_HFCT,
    "window_antenna_vis": 5000,
    "window_HFCT_vis": 5000,
    "half_window_antenna": int(window_antenna / 2),
    "half_window_HFCT": int(window_HFCT / 2),
    "main_time_init": 1 * 5000,
    "main_time_fin": 40 * 5000,
    "reverse_time_init": 40 * 5000,
    "trigger_width": 1.5,
    "fs": 5e9,
}

samplesToMicros = 5000  # Previouly Known
impulseDownsample = 100000
tkinterAppDim = "750x450"

host = "127.0.0.1"  # Host address for the app
port = 8000  # Port for the app
