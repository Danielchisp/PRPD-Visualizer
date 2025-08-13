# %% LIBRARIES

# from tkinter import Tk, filedialog, messagebox, simpledialog
import os
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

# import dash
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# import plotly.graph_objects as go
# import scipy.signal
# from dash import ctx, dcc, html
# from dash.dependencies import Input, Output
from numpy.polynomial.polynomial import polyfit

# from IPython import get_ipython
# from PyQt5.QtWidgets import QApplication, QFileDialog
# from scipy import signal
from scipy.fft import fft
# from scipy.signal import hilbert, morlet, welch, butter, filtfilt
# from tqdm import tqdm
# from scipy.integrate import simps, trapz
import pickle
# from joblib import load

# %% FUNCTIONS

def best_fit_to_impulse_curve(pdx, pdy, impx, impy):
    # Encuentra los índices de tiempo correspondientes
    time_index = [np.argmin(abs(impx - x)**2) for x in pdx]

    # Extrae los valores de impy correspondientes a los puntos pdx
    impy_values = impy[time_index]

    # Calcula el factor de ajuste óptimo usando mínimos cuadrados
    k_adjust = np.sum(pdy * impy_values) / np.sum(impy_values**2)

    # Predicciones del modelo (y_hat = k * impy_values)
    y_pred = k_adjust * impy_values

    # Suma de cuadrados total (SST) y suma de cuadrados de los residuos (SSE)
    SST = np.sum((pdy - np.mean(pdy))**2)  # Variabilidad total
    SSE = np.sum((pdy - y_pred)**2)        # Variabilidad no explicada

    # Coeficiente de determinación R²
    R2 = 1 - (SSE / SST) if SST != 0 else 0  # Evita división por cero

    return [k_adjust, R2]

# %% IMPORT FILES

# Bushing cobre particulas | Nuevas Internas - copia | Metacrilato Superficiales - Volteado correctamente | Nuevas Internas 2 Vacuolas


subfoldersName = ['Bushing cobre particulas', 'Nuevas Internas - copia',
                  'Metacrilato Superficiales - Volteado correctamente', 'Nuevas Internas 2 Vacuolas']



folder = r'E:\Mediciones Impulso Reversas\nuevas\\' + subfoldersName[2]

numImpulsesTest = 50

# subfolders = ['T1', 'T2', 'T3', 'T4', 'T5']
subfolders = ['T1', 'T2', 'T3', 'T4']
# 
tensiones = pd.read_csv(os.path.join(folder, 'Tensiones.txt'), header=None)

impulses_per_voltage = []
time_impulses_per_voltage = []
main_discharges_ids_per_voltage = []
reverse_discharges_ids_per_voltage = []
antenna_ids_per_voltage = []
data_per_voltage = []
delays_per_voltage = []
antenna_ids = []

palette = ['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE']


for i in subfolders:

    impulse_ave = np.load(os.path.join(
        folder, i, 'impulse_ave_final' + '.npy'))
    time_impulse = np.load(os.path.join(folder, i, 'time1' + '.npy'))

    main_discharges_ids = pd.read_csv(os.path.join(folder, i, 'Main HFCT.csv'))
    reverse_discharges_ids = pd.read_csv(
        os.path.join(folder, i, 'Reverse HFCT.csv'))
    # antenna_ids = pd.read_csv(os.path.join(folder, i, 'Antenna.csv'))

    file_path = os.path.join(folder, i, 'TRPD_metadata.pkl')
    with open(file_path, 'rb') as f:  # 'rb' = read binary mode
        data = pickle.load(f)

    delays = pd.read_csv(os.path.join(folder, i, 'delays.csv'))

    # PER VOLTAGE DEFINITION

    impulses_per_voltage.append(impulse_ave)
    time_impulses_per_voltage.append(time_impulse)
    main_discharges_ids_per_voltage.append(main_discharges_ids)
    reverse_discharges_ids_per_voltage.append(reverse_discharges_ids)
    data_per_voltage.append(data)
    delays_per_voltage.append(delays)
    antenna_ids_per_voltage.append(antenna_ids)

# %% Análisis Métricas por Impulso

labelDict = {'Main PD Amplitude (V)': 'Main PD Amplitude (V)',
             'Main PD Time (us)': 'Main PD Time Lag (us)',
             'Reverse Npd': 'Reverse Npd',
             'Reverse PD Min Time (us)': 'Reverse PD Min Time (us)',
             'Reverse PD Average Amplitude (V)': 'Reverse PD Average Amplitude (V)'}

metricKeys = list(labelDict.keys())

mainReverseParams = {metricKeys[0]: [[] for _ in range(len(subfolders))],
                     metricKeys[1]: [[] for _ in range(len(subfolders))],
                     metricKeys[2]: [[] for _ in range(len(subfolders))],
                     metricKeys[3]: [[] for _ in range(len(subfolders))],
                     metricKeys[4]: [[] for _ in range(len(subfolders))],
                     }


for i in range(len(data_per_voltage)):
    main_time_all = []
    reverse_time_all = []

    for j in range(numImpulsesTest):

        amplitude_pd_main = np.array(data_per_voltage[i][
            (data_per_voltage[i]['id'].isin(main_discharges_ids_per_voltage[i]['id'])) &
            (data_per_voltage[i]['impulseNum'] == j)
        ]['Vpp'])

        amplitude_pd_reverse = np.array(data_per_voltage[i][
            (data_per_voltage[i]['id'].isin(reverse_discharges_ids_per_voltage[i]['id'])) &
            (data_per_voltage[i]['impulseNum'] == j)
        ]['Vpp'])

        time_pd_main = np.array(
            data_per_voltage[i][
                (data_per_voltage[i]['id'].isin(main_discharges_ids_per_voltage[i]['id'])) &
                (data_per_voltage[i]['impulseNum'] == j)
            ]['x'] - (delays_per_voltage[i]['t0_linear']*delays_per_voltage[0]['delay_us']/delays_per_voltage[0]['delay_samples'])[0]
        )

        time_pd_reverse = np.array(
            data_per_voltage[i][
                (data_per_voltage[i]['id'].isin(reverse_discharges_ids_per_voltage[i]['id'])) &
                (data_per_voltage[i]['impulseNum'] == j)
            ]['x'] - (delays_per_voltage[i]['t0_linear']*delays_per_voltage[0]['delay_us']/delays_per_voltage[0]['delay_samples'])[0]
        )

        if len(time_pd_main) and len(time_pd_reverse) != 0:

            mainReverseParams[metricKeys[0]][i].append(np.max(amplitude_pd_main))
            mainReverseParams[metricKeys[1]][i].append(np.max(time_pd_main))
            mainReverseParams[metricKeys[2]][i].append(len(time_pd_reverse))
            mainReverseParams[metricKeys[3]][i].append(np.min(time_pd_reverse))
            mainReverseParams[metricKeys[4]][i].append(np.max(amplitude_pd_reverse)) # CAMBIAR 


# %% LAST IMPULSES

metricSelected = list(mainReverseParams.keys())[2]

fig, ax = plt.subplots(dpi = 300)

for i in range(len(subfolders)):

    plt.plot(mainReverseParams[metricSelected][i], label = f'{tensiones[i][0]} kV')
    
plt.xlabel('# Impulse')
plt.ylabel(metricSelected)
plt.legend()

# %% MÉTRICAS POR IMPULSO       

# Función para calcular métricas de cluster (WCSS, distancia promedio, diámetro)
def calcular_metricas(puntos):
    if len(puntos) < 2:
        return 0.0, 0.0, 0.0, np.array([0, 0])  # Retorna centroide [0,0] para casos vacíos
    
    centroide = np.mean(puntos, axis=0)
    
    # WCSS (Within-Cluster Sum of Squares)
    wcss = np.sum((puntos - centroide)**2)
    
    # Distancia promedio intra-cluster (usando norma euclidiana)
    distancias = np.linalg.norm(puntos[:, np.newaxis] - puntos, axis=2)
    np.fill_diagonal(distancias, 0)  # Eliminar diagonal (distancia consigo mismo)
    dist_promedio = np.sum(distancias) / (len(puntos) * (len(puntos) - 1))
    
    # Diámetro (máxima distancia entre puntos del cluster)
    diametro = np.max(distancias)
    
    return wcss, dist_promedio, diametro, centroide

# Definición de claves (parámetros a comparar)
claves = list(mainReverseParams.keys())

# Generación de gráficos comparativos
for j in claves:
    for k in claves:
        if j == k:
            continue         
        
        fig, ax = plt.subplots(dpi=300)
        
        for i in range(len(subfolders)):
            # Prepara los puntos del cluster actual
            puntos = np.column_stack((mainReverseParams[j][i], mainReverseParams[k][i]))
            
            # Calcula métricas y centroide
            wcss, dist_prom, diametro, centroide = calcular_metricas(puntos)
            
            # Scatter plot de los puntos del cluster
            plt.scatter(
                puntos[:, 0], puntos[:, 1], 
                label=f'{tensiones[i][0]} kV',
                s=8, 
                color=palette[i], 
                alpha=0.5
            )
            
            # Scatter plot del centroide (con marcador más grande y borde negro)
            plt.scatter(
                centroide[0], centroide[1],
                s=50,                    # Tamaño grande
                color='black',         # Mismo color que el cluster
                edgecolor=palette[i],        # Borde negro
                linewidth=2,              # Grosor del borde
                marker='x'                # Forma de estrella
            )
        
        # Leyenda mejorada
        plt.legend(
            loc='best',
            frameon=False,
            fontsize=8,
            title="Voltage"
        )
        
        # Etiquetas y título
        plt.xlabel(labelDict[j], fontsize=10)
        plt.ylabel(labelDict[k], fontsize=10)
        plt.title(f"{labelDict[j]} vs {labelDict[k]}", fontsize=12, pad=15)
        plt.tight_layout()
        plt.show()
# %% Descargas Principales HFCT

gain = 1
signalPicked = 0

amplitude_pd_impulsenum_all = []
amplitude_pd_all = []
time_pd_all = []
fft_all = []
amp_error = []
time_error = []
range_main = []
num_discharges_main = []
vpp_mean_per_kv = []
min_main = []
amplitude_dependence_per_kv = []
R2_dependence_per_kv = []


fig, ax = plt.subplots(dpi=300)
temporalPlotExample = np.array(data_per_voltage[0][data_per_voltage[0]['id'].isin(
    main_discharges_ids_per_voltage[0]['id'])]['signal'])
timeExample = np.array(data_per_voltage[0][data_per_voltage[0]['id'].isin(
    main_discharges_ids_per_voltage[0]['id'])]['t'])
plt.plot(timeExample[signalPicked], temporalPlotExample[signalPicked], color=palette[0])
plt.xlabel('Time ($\mu s$)')
plt.ylabel('Voltage (V)')
plt.show()

fig, ax = plt.subplots(dpi=300)

for j in range(len(impulses_per_voltage)):

    time_pd = np.array(data_per_voltage[j][data_per_voltage[j]['id'].isin(main_discharges_ids_per_voltage[j]['id'])]['x'] - (
        delays_per_voltage[j]['t0_linear']*delays_per_voltage[0]['delay_us']/delays_per_voltage[0]['delay_samples'])[0])
    amplitude_pd = np.array(data_per_voltage[j][data_per_voltage[j]['id'].isin(
        main_discharges_ids_per_voltage[j]['id'])]['Vpp'])
    ampltiude_pd_impulsenum = np.array(data_per_voltage[j][data_per_voltage[j]['id'].isin(
        main_discharges_ids_per_voltage[j]['id'])]['impulseNum'])
    vpp_pd = data_per_voltage[j][data_per_voltage[j]['id'].isin(
        main_discharges_ids_per_voltage[j]['id'])]['Vpp']
    fft = data_per_voltage[j][data_per_voltage[j]['id'].isin(
        main_discharges_ids_per_voltage[j]['id'])]['fft_values']
    time_impulse = time_impulses_per_voltage[j] - (delays_per_voltage[j]['t0_linear']
                                                   * delays_per_voltage[0]['delay_us']/delays_per_voltage[0]['delay_samples'])[0]

    amplitude_dependence_per_kv.append(best_fit_to_impulse_curve(
        time_pd, amplitude_pd, time_impulse, impulses_per_voltage[j])[0])
    R2_dependence_per_kv.append(round(100*best_fit_to_impulse_curve(
        time_pd, amplitude_pd, time_impulse, impulses_per_voltage[j])[1], 3))

    amplitude_pd_impulsenum_all.append(ampltiude_pd_impulsenum)
    amplitude_pd_all.append(np.mean(amplitude_pd))
    amp_error.append(np.std(amplitude_pd))
    vpp_mean_per_kv.append(np.mean(vpp_pd))
    time_pd_all.append(np.mean(time_pd))
    min_main.append(np.min(time_pd))
    time_error.append(np.std(time_pd))
    range_main.append(max(time_pd) - min(time_pd))
    num_discharges_main.append(len(time_pd))
    fft_all.append(np.mean(fft))
    
    print(f'Mínimo Time Lag = {round(min(time_pd),2)} us y Máximo Time Lag = {round(max(time_pd),2)} us')

    plt.plot(time_impulse, impulses_per_voltage[j] *
             amplitude_dependence_per_kv[-1], alpha=1, color=palette[j])
    plt.scatter(time_pd, amplitude_pd, s=3, label=f'{tensiones[j][0]} kV', color=palette[j], alpha=1.0)

plt.scatter(time_pd_all, amplitude_pd_all, color='black', marker='x')
plt.xlim(-1, 5)
plt.xlabel('Time (us)')
plt.ylabel('PD Peak to Peak Voltage (V)')
plt.legend(loc='lower right')
plt.show()

fig, ax = plt.subplots(dpi=300)
plt.plot(tensiones.iloc[0], amplitude_dependence_per_kv,
         marker='o', linewidth=1.5, color=palette[0])
plt.xlabel('Voltage (kV)')
plt.ylabel('Calibration Factor')
plt.show()

fig, ax = plt.subplots(dpi=300)

# Primera gráfica (eje izquierdo - azul)
line1 = ax.plot(tensiones.loc[0], time_pd_all, marker='o', color=palette[0])[0]
ax.set_xlabel('Voltage (kV)')
ax.set_ylabel('Average Time of Occurence ($\mu$s)',
              color=palette[0])  # Color igual que la curva
ax.tick_params(axis='y', labelcolor=palette[0])  # Color de los ticks

# Segunda gráfica (eje derecho - rojo)
ax2 = ax.twinx()
line2 = ax2.plot(tensiones.loc[0], range_main, marker='o', color=palette[1])[0]
# Color igual que la curva
ax2.set_ylabel('Time Range ($\mu$s)', color=palette[1])
ax2.tick_params(axis='y', labelcolor=palette[1])  # Color de los ticks

plt.tight_layout()
plt.show()

fig, ax = plt.subplots(dpi=300)

# Primera gráfica (eje izquierdo - azul)
line1 = ax.plot(tensiones.loc[0], vpp_mean_per_kv,
                marker='o', color=palette[0])[0]
ax.set_xlabel('Voltage (kV)')
ax.set_ylabel('$V_{pp}$ (V)', color=palette[0])  # Color igual que la curva
ax.tick_params(axis='y', labelcolor=palette[0])  # Color de los ticks

# Segunda gráfica (eje derecho - rojo)
ax2 = ax.twinx()
line2 = ax2.plot(tensiones.loc[0], np.array(
    num_discharges_main)/numImpulsesTest, marker='o', color=palette[1])[0]
# Color igual que la curva
ax2.set_ylabel('$N_{PD}/Impulse$', color=palette[1])
ax2.tick_params(axis='y', labelcolor=palette[1])  # Color de los ticks

plt.tight_layout()
plt.show()

fig, ax = plt.subplots(dpi=300)

for j in range(len(fft_all)):
    plt.plot(fft_all[j], label=f'{str(tensiones[j][0])} kV', color=palette[j])

plt.xlim(0, 100)
plt.xlabel('Frequency (MHz)')
plt.ylabel('($V^{2}$)')
plt.legend()

# Crear eje de zoom (puedes ajustar posición y tamaño)
axins = ax.inset_axes([0.35, 0.2, 0.6, 0.3])

for j in range(len(fft_all)):
    axins.plot(fft_all[j], color=palette[j])

# Ajustar estos límites según la región que quieras ampliar
axins.set_xlim(20, 60)  # Ejemplo: zoom en frecuencia 20-30 MHz
axins.set_ylim(0, 3e-4)   # Ejemplo: ajustar según tus datos

# Opcional: añadir líneas de conexión o marcar la zona ampliada
ax.indicate_inset_zoom(axins, edgecolor="black")

plt.show()

# %% Descargas Principales Antenna

gain = 1

amplitude_pd_all = []
time_pd_all = []
fft_all = []
amp_error = []
time_error = []
range_main = []
num_discharges_main = []
vpp_mean_per_kv = []
min_main = []
amplitude_dependence_per_kv = []
R2_dependence_per_kv = []

palette = ['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE']

fig, ax = plt.subplots(dpi=300)
temporalPlotExample = np.array(data_per_voltage[0][data_per_voltage[0]['id'].isin(
    antenna_ids_per_voltage[0]['id'])]['signal'])
timeExample = np.array(data_per_voltage[0][data_per_voltage[0]['id'].isin(
    antenna_ids_per_voltage[0]['id'])]['t'])
plt.plot(timeExample[0], temporalPlotExample[0], color=palette[0])
plt.xlabel('Time ($\mu s$)')
plt.ylabel('Voltage (V)')
plt.show()

fig, ax = plt.subplots(dpi=300)

for j in range(len(impulses_per_voltage)):

    time_pd = np.array(data_per_voltage[j][data_per_voltage[j]['id'].isin(antenna_ids_per_voltage[j]['id'])]['x'] - (
        delays_per_voltage[j]['t0_linear']*delays_per_voltage[0]['delay_us']/delays_per_voltage[0]['delay_samples'])[0])
    amplitude_pd = np.array(data_per_voltage[j][data_per_voltage[j]['id'].isin(
        antenna_ids_per_voltage[j]['id'])]['y'])
    vpp_pd = data_per_voltage[j][data_per_voltage[j]['id'].isin(
        antenna_ids_per_voltage[j]['id'])]['Vpp']
    fft = data_per_voltage[j][data_per_voltage[j]['id'].isin(
        antenna_ids_per_voltage[j]['id'])]['fft_values']
    time_impulse = time_impulses_per_voltage[j] - (delays_per_voltage[j]['t0_linear']
                                                   * delays_per_voltage[0]['delay_us']/delays_per_voltage[0]['delay_samples'])[0]

    amplitude_dependence_per_kv.append(best_fit_to_impulse_curve(
        time_pd, amplitude_pd, time_impulse, impulses_per_voltage[j])[0])
    R2_dependence_per_kv.append(round(100*best_fit_to_impulse_curve(
        time_pd, amplitude_pd, time_impulse, impulses_per_voltage[j])[1], 3))
    amplitude_pd_all.append(np.mean(amplitude_pd))
    amp_error.append(np.std(amplitude_pd))
    vpp_mean_per_kv.append(np.mean(vpp_pd))
    time_pd_all.append(np.mean(time_pd))
    min_main.append(np.min(time_pd))
    time_error.append(np.std(time_pd))
    range_main.append(max(time_pd) - min(time_pd))
    num_discharges_main.append(len(time_pd))
    fft_all.append(np.mean(fft))

    plt.plot(time_impulse, impulses_per_voltage[j] *
             amplitude_dependence_per_kv[-1], alpha=1, color=palette[j])
    plt.scatter(time_pd, amplitude_pd, s=3, label=f'{str(tensiones[j][0])} kV', color=palette[j], alpha=1.0)

plt.scatter(time_pd_all, amplitude_pd_all, color='black', marker='x')
plt.xlim(-1, 20)
plt.xlabel('Time (us)')
plt.ylabel('PD Peak to Peak Voltage (V)')
plt.legend(loc='upper right')
plt.show()

fig, ax = plt.subplots(dpi=300)
plt.plot(tensiones.iloc[0], amplitude_dependence_per_kv,
         marker='o', linewidth=1.5, color=palette[0])
plt.xlabel('Voltage (kV)')
plt.ylabel('Calibration Factor')
plt.show()

fig, ax = plt.subplots(dpi=300)

# Primera gráfica (eje izquierdo - azul)
line1 = ax.plot(tensiones.loc[0], time_pd_all, marker='o', color=palette[0])[0]
ax.set_xlabel('Voltage (kV)')
ax.set_ylabel('Average Time of Occurence ($\mu$s)',
              color=palette[0])  # Color igual que la curva
ax.tick_params(axis='y', labelcolor=palette[0])  # Color de los ticks

# Segunda gráfica (eje derecho - rojo)
ax2 = ax.twinx()
line2 = ax2.plot(tensiones.loc[0], range_main, marker='o', color=palette[1])[0]
# Color igual que la curva
ax2.set_ylabel('Time Range ($\mu$s)', color=palette[1])
ax2.tick_params(axis='y', labelcolor=palette[1])  # Color de los ticks

plt.tight_layout()
plt.show()

fig, ax = plt.subplots(dpi=300)

# Primera gráfica (eje izquierdo - azul)
line1 = ax.plot(tensiones.loc[0], vpp_mean_per_kv,
                marker='o', color=palette[0])[0]
ax.set_xlabel('Voltage (kV)')
ax.set_ylabel('$V_{pp}$ (V)', color=palette[0])  # Color igual que la curva
ax.tick_params(axis='y', labelcolor=palette[0])  # Color de los ticks

# Segunda gráfica (eje derecho - rojo)
ax2 = ax.twinx()
line2 = ax2.plot(tensiones.loc[0], np.array(
    num_discharges_main)/numImpulsesTest, marker='o', color=palette[1])[0]
# Color igual que la curva
ax2.set_ylabel('$N_{PD}/Impulse$', color=palette[1])
ax2.tick_params(axis='y', labelcolor=palette[1])  # Color de los ticks

plt.tight_layout()
plt.show()

fig, ax = plt.subplots(dpi=300)

for j in range(len(fft_all)):
    plt.plot(fft_all[j], label=f'{str(tensiones[j][0])} kV', color=palette[j])

plt.xlim(0, 1000)
plt.xlabel('Frequency (MHz)')
plt.ylabel('($V^{2}$)')
plt.legend()
plt.show()

# %% Descargas Reversas
gain = 0.002

reverse_amplitude_pd_all = []
reverse_time_pd_all = []
reverse_fft_all = []
range_reverse = []
min_reverse = []
mean_reverse = []
num_reverse = []
vpp_reverse = []
fft_all_reverse = []


palette = ['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE']

fig, ax = plt.subplots(dpi=300)
temporalPlotExample = np.array(data_per_voltage[0][data_per_voltage[0]['id'].isin(
    reverse_discharges_ids_per_voltage[0]['id'])]['signal'])
timeExample = np.array(data_per_voltage[0][data_per_voltage[0]['id'].isin(
    reverse_discharges_ids_per_voltage[0]['id'])]['t'])
plt.plot(timeExample[0], temporalPlotExample[0], color=palette[0])
plt.xlabel('Time ($\mu s$)')
plt.ylabel('Voltage (V)')
plt.show()

fig, ax = plt.subplots(dpi=300)

for j in range(len(impulses_per_voltage)):

    amplitude_pd = data_per_voltage[j][data_per_voltage[j]['id'].isin(
        reverse_discharges_ids_per_voltage[j]['id'])]['y']
    reverse_amplitude_pd_all.append(np.mean(amplitude_pd))

    vpp_pd = data_per_voltage[j][data_per_voltage[j]['id'].isin(
        reverse_discharges_ids_per_voltage[j]['id'])]['Vpp']
    vpp_reverse.append(np.mean(vpp_pd*1000))

    time_pd = data_per_voltage[j][data_per_voltage[j]['id'].isin(
        reverse_discharges_ids_per_voltage[j]['id'])]['x'] + delays_per_voltage[j]['delay_us'][0]
    reverse_time_pd_all.append(np.mean(time_pd))

    min_reverse.append(np.min(time_pd))
    range_reverse.append(np.max(time_pd) - np.min(time_pd))
    mean_reverse.append(np.mean(amplitude_pd))
    num_reverse.append(len(amplitude_pd))
    
    print(f'Mínimo Time Lag = {round(min(time_pd),2)} us y Máximo Time Lag = {round(max(time_pd),2)} us')


    fft = data_per_voltage[j][data_per_voltage[j]['id'].isin(
        reverse_discharges_ids_per_voltage[j]['id'])]['fft_values']
    fft_all_reverse.append(np.mean(fft))

    plt.plot(time_impulses_per_voltage[j] + delays_per_voltage[j]['delay_us']
             [0], impulses_per_voltage[j]*gain, alpha=1, color=palette[j])
    plt.scatter(time_pd, amplitude_pd, s=3, label=f'{tensiones[j][0]} kV - Npd/imp: {round(num_reverse[-1]/50,0)}', color=palette[j])
    # plt.xlim(50, 200)

# plt.plot(reverse_time_pd_all, reverse_amplitude_pd_all, color = 'black', marker = 'x')
plt.xlabel('Time (us)')
plt.ylabel('PD Voltage (V)')
# plt.xlim(15,200)
plt.ylim(-0.04, 0.015)
plt.legend(fontsize=8, loc = 'lower left')

fig, ax = plt.subplots(dpi=300)

# Primera gráfica (eje izquierdo - azul)
line1 = ax.plot(tensiones.loc[0], min_reverse, marker='o', color=palette[0])[0]
ax.set_xlabel('Voltage (kV)')
# Color igual que la curva
ax.set_ylabel('Minimum Time ($\mu$s)', color=palette[0])
ax.tick_params(axis='y', labelcolor=palette[0])  # Color de los ticks

# Segunda gráfica (eje derecho - rojo)
ax2 = ax.twinx()
line2 = ax2.plot(tensiones.loc[0], range_reverse,
                 marker='o', color=palette[1])[0]
# Color igual que la curva
ax2.set_ylabel('Time Range ($\mu$s)', color=palette[1])
ax2.tick_params(axis='y', labelcolor=palette[1])  # Color de los ticks

plt.tight_layout()
plt.show()

fig, ax = plt.subplots(dpi=300)

# Primera gráfica (eje izquierdo - azul)
line1 = ax.plot(tensiones.loc[0], vpp_reverse, marker='o', color=palette[0])[0]
ax.set_xlabel('Voltage (kV)')
# Color igual que la curva
ax.set_ylabel('Peak to Peak Voltage (mV)', color=palette[0])
ax.tick_params(axis='y', labelcolor=palette[0])  # Color de los ticks

# Segunda gráfica (eje derecho - rojo)
ax2 = ax.twinx()
line2 = ax2.plot(tensiones.loc[0], np.array(
    num_reverse)/numImpulsesTest, marker='o', color=palette[1])[0]
# Color igual que la curva
ax2.set_ylabel('$N_{PD}/Impulse$', color=palette[1])
ax2.tick_params(axis='y', labelcolor=palette[1])  # Color de los ticks

plt.tight_layout()
plt.show()

fig, ax = plt.subplots(dpi=300)

for j in range(len(fft_all_reverse)):
    plt.plot(fft_all_reverse[j], label=f'{str(tensiones[j][0])} kV', color=palette[j])

plt.xlim(0, 100)
plt.xlabel('Frequency (MHz)')
plt.ylabel('($V^{2}$)')
plt.legend()

# Crear eje de zoom (puedes ajustar posición y tamaño)
axins = ax.inset_axes([0.25, 0.2, 0.7, 0.3])

for j in range(len(fft_all_reverse)):
    axins.plot(fft_all_reverse[j], color=palette[j])

# Ajustar estos límites según la región que quieras ampliar
axins.set_xlim(20, 60)  # Ejemplo: zoom en frecuencia 20-30 MHz
axins.set_ylim(0, 0.03e-6)   # Ejemplo: ajustar según tus datos

# Opcional: añadir líneas de conexión o marcar la zona ampliada
ax.indicate_inset_zoom(axins, edgecolor="black")

plt.show()

# %% REVERSAS RES TEMPORAL

max_time = 200

num_pd_per_frame = []
mean_pd_per_frame = []
frame_num = 50
time_ref = np.linspace(0, max_time, len(impulse_ave))
time_step_groups = np.linspace(0, max_time, frame_num)

frame_step = max_time/frame_num

for j in range(len(impulses_per_voltage)):

    pd_times = data_per_voltage[j][data_per_voltage[j]['id'].isin(
        reverse_discharges_ids_per_voltage[j]['id'])]['x'] + delays_per_voltage[j]['delay_us'][0]
    pd_vpps = data_per_voltage[j][data_per_voltage[j]['id'].isin(
        reverse_discharges_ids_per_voltage[j]['id'])]['Vpp']*1000

    for i in range(frame_num):
        aux_per_step = []
        for k in pd_times.index:
            if i > 0 and i < 200:
                if pd_times[k] > (i-1)*frame_step and pd_times[k] < (i+1)*frame_step:
                    aux_per_step.append(pd_vpps[k])

                    # AÑAAAAAAAAAADIR DELAAAAAAAAAAAAAYS!!!!!!!!!!!!!!!!!!
        if len(aux_per_step) == 0:
            mean_pd_per_frame.append(0)
            num_pd_per_frame.append(0)

        else:
            mean_pd_per_frame.append(np.mean(aux_per_step))
            num_pd_per_frame.append(len(aux_per_step))

vpp_mean_per_frame_per_kV = []
num_PD_per_frame_per_kV = []

for i in range(len(subfolders)):
    if i > 0:
        vpp_mean_per_frame_per_kV.append(
            mean_pd_per_frame[frame_num*(i):frame_num*(i+1)])
        num_PD_per_frame_per_kV.append(
            num_pd_per_frame[frame_num*(i):frame_num*(i+1)])

    else:
        vpp_mean_per_frame_per_kV.append(mean_pd_per_frame[0:frame_num])
        num_PD_per_frame_per_kV.append(num_pd_per_frame[0:frame_num])

# Para el gráfico de Average PD
fig, ax = plt.subplots(dpi=300)
for i in vpp_mean_per_frame_per_kV:
    color = palette[vpp_mean_per_frame_per_kV.index(i)]
    label = f'{str(tensiones[vpp_mean_per_frame_per_kV.index(i)][0])} kV'
    line, = plt.plot(time_step_groups, i, label=label, color=color)
    
    # Encontrar el máximo
    max_val = max(i)
    max_idx = np.argmax(i)
    max_time = time_step_groups[max_idx]
    
    # # Añadir marcador en cruz
    # plt.plot(max_time, max_val, 'x', color=color, markersize=10, markeredgewidth=2)
    
    # # Añadir texto con el valor
    # plt.text(max_time, max_val, f' {max_val:.1f} mV', 
    #          color=color, verticalalignment='bottom')

plt.xlim(18,200)
plt.xlabel('Time ($\mu s$)')
plt.ylabel('Average PD (mV)')
plt.legend()

# Para el gráfico de N_PD
fig, ax = plt.subplots(dpi=300)
for i in num_PD_per_frame_per_kV:
    color = palette[num_PD_per_frame_per_kV.index(i)]
    label = f'{str(tensiones[num_PD_per_frame_per_kV.index(i)][0])} kV'
    line, = plt.plot(time_step_groups, i, label=label, color=color)
    
    # Encontrar el máximo
    max_val = max(i)
    max_idx = np.argmax(i)
    max_time = time_step_groups[max_idx]
    
    # # Añadir marcador en cruz
    # plt.plot(max_time, max_val, 'x', color=color, markersize=10, markeredgewidth=2)
    
    # # Añadir texto con el valor
    # plt.text(max_time, max_val, f' {max_val:.0f}', 
    #          color=color, verticalalignment='bottom')

plt.xlim(18,200)
plt.xlabel('Time ($\mu s$)')
plt.ylabel('$N_{PD}$')
plt.legend()

# %% Comparative Analysis
fig, ax = plt.subplots(dpi=300)
plt.plot(time_pd_all, min_reverse)
plt.xlabel('Main Discharges Average Time ($\mu s$)')
plt.ylabel('First Reverse Discharge ($\mu s$)')
