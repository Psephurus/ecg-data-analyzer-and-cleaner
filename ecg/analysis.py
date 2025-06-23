import logging
import numpy as np
import pandas as pd
from scipy.signal import find_peaks


def detect_r_peaks(ecg_signal: np.ndarray, fs: float):
    """
    检测 ECG 信号中的 R 波峰值并计算 R-R 间期（秒）

    参数:
        ecg_signal (np.ndarray): ECG 信号数组（1D）
        fs (float): 采样率 (Hz)

    返回:
        rr_intervals (np.ndarray): R-R 间期（单位：秒）
        r_peaks (np.ndarray): R 波峰值位置索引（单位：采样点）
    """

    peaks, _ = find_peaks(
        ecg_signal,
        height=np.percentile(ecg_signal, 90),
        distance=int(0.25 * fs),
        prominence=np.std(ecg_signal) * 0.8
    )

    # 计算 RR 间期（秒）
    rr_intervals = np.diff(peaks) / fs
    logging.info(f"Detected {len(peaks)} R peaks")
    return rr_intervals, peaks


def clean_rr_intervals(rr: np.ndarray, max_diff: float = 1.0,
                       min_rr: float = 0.0, max_rr: float = 1.0) -> np.ndarray:
    """清洗异常 R-R 间期（去除极端值及突变点）"""
    mask = (rr > min_rr) & (rr < max_rr)
    rr = rr[mask]
    valid_indices = [0]  # 保留首个点

    for i in range(1, len(rr)):
        if abs(rr[i] - rr[valid_indices[-1]]) <= max_diff:
            valid_indices.append(i)

    rr_cleaned = rr[valid_indices]
    logging.info(f"Cleaned RR intervals: {len(rr)} → {len(rr_cleaned)}")
    return rr_cleaned


def save_rr_intervals(rr_intervals: np.ndarray, filepath: str):
    """保存 R-R 间期到 CSV 文件。"""
    df_rr = pd.DataFrame({'RR_interval_s': rr_intervals})
    df_rr.to_csv(filepath, index=False)
    logging.info(f"R-R intervals saved to: {filepath}")


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    from loader import load_ecg_data
    from filters import bandpass_filter

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # === 参数 ===
    FILEPATH = "../data/20250604/dataLog-2025-6-2-12-31-6-1.5h.txt"
    FS = 500

    # === 读取与预处理 ===
    df = load_ecg_data(FILEPATH)
    ecg = df['ADC'].values[:FS * (65 - 45)]
    ecg_filtered = bandpass_filter(ecg, FS)

    # === 检测 R 波峰 ===
    rr_intervals, r_peaks = detect_r_peaks(ecg_filtered, fs=FS)

    # === 可视化 ===
    t = np.linspace(45, 65, len(ecg_filtered))

    plt.figure(figsize=(250, 4))
    plt.plot(t, ecg_filtered, label='Filtered ECG')
    plt.plot(t[r_peaks], ecg_filtered[r_peaks], 'ro', label='R Peaks')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
