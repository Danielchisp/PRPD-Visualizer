import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.signal import find_peaks, welch
from tqdm import tqdm


from config import (
    CHANNEL_COLORS,
    FFT_LIMITS,
    TRIGGER_SETTINGS,
    WINDOW_SETTINGS,
)

from utils import calculate_time_corrections


def time_metrics(t: np.ndarray, s: np.ndarray) -> tuple[float, float]:
    E = np.sum(s**2)
    t0 = np.sum(t * s**2) / E
    T2 = np.sqrt(np.sum((t - t0) ** 2 * s**2) / E)
    return t0, T2, E


def W_eq_squared(f: np.ndarray, Pxx: np.ndarray) -> float:
    return np.sqrt(np.sum(f**2 * Pxx) / np.sum(Pxx))


def process_channel(channel_name, channel_cfg, impulsesNum, time_corrections):
    global WINDOW_SETTINGS
    metadataDict = []

    for i in tqdm(range(impulsesNum), desc=f"Procesando {channel_name.upper()}"):
        signal_num = 2 * i + 1
        signal = channel_cfg["signal"][signal_num]

        for discharge_type, peaks in [
            ("Rise", channel_cfg["main_peaks"][i]),
            ("Tail", channel_cfg["reverse_peaks"][i]),
        ]:
            for peak_idx in peaks:

                if channel_name == "Antenna":

                    start = peak_idx - int(0.2 * WINDOW_SETTINGS["window_antenna_vis"])
                    end = peak_idx + int(0.8 * WINDOW_SETTINGS["window_antenna_vis"])
                    signalPicked = signal[start:end]

                else:
                    start = peak_idx - int(0.2 * WINDOW_SETTINGS["window_HFCT_vis"])
                    end = peak_idx + int(0.8 * WINDOW_SETTINGS["window_HFCT_vis"])
                    signalPicked = signal[start:end]

                f, Pxx = welch(
                    signalPicked,
                    WINDOW_SETTINGS["fs"],
                    nperseg=min(5000, len(signalPicked)),
                    scaling="spectrum",
                )

                t_local = np.arange(len(signalPicked)) / WINDOW_SETTINGS["fs"]
                t0, T2, Energy = time_metrics(t_local, signalPicked)
                W2 = W_eq_squared(f, Pxx)
                Qapp = min(np.cumsum(signalPicked))
                Vpp = max(signalPicked) + abs(min(signalPicked))

                metadataDict.append(
                    {
                        "t": channel_cfg["time"][start:end],
                        "signal": signalPicked,
                        "fft_values": Pxx,
                        "freqs": f,
                        "amplitude": signal[peak_idx],
                        "time": channel_cfg["time"][peak_idx],
                        "x": channel_cfg["time"][peak_idx],
                        "y": signal[peak_idx],
                        "type": discharge_type,
                        "channel": channel_name,
                        "trigger": channel_cfg["trigger"],
                        "color": channel_cfg["color"],
                        "fft_lim": channel_cfg["fft_lim"],
                        "t0": t0,
                        "T2": T2,
                        "W2": W2,
                        "Qapp": Qapp,
                        "Vpp": Vpp,
                        "Energy": Energy,
                        "impulseNum": i,
                    }
                )

    print(f"Processed {len(metadataDict)} signals for {channel_name.upper()}.")

    return metadataDict


def process_data(
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
):

    time_corrections = calculate_time_corrections(impulseMainData)
    impulsesNum = int(len(impulseMainData.columns) / 2)

    mainDischargesCH2 = []
    mainDischargesCH3 = []
    mainDischargesCH4 = []
    reverseDischargesCH2 = []
    reverseDischargesCH3 = []
    reverseDischargesCH4 = []

    CHANNELS = {
        "Main HFCT": {
            "signal": mainHFCTMainData,
            "time": time2,
            "main_peaks": mainDischargesCH2,
            "reverse_peaks": reverseDischargesCH2,
            "trigger": TRIGGER_SETTINGS["mainHFCT"]["main"],
            "fft_lim": FFT_LIMITS["CH2"],
            "color": CHANNEL_COLORS["CH2"],
        },
        "Reverse HFCT": {
            "signal": reverseHFCTMainData,
            "time": time3,
            "main_peaks": mainDischargesCH3,
            "reverse_peaks": reverseDischargesCH3,
            "trigger": TRIGGER_SETTINGS["reverseHFCT"]["reverse"],
            "fft_lim": FFT_LIMITS["CH3"],
            "color": CHANNEL_COLORS["CH3"],
        },
        "Antenna": {
            "signal": antennaMainData,
            "time": time4,
            "main_peaks": mainDischargesCH4,
            "reverse_peaks": reverseDischargesCH4,
            "trigger": TRIGGER_SETTINGS["antenna"]["main"],
            "fft_lim": FFT_LIMITS["CH4"],
            "color": CHANNEL_COLORS["CH4"],
        },
    }

    for i in tqdm(range(impulsesNum)):
        signalNum = 2 * i + 1

        for ch_name, ch_data in CHANNELS.items():
            signal = ch_data["signal"][signalNum]

            if ch_name == "Antenna":

                main_peaks, _ = find_peaks(
                    signal[
                        WINDOW_SETTINGS["main_time_init"] : WINDOW_SETTINGS[
                            "main_time_fin"
                        ]
                    ],
                    height=ch_data["trigger"],
                    distance=WINDOW_SETTINGS["window_antenna"],
                )
                reverse_peaks, _ = find_peaks(
                    signal[WINDOW_SETTINGS["reverse_time_init"] : -5000],
                    height=ch_data["trigger"],
                    distance=WINDOW_SETTINGS["window_antenna"],
                )
            else:

                main_peaks, _ = find_peaks(
                    signal[
                        WINDOW_SETTINGS["main_time_init"] : WINDOW_SETTINGS[
                            "main_time_fin"
                        ]
                    ],
                    height=ch_data["trigger"],
                    distance=WINDOW_SETTINGS["window_HFCT"],
                )
                reverse_peaks, _ = find_peaks(
                    -signal[WINDOW_SETTINGS["reverse_time_init"] : -5000],
                    height=ch_data["trigger"],
                    distance=WINDOW_SETTINGS["window_HFCT"],
                )

            ch_data["main_peaks"].append(main_peaks + WINDOW_SETTINGS["main_time_init"])
            ch_data["reverse_peaks"].append(
                reverse_peaks + WINDOW_SETTINGS["reverse_time_init"]
            )

    signals = []

    for ch_name, ch_cfg in CHANNELS.items():
        status_label.config(text=f"Processing {ch_name.upper()}...")
        status_label.update()

        signals += process_channel(ch_name, ch_cfg, impulsesNum, time_corrections)

    status_label.config(
        text="Processing completed. Generating scatter plot for all channels..."
    )
    status_label.update()

    df = pd.DataFrame(signals)
    df["id"] = range(len(df))
    df["group"] = df["type"] + " " + df["channel"]

    ganancia = max(df["amplitude"]) / max(impulse_ave_final)
    impulse_ave_final = [elemento * ganancia for elemento in impulse_ave_final]

    scatter_traces = create_scatter_traces(df, impulse_ave_final, time1)

    return df, scatter_traces, impulse_ave_final


def create_scatter_traces(df, impulse_ave_final, time1):
    scatter_traces = []
    for group_name, group_data in df.groupby("group"):
        scatter_traces.append(
            go.Scattergl(
                x=group_data["x"],
                y=group_data["y"],
                mode="markers",
                marker=dict(
                    size=4,
                    color=group_data["color"],
                ),
                customdata=np.stack(
                    (
                        group_data["time"],
                        group_data["type"],
                        group_data["channel"],
                        group_data["id"],
                        group_data["impulseNum"],
                    ),
                    axis=-1,
                ),
                hovertemplate="<b>Time:</b> %{customdata[0]:.2f} us<br>"
                + "<b>Amplitude:</b> %{y:.2f} V<br>"
                + "<b>Type:</b> %{customdata[1]}<br>"
                + "<b>Impulse N°:</b> %{customdata[4]}<br>"
                + "<b>Channel:</b> %{customdata[2]}<br>"
                + "<b>ID:</b> %{customdata[3]}<extra></extra>",
                name=group_name,
            )
        )

    scatter_traces.append(
        go.Scatter(
            x=time1,
            y=impulse_ave_final,
            mode="lines",
            line=dict(color="black", width=2.5),
            name="Impulse",
            hoverinfo="none",
        )
    )
    return scatter_traces
