import h5py
import numpy as np

pid = 462
# 文件路径
# file_path = r"D:\yangyuanming\artiq_control\302adc_dds2_ttl2\experiment\results\2025-08-13\19\000000402-BaseSequence.h5"
# file_path = r"D:\yangyuanming\artiq_control\302adc_dds2_ttl2\experiment\results\2025-08-14\01\000000441-BaseSequence.h5"
# file_path = r"D:\yangyuanming\artiq_control\302adc_dds2_ttl2\experiment\results\2025-08-14\01\000000442-BaseSequence.h5"
# file_path = r"D:\yangyuanming\artiq_control\302adc_dds2_ttl2\experiment\results\2025-08-14\01\000000444-BaseSequence.h5"
file_path = r"D:\yangyuanming\artiq_control\302adc_dds2_ttl2\experiment\results\2025-08-15\16\000000462-BaseSequence.h5"
def read_channel_counts(file_path):
    with h5py.File(file_path, "r") as f:
        # 1) 浏览结构 & 获取数据集
        print("top keys:", list(f.keys()))
        try:
            dataset_name = f"datasets/ndscan.rid_{pid}.points.channel_counts"
            if dataset_name in f:
                data = f[dataset_name][()]
                return data
            else:
                return None
        except Exception as e:
            return None

read_channel_counts(file_path)

# 读取channel_counts数据
data = read_channel_counts(file_path)
if data is None:
    print("未能读取到数据")
else:
    # 假设data的shape为 (N, 4)，前三列为索引（float），最后一列为结果
    # 先将前三列作为索引，最后一列为value
    # 由于float有精度问题，需要对前三列做分组，允许一定的容差
    from collections import defaultdict

    # 设置容差，比如1e-6以内认为是同一类
    tol = 1e-7

    def float_group_key(arr, tol=tol):
        # arr为长度为3的float数组
        # 用四舍五入到一定精度的tuple作为key
        return tuple([round(x / tol) for x in arr])

    grouped = defaultdict(list)
    for row in data:
        idx = row[:3]
        val = row[3]
        key = float_group_key(idx)
        grouped[key].append(val)

    # 输出分组后的结果
    print(f"分组数量: {len(grouped)}")
    for key, vals in grouped.items():
        # 还原为float索引，并将其格式化为更友好的字符串，避免出现一长串9
        idx_floats = tuple([k * tol for k in key])
        # 尝试将索引转为整数（如果接近整数），否则保留3位小数
        idx_fmt = []
        for v in idx_floats:
            if abs(v - round(v)) < tol * 10:
                idx_fmt.append(int(round(v)))
            else:
                idx_fmt.append(round(v, 6))
        print(f"索引: {tuple(idx_fmt)}, 结果数量: {len(vals)}, 结果示例: {vals[:]}")
    
    # 任选一组分组即可，不必特意筛选dim=1
    import matplotlib.pyplot as plt
    import numpy as np

    # 随便选一个分组（比如第一个）
    if not grouped:
        print("No grouped data found")
    else:
        # 取第一个分组
        selected_key = list(grouped.keys())[0]
        selected_vals = grouped[selected_key]
        print(f"\nSelected group index: {selected_key}, data count: {len(selected_vals)}")
        # 转为numpy数组
        vals = np.array(selected_vals)
        # 统计0-800区间内，以2为步长的直方图
        step = 2
        bins = np.arange(0, 101,step)
        hist, bin_edges = np.histogram(vals, bins=bins)
        print("Count in each interval:")
        for i in range(len(hist)):
            print(f"{bin_edges[i]:.0f} - {bin_edges[i+1]:.0f}: {hist[i]}")
        # 画图
        plt.figure(figsize=(10,2))
        plt.bar(bin_edges[:-1], hist, width=step, align='edge', edgecolor='k')
        plt.xlabel("Value")
        plt.ylabel("Count")
        plt.title(f"dim=1, index={selected_key} result distribution (0-800, step 10)")
        plt.tight_layout()
        plt.show()
