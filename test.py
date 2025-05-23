"""直接从原始文件中转换得到RR间期，并保存为CSV文件"""
import sys
import pandas as pd
from data_loader import load_ecg_data


# === 参数设置 ===
FILEPATH = sys.argv[1] if len(sys.argv) > 1 else "data/10 min.txt"
out_prefix = FILEPATH.replace("/", "_").replace("\\", "_").replace(".txt", "")
out_prefix = out_prefix.split("_")[-1]

FS = 500  # 采样率

RR_CSV_PATH = f"out/rr_intervals_{out_prefix}.csv"
ECG_PLOT_PATH = f"out/ecg_with_peaks_{out_prefix}.png"

df = load_ecg_data(FILEPATH)

rr_from_hr4s = pd.DataFrame({
    "RR(n)": df["rr_interval_from_hr4s"][:-1].reset_index(drop=True),
    "RR(n+1)": df["rr_interval_from_hr4s"][1:].reset_index(drop=True)
})
rr_from_hr4s.to_csv(f"out/rr_from_hr4s_{out_prefix}.csv", index=False)

rr_from_hr30s = pd.DataFrame({
    "RR(n)": df["rr_interval_from_hr30s"][:-1].reset_index(drop=True),
    "RR(n+1)": df["rr_interval_from_hr30s"][1:].reset_index(drop=True)
})
rr_from_hr30s.to_csv(f"out/rr_from_hr30s_{out_prefix}.csv", index=False)