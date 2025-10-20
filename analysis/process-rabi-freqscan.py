import h5py
import numpy as np
import pandas as pd


rid=1096
def extract_counts(h5_path,
                   key_counts=f"datasets/ndscan.rid_{rid}.points.channel_counts",
                   key_ax0=f"datasets/ndscan.rid_{rid}.points.axis_0",
                   key_ax1=f"datasets/ndscan.rid_{rid}.points.axis_1",
                   out_csv=None):
    with h5py.File(h5_path, "r") as f:
        counts = f[key_counts][()]                  # 形状 ~ (N, 3)
        print(counts.shape)
        ax0 = f[key_ax0][()] if key_ax0 in f else np.arange(len(counts))
        ax1 = f[key_ax1][()] if key_ax1 in f else np.zeros(len(counts))

    df = pd.DataFrame(counts, columns=[f"ch{i}" for i in range(counts.shape[1])])
    df.insert(0, "axis_1", ax1)
    df.insert(0, "axis_0", ax0)

    if out_csv:
        df.to_csv(out_csv, index=False)
    return df

# 用法示例：
df = extract_counts(f"D:\\yangyuanming\\artiq_control\\302adc_dds2_ttl2\\experiment\\results\\2025-10-13\\23\\00000{rid}-BaseSequence.h5",
                    out_csv=f"00000{rid}_channel_counts.csv")
print(df.head())

import matplotlib.pyplot as plt

# 提取 ch1 和 ch2
x = df['ch1']
y = df['ch2']

# 按x分组，计算y的均值和标准误
grouped = df.groupby('ch1')['ch2']
x_unique = grouped.mean().index.values
y_mean = grouped.mean().values
y_sem = grouped.sem().values  # 标准误差（standard error of mean）

# 绘制均值和误差棒的图
plt.figure(figsize=(8,6))
plt.errorbar((x_unique + 12.5e9) / 1e9, y_mean, yerr=y_sem, fmt='o', capsize=5, markersize=6, label='mean ± SEM')
plt.xlabel("MW frequency (GHz)")
plt.ylabel("counts")
plt.title("counts vs MW frequency")
plt.grid(True)
plt.tight_layout()
plt.legend()
plt.show()

