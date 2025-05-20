import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.signal import find_peaks, welch, resample
from tqdm import tqdm


from config import (
    CHANNEL_COLORS,
    FFT_LIMITS,
    TRIGGER_SETTINGS,
    WINDOW_SETTINGS,
    impulseDownsample,
)


def time_metrics(t: np.ndarray, s: np.ndarray) -> tuple[float, float]:
    E = np.sum(s**2)
    t0 = np.sum(t * s**2) / E
    T2 = np.sqrt(np.sum((t - t0) ** 2 * s**2) / E)
    return t0, T2


def W_eq_squared(f: np.ndarray, Pxx: np.ndarray) -> float:
    return np.sqrt(np.sum(f**2 * Pxx) / np.sum(Pxx))


def process_channel(channel_name, channel_cfg, impulsesNum):
    global WINDOW_SETTINGS
    signals_list = []

    for i in tqdm(range(impulsesNum), desc=f"Procesando {channel_name.upper()}"):
        signal_num = 2 * i + 1
        signal = channel_cfg["signal"][signal_num]

        for discharge_type, peaks in [
            ("Rise", channel_cfg["main_peaks"][i]),
            ("Tail", channel_cfg["reverse_peaks"][i]),
        ]:
            for peak_idx in peaks:

                if channel_name == "Antenna":

                    start = peak_idx - int(0.2 * WINDOW_SETTINGS["window_antenna"])
                    end = peak_idx + int(0.8 * WINDOW_SETTINGS["window_antenna"])
                    seg = signal[start:end]

                else:
                    start = peak_idx - int(0.2 * WINDOW_SETTINGS["window_HFCT"])
                    end = peak_idx + int(0.8 * WINDOW_SETTINGS["window_HFCT"])
                    seg = signal[start:end]

                f, Pxx = welch(
                    seg,
                    WINDOW_SETTINGS["fs"],
                    nperseg=min(5000, len(seg)),
                    scaling="spectrum",
                )

                t_local = np.arange(len(seg)) / WINDOW_SETTINGS["fs"]
                t0, T2 = time_metrics(t_local, seg)
                W2 = W_eq_squared(f, Pxx)

                signals_list.append(
                    {
                        "t": channel_cfg["time"][start:end],
                        "signal": seg,
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
                        "impulseNum": i,
                    }
                )

    print(f"Processed {len(signals_list)} signals for {channel_name.upper()}.")

    return signals_list


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

        signals += process_channel(ch_name, ch_cfg, impulsesNum)

    status_label.config(
        text="Processing completed. Generating scatter plot for all channels..."
    )
    status_label.update()

    df = pd.DataFrame(signals)
    df["id"] = range(len(df))
    df["group"] = df["type"] + " " + df["channel"]

    scatter_traces = []
    for group_name, group_data in df.groupby("group"):
        scatter_traces.append(
            go.Scattergl(
                x=group_data["x"],
                y=group_data["y"],
                mode="markers",
                marker=dict(
                    size=8,
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

    status_label.config(
        text="Processing completed. Calculating average impulse response..."
    )
    status_label.update()

    # impulses_list = [impulseMainData[2 * i + 1] for i in range(impulsesNum)]
    # impulse_ave_final = pd.DataFrame([sum(x) / len(x) for x in zip(*impulses_list)])[0]
    ganancia = max(df["amplitude"]) / max(impulse_ave_final)
    impulse_ave_final = [elemento * ganancia for elemento in impulse_ave_final]

    # impulse_ave_final = resample(impulse_ave_final, impulseDownsample)

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

    return df, scatter_traces, impulse_ave_final
