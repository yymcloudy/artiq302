import h5py
import numpy as np
import pandas as pd


rid=1076
def extract_counts(h5_path,
                   key_counts=f"datasets/ndscan.rid_{rid}.points.channel_counts",
                   key_ax0=f"datasets/ndscan.rid_{rid}.points.axis_0",
                   key_ax1=f"datasets/ndscan.rid_{rid}.points.axis_1",
                   out_csv=None):
    with h5py.File(h5_path, "r") as f:
        counts = f[key_counts][()]                  # 形状 ~ (N, 3)
        print(counts.shape)
        ax0 = f[key_ax0][()] if key_ax0 in f else np.arange(len(counts))
        # ax1 = f[key_ax1][()] if key_ax1 in f else np.zeros(len(counts))

    df = pd.DataFrame(counts, columns=[f"ch{i}" for i in range(counts.shape[1])])
    # df.insert(0, "axis_1", ax1)
    df.insert(0, "axis_0", ax0)

    if out_csv:
        df.to_csv(out_csv, index=False)
    return df

# 用法示例：
df = extract_counts(f"D:\\yangyuanming\\artiq_control\\302adc_dds2_ttl2\\experiment\\results\\2025-10-13\\21\\00000{rid}-BaseSequence.h5",
                    out_csv=f"00000{rid}_channel_counts.csv")
print(df.head())

import matplotlib.pyplot as plt

# 提取 ch0 为 x，ch1 为 y
x = df['ch0']
y = df['ch1']

# 按x分组，计算y的均值和标准误差
grouped = df.groupby('ch0')['ch1']
x_unique = grouped.mean().index.values
y_mean = grouped.mean().values
y_sem = grouped.sem().values  # 标准误（standard error of mean）

# 绘制带误差棒的折线图/散点图
plt.figure(figsize=(8,6))
plt.errorbar(x_unique*1e6, y_mean, yerr=y_sem, fmt='o', capsize=5, markersize=6, label='mean ± SEM')
plt.xlabel("pumping time (us)")
plt.ylabel("counts")
plt.title("counts vs pumping time")
plt.grid(True)
plt.tight_layout()
plt.legend()
plt.show()

