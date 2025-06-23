import os
import pandas as pd


def load_ecg_data(filepath: str) -> pd.DataFrame:
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"ECG File not Found: {filepath}")

    data = []

    with open(filepath, 'r') as file:
        next(file)
        for line in file:
            parts = line.split()
            timestamp = float(parts[0][:-1])  # 去掉末尾的冒号
            adc = int(parts[1])
            data.append((timestamp, adc))

    columns = ["Time", "ADC"]

    return pd.DataFrame(data, columns=columns)


if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 测试加载函数
    filepath = "../data/20250604/dataLog-2025-6-2-12-31-6-1.5h.txt"
    df = load_ecg_data(filepath)
    print(df.head())

    logging.info(f"Loaded {len(df)} records from {filepath}")
