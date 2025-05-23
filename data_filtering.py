import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from data_loader import load_ecg_data

def bandpass_filter(signal: np.ndarray, fs: float, lowcut: float = 1, highcut: float = 45.0, order: int = 4) -> np.ndarray:
    """
    对 ECG 信号进行带通滤波，默认频率范围为 0.5-45 Hz。

    参数:
        signal (np.ndarray): 原始 ECG 信号
        fs (float): 采样率 (Hz)
        lowcut (float): 低截止频率
        highcut (float): 高截止频率
        order (int): 滤波器阶数

    返回:
        np.ndarray: 滤波后的信号
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band') # type: ignore
    return filtfilt(b, a, signal)

if __name__ == "__main__":
    # === 参数设置 ===
    FILEPATH = "data/10 min.txt"
    FS = 500  # 采样率 Hz（估算值）

    # === 读取数据 ===
    df = load_ecg_data(FILEPATH)
    adc = df["ADC"].values
    time_segment = np.linspace(45, 60, int(FS * (60-45)))
    adc_segment = adc[:len(time_segment)]

    # === 滤波处理 ===
    adc_filtered = bandpass_filter(adc_segment, FS)

    # === 可视化（上下子图） ===
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(250, 4), sharex=True)

    ax1.plot(time_segment, adc_segment, color='steelblue')
    ax1.grid(True)

    ax2.plot(time_segment, adc_filtered, color='seagreen')
    ax2.grid(True)

    plt.tight_layout()
    plt.show()
