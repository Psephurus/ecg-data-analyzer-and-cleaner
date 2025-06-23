import logging
import numpy as np
import matplotlib.pyplot as plt


def plot_ecg_with_peaks(time: np.ndarray, ecg: np.ndarray,
                        r_peaks: np.ndarray, output_path: str):
    """绘制带有 R 波峰值的 ECG 图。"""
    plt.figure(figsize=(250, 4))
    plt.plot(time, ecg, linewidth=0.8)
    plt.scatter(time[r_peaks], ecg[r_peaks], color='red', s=10)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=600)
    logging.info(f"ECG plot with R peaks saved to: {output_path}")
    plt.close()


def plot_poincare(rr_intervals: np.ndarray, output_path: str):
    """
    绘制庞加莱散点图（RR_n vs RR_n+1）

    参数:
        rr_intervals (np.ndarray): 清洗后的 R-R 间期
        output_path (str): 输出图像路径
    """
    rr_intervals_ms = rr_intervals * 1000

    rr_n = rr_intervals_ms[:-1]
    rr_n1 = rr_intervals_ms[1:]

    plt.figure(figsize=(6, 6))

    # 绘制蓝色实心点，无边框
    plt.scatter(rr_n, rr_n1, color='blue', edgecolors='none', s=10)

    # 设置标签字体
    font = {'family': 'Arial', 'weight': 'bold', 'size': 12}
    plt.xlabel("R$_{n-1}$-R$_n$ intervals (ms)", fontdict=font)
    plt.ylabel("R$_n$-R$_{n+1}$ intervals (ms)", fontdict=font)

    # 去掉网格线
    plt.grid(False)

    # 设置边框线宽
    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_linewidth(2.25)

    # 设置坐标轴刻度
    ax.tick_params(axis='both', which='major', labelsize=12, width=1.5)
    
    # 坐标轴等比例
    plt.axis("equal")
    plt.tight_layout()

    # 保存图像
    plt.savefig(output_path, dpi=300)
    logging.info(f"Poincaré plot saved to: {output_path}")
    plt.close()
