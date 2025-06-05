import pandas as pd
import re


def load_ecg_data(filepath: str) -> pd.DataFrame:
    data = []

    with open(filepath, 'r') as file:
        for line in file:
            match = re.match(r"(\d+\.\d+):\s+(-?\d+)\s+(\d+)\s+(\d+)", line)
            if match:
                timestamp = float(match.group(1))
                adc = int(match.group(2))
                hr_4s = int(match.group(3))
                hr_30s = int(match.group(4))
                data.append((timestamp, adc, hr_4s, hr_30s))

    columns = ["Time", "ADC"]

    return pd.DataFrame(data, columns=columns)


if __name__ == "__main__":
    # 测试加载函数
    filepath = "data/10 min.txt"
    df = load_ecg_data(filepath)
    print(df.head())
