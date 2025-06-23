import os
import logging
import numpy as np

from .loader import load_ecg_data
from .filters import bandpass_filter
from .analysis import detect_r_peaks, clean_rr_intervals, save_rr_intervals
from .visualization import plot_ecg_with_peaks, plot_poincare


class ECGProcessor:
    def __init__(self, fs: int = 500, max_diff: float = 0.3,
                 min_rr: float = 0.0, lowcut: float = 1.0,
                 highcut: float = 45.0, order: int = 4):

        self.fs = fs
        self.max_diff = max_diff
        self.min_rr = min_rr
        self.lowcut = lowcut
        self.highcut = highcut
        self.order = order


    def process_file(self, filepath: str, out_dir: str = "out"):
        # === 加载数据 ===
        logging.info("Loading ECG data...")
        df = load_ecg_data(filepath)

        ecg_raw = df["ADC"].values

        total_samples = len(ecg_raw)
        time_vector = np.arange(total_samples) / self.fs

        # === 滤波处理 ===
        logging.info("Filtering ECG signal...")
        ecg_filtered = bandpass_filter(
            ecg_raw, self.fs, self.lowcut, self.highcut, self.order
        )

        # === R 波检测 ===
        logging.info("Detecting R peaks...")
        rr_intervals, r_peaks = detect_r_peaks(ecg_filtered, self.fs)

        # === 数据清洗 ===
        logging.info("Cleaning RR intervals...")
        rr_cleaned = clean_rr_intervals(
            rr_intervals, max_diff=self.max_diff, min_rr=self.min_rr
        )

        # === 输出路径设置 ===
        os.makedirs(out_dir, exist_ok=True)
        out_prefix = os.path.splitext(os.path.basename(filepath))[0]
        rr_csv_path = os.path.join(out_dir, f"rr_intervals_{out_prefix}.csv")
        # ecg_plot_path = os.path.join(out_dir, f"ecg_with_peaks_{out_prefix}.png"
        poincare_plot_path = os.path.join(out_dir, f"poincare_plot_{out_prefix}.png")


        # === 保存与可视化 ===
        save_rr_intervals(rr_cleaned, rr_csv_path)
        # if args.plot_ecg:
        #     plot_ecg_with_peaks(time_vector, ecg_filtered, r_peaks, ecg_plot_path)
        plot_poincare(rr_cleaned, poincare_plot_path)

        logging.info(f"Processing completed for {filepath}")
