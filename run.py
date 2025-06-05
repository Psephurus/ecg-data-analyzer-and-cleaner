import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_loader import load_ecg_data
from data_filtering import bandpass_filter
from find_peaks import detect_r_peaks


def save_rr_intervals(rr_intervals: np.ndarray, filepath: str):
    """保存 R-R 间期到 CSV 文件。"""
    df_rr = pd.DataFrame({'RR_interval_s': rr_intervals})
    df_rr.to_csv(filepath, index=False)
    print(f"[INFO] R-R intervals saved to: {filepath}")


def plot_ecg_with_peaks(time: np.ndarray, ecg: np.ndarray, r_peaks: np.ndarray, output_path: str):
    """绘制带有 R 波峰值的 ECG 图。"""
    plt.figure(figsize=(250, 4))
    plt.plot(time, ecg, linewidth=0.8)
    plt.scatter(time[r_peaks], ecg[r_peaks], color='red', s=10)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=600)
    print(f"[INFO] ECG plot with R peaks saved to: {output_path}")
    plt.close()


def clean_rr_intervals(rr: np.ndarray, max_diff: float = 0.1,
                       min_rr: float = 0.0, max_rr: float = 1.0) -> np.ndarray:
    """清洗异常 R-R 间期（去除极端值及突变点）"""
    mask = (rr > min_rr) & (rr < max_rr)
    rr = rr[mask]
    valid_indices = [0]  # 保留首个点

    for i in range(1, len(rr)):
        if abs(rr[i] - rr[valid_indices[-1]]) <= max_diff:
            valid_indices.append(i)

    rr_cleaned = rr[valid_indices]
    print(f"[INFO] Cleaned RR intervals based on ΔRR: {len(rr)} → {len(rr_cleaned)}")
    return rr_cleaned


def plot_poincare(rr_intervals: np.ndarray, output_path: str):
    """
    绘制庞加莱散点图（RR_n vs RR_n+1）

    参数:
        rr_intervals (np.ndarray): 清洗后的 R-R 间期
        output_path (str): 输出图像路径
    """
    rr_n = rr_intervals[:-1]
    rr_n1 = rr_intervals[1:]

    plt.figure(figsize=(6, 6))
    plt.scatter(rr_n, rr_n1, alpha=0.5, s=10)
    plt.title("Poincaré Plot")
    plt.xlabel("RR(n) (s)")
    plt.ylabel("RR(n+1) (s)")
    plt.grid(True)
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"[INFO] Poincaré plot saved to: {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="ECG R-peak detection and RR analysis")
    parser.add_argument("filepath", type=str, nargs="?", default="data/10 min.txt", help="Path to ECG txt file")
    parser.add_argument("--fs", type=int, default=500, help="Sampling rate (Hz)")
    parser.add_argument("--max-diff", type=float, default=0.3,
                        help="Maximum allowed difference between adjacent RR intervals (in seconds)")
    parser.add_argument("--min-rr", type=float, default=0.0, help="Minimum allowed RR interval (in seconds)")
    args = parser.parse_args()

    # === 输出路径设置 ===
    out_prefix = args.filepath.replace("/", "_").replace("\\", "_").replace(".txt", "").split("_")[-1]
    rr_csv_path = f"out/rr_intervals_{out_prefix}.csv"
    # ecg_plot_path = f"out/ecg_with_peaks_{out_prefix}.png"
    poincare_plot_path = f"out/poincare_plot_{out_prefix}.png"

    # === 加载数据 ===
    print("[STEP] Loading ECG data...")
    df = load_ecg_data(args.filepath)
    ecg_raw = df["ADC"].values
    # total_samples = len(ecg_raw)
    # time_vector = np.arange(total_samples) / args.fs

    # === 滤波处理 ===
    print("[STEP] Filtering ECG signal...")
    ecg_filtered = bandpass_filter(ecg_raw, args.fs)

    # === R 波检测 ===
    print("[STEP] Detecting R peaks...")
    rr_intervals, r_peaks = detect_r_peaks(ecg_filtered, args.fs)

    # === 数据清洗 ===
    print("[STEP] Cleaning RR intervals...")
    rr_cleaned = clean_rr_intervals(rr_intervals, max_diff=args.max_diff, min_rr=args.min_rr)

    # === 保存与可视化 ===
    save_rr_intervals(rr_cleaned, rr_csv_path)
    # plot_ecg_with_peaks(time_vector, ecg_filtered, r_peaks, ecg_plot_path)
    plot_poincare(rr_cleaned, poincare_plot_path)

    print("[DONE] All tasks completed.")


if __name__ == "__main__":
    main()
