import h5py
import numpy as np

# 指定h5文件路径
pid = 441   
file_path = r"D:\yangyuanming\artiq_control\302adc_dds2_ttl2\experiment\results\2025-08-14\01\000000441-BaseSequence.h5"

try:
    # 打开h5文件
    with h5py.File(file_path, "r") as f:
        print(f"成功打开文件: {file_path}")
        
        # 检查datasets组是否存在
        if "datasets" not in f:
            raise ValueError("文件中不存在'datasets'组")
        
        # 获取所有数据集名称并检查
        dataset_names = list(f["datasets"].keys())
        if not dataset_names:
            raise ValueError("'datasets'组中没有任何数据集")
        
        print(f"找到的数据集: {dataset_names}")
        dataset_name = dataset_names[0]
        dataset_path = f"datasets/{dataset_name}"
        
        # 检查points组是否存在
        if "points" not in f[dataset_path]:
            raise ValueError(f"数据集 {dataset_name} 中不存在'points'组")
        
        # 构建channel_counts的完整路径
        channel_counts_path = f"{dataset_path}/points/channel_counts"
        
        # 检查channel_counts是否存在
        if channel_counts_path not in f:
            # 尝试常见的替代路径（可能是单数形式或其他命名）
            alternative_paths = [
                f"{dataset_path}/points/channel_count",  # 单数形式
                f"{dataset_path}/channel_counts",        # 不在points下
                f"{dataset_path}/channel_count"          # 其他组合
            ]
            
            found = False
            for alt_path in alternative_paths:
                if alt_path in f:
                    channel_counts_path = alt_path
                    found = True
                    print(f"使用替代路径: {channel_counts_path}")
                    break
            
            if not found:
                raise ValueError(f"找不到channel_counts数据，已尝试路径: {channel_counts_path} 及其他替代路径")
        
        # 读取数据
        channel_counts = f[channel_counts_path][()]
        
        # 输出基本信息
        print(f"成功读取channel_counts数据")
        print(f"数据形状: {channel_counts.shape}")
        print(f"数据类型: {channel_counts.dtype}")
        print(f"前3行数据:\n{channel_counts[:3]}")

except FileNotFoundError:
    print(f"错误: 找不到文件 {file_path}")
except PermissionError:
    print(f"错误: 没有权限访问文件 {file_path}")
except Exception as e:
    print(f"读取数据时出错: {str(e)}")
    