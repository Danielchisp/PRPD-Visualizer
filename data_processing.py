import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.signal import find_peaks, welch, resample
from tqdm import tqdm


from config import (
    CHANNEL_COLORS,
    CHANNEL_DICT,
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
    signals_list = []
    window_antenna = WINDOW_SETTINGS["window_antenna"]
    window_HFCT = WINDOW_SETTINGS["window_HFCT"]
    FS = WINDOW_SETTINGS["fs"]

    for i in tqdm(range(impulsesNum), desc=f"Procesando {channel_name.upper()}"):
        signal_num = 2 * i + 1
        signal = channel_cfg["signal"][signal_num]

        for discharge_type, peaks in [
            ("Main", channel_cfg["main_peaks"][i]),
            ("Reverse", channel_cfg["reverse_peaks"][i]),
        ]:
            for peak_idx in peaks:

                if channel_name == "CH4":

                    start = peak_idx - int(0.2 * window_antenna)
                    end = peak_idx + int(0.8 * window_antenna)
                    seg = signal[start:end]

                else:
                    start = peak_idx - int(0.2 * window_HFCT)
                    end = peak_idx + int(0.8 * window_HFCT)
                    seg = signal[start:end]

                f, Pxx = welch(seg, FS, nperseg=min(5000, len(seg)), scaling="spectrum")

                t_local = np.arange(len(seg)) / FS
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
                    }
                )

    print(f"Processed {len(signals_list)} signals for {channel_name.upper()}.")

    return signals_list


def load_data(folder):
    ch1 = pd.read_csv(
        folder + "\\" + CHANNEL_DICT["Impulse"] + ".csv", header=None, skiprows=25
    )
    ch2 = pd.read_csv(
        folder + "\\" + CHANNEL_DICT["Ferrite 1"] + ".csv", header=None, skiprows=25
    )
    ch3 = pd.read_csv(
        folder + "\\" + CHANNEL_DICT["Ferrite 2"] + ".csv", header=None, skiprows=25
    )
    ch4 = pd.read_csv(
        folder + "\\" + CHANNEL_DICT["Antenna"] + ".csv", header=None, skiprows=25
    )

    finalTime = int(len(ch1) / 5000)
    time1 = np.linspace(0, finalTime, len(ch1))
    time2 = np.linspace(0, finalTime, len(ch2))
    time3 = np.linspace(0, finalTime, len(ch3))
    time4 = np.linspace(0, finalTime, len(ch4))

    print("Data loaded successfully.")

    time1 = np.linspace(time1[0], time1[-1], impulseDownsample)

    return ch1, ch2, ch3, ch4, time1, time2, time3, time4


def process_data(ch1, ch2, ch3, ch4, time1, time2, time3, time4):
    impulsesNum = int(len(ch1.columns) / 2)

    mainDischargesCH2 = []
    mainDischargesCH3 = []
    mainDischargesCH4 = []
    reverseDischargesCH2 = []
    reverseDischargesCH3 = []
    reverseDischargesCH4 = []

    CHANNELS = {
        "CH2": {
            "signal": ch2,
            "time": time2,
            "main_peaks": mainDischargesCH2,
            "reverse_peaks": reverseDischargesCH2,
            "trigger": TRIGGER_SETTINGS["CH2"]["main"],
            "fft_lim": FFT_LIMITS["CH2"],
            "color": CHANNEL_COLORS["CH2"],
        },
        "CH3": {
            "signal": ch3,
            "time": time3,
            "main_peaks": mainDischargesCH3,
            "reverse_peaks": reverseDischargesCH3,
            "trigger": TRIGGER_SETTINGS["CH3"]["reverse"],
            "fft_lim": FFT_LIMITS["CH3"],
            "color": CHANNEL_COLORS["CH3"],
        },
        "CH4": {
            "signal": ch4,
            "time": time4,
            "main_peaks": mainDischargesCH4,
            "reverse_peaks": reverseDischargesCH4,
            "trigger": TRIGGER_SETTINGS["CH4"]["main"],
            "fft_lim": FFT_LIMITS["CH4"],
            "color": CHANNEL_COLORS["CH4"],
        },
    }

    for i in tqdm(range(impulsesNum)):
        signalNum = 2 * i + 1

        for ch_name, ch_data in CHANNELS.items():
            signal = ch_data["signal"][signalNum]

            if ch_name == "CH4":
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
        signals += process_channel(ch_name, ch_cfg, impulsesNum)

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
                    ),
                    axis=-1,
                ),
                hovertemplate="<b>Time:</b> %{customdata[0]:.2f} us<br>"
                + "<b>Amplitude:</b> %{y:.2f} V<br>"
                + "<b>Type:</b> %{customdata[1]}<br>"
                + "<b>Channel:</b> %{customdata[2]}<br>"
                + "<b>ID:</b> %{customdata[3]}<extra></extra>",
                name=group_name,
            )
        )

    impulses_list = [ch1[2 * i + 1] for i in range(impulsesNum)]
    impulse_ave_final = pd.DataFrame([sum(x) / len(x) for x in zip(*impulses_list)])[0]
    ganancia = max(df["amplitude"]) / max(impulse_ave_final)
    impulse_ave_final = [elemento * ganancia for elemento in impulse_ave_final]

    impulse_ave_final = resample(impulse_ave_final, impulseDownsample)

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
