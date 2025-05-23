import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

def detect_r_peaks(ecg_signal: np.ndarray, fs: float):
    """
    检测 ECG 信号中的 R 波峰值并计算 R-R 间期（秒）

    参数:
        ecg_signal (np.ndarray): ECG 信号数组（1D）
        fs (float): 采样率 (Hz)
        method (str): 可选方法 ['scipy', 'heartpy', 'biosppy']

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
    return rr_intervals, peaks

if __name__ == "__main__":
    from data_loader import load_ecg_data
    from data_filtering import bandpass_filter

    # === 参数 ===
    FILEPATH = "data/10 min.txt"
    FS = 500

    # === 读取与预处理 ===
    df = load_ecg_data(FILEPATH)
    ecg = df['ADC'].values[:FS * (65-45)]
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

    # === 打印结果 ===
    print(f"R-R intervals (s): {np.round(rr_intervals, 3)}")
    print(f"Number of R peaks: {len(r_peaks)}")
