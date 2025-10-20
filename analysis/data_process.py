import h5py
import numpy as np

# 指定h5文件路径
file_path = r"D:\yangyuanming\artiq_control\302adc_dds2_ttl2\experiment\results\2025-08-13\19\000000402-BaseSequence.h5"

try:
    # 打开h5文件
    with h5py.File(file_path, "r") as f:
        # 获取第一个数据集名称
        dataset_name = list(f["datasets"].keys())[0]
        
        # 构建channel_counts的完整路径
        channel_counts_path = f"datasets/{dataset_name}/points/channel_counts"
        
        # 读取数据
        channel_counts = f[channel_counts_path][()]
        
        # 输出基本信息
        print(f"成功读取channel_counts数据")
        print(f"数据形状: {channel_counts.shape}")
        print(f"数据类型: {channel_counts.dtype}")
        print(f"前3行数据:\n{channel_counts[:3]}")

except Exception as e:
    print(f"读取数据时出错: {e}")
    