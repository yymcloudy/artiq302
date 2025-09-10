import h5py
import numpy as np

#验证一下h5文件可以被读取

# 指定h5文件路径
file_path = r"D:\yangyuanming\artiq_control\302adc_dds2_ttl2\experiment\results\2025-08-10\15\000000289-Example2.h5"
file_path = r"D:\yangyuanming\artiq_control\302adc_dds2_ttl2\experiment\results\2025-08-06\20\000000236-Example2.h5"
file_path = r"D:\yangyuanming\artiq_control\302adc_dds2_ttl2\experiment\results\2025-08-12\20\000000365-BaseSequence.h5"
file_path = r"D:\yangyuanming\artiq_control\302adc_dds2_ttl2\experiment\results\2025-08-13\19\000000402-BaseSequence.h5"
# 打开h5文件并读取数据

path = file_path

# 1) 浏览结构 & 获取数据集
with h5py.File(path, "r") as f:
    # 顶层组/数据集
    print("top keys:", list(f.keys()))

    # 递归打印所有组/数据集信息
    def show(name, obj):
        if isinstance(obj, h5py.Group):
            print(f"[GROUP]   {name}")
        elif isinstance(obj, h5py.Dataset):
            print(f"[DATASET] {name} shape={obj.shape} dtype={obj.dtype}")
    f.visititems(show)

    # 2) 读取具体数据集（使用实际存在的路径）
    try:
        # 尝试访问一些实际存在的数据集
        if "datasets" in f:
            # 获取可用的数据集
            available_datasets = list(f["datasets"].keys())
            if available_datasets:
                # 选择第一个数据集（例如：ndscan.rid_402）
                first_dataset = available_datasets[0]
                print(f"\n尝试访问数据集: {first_dataset}")
                
                # 构建完整的数据集路径
                dataset_path = f"datasets/{first_dataset}"
                
                # 访问该数据集下的points
                if "points" in f[dataset_path]:
                    points_group = f[f"{dataset_path}/points"]
                    print(f"Points组中的键: {list(points_group.keys())}")
                    
                    # 尝试读取axis_0数据
                    if "axis_0" in points_group:
                        axis_data = points_group["axis_0"][...]
                        print(f"axis_0数据: shape={axis_data.shape}, dtype={axis_data.dtype}")
                        print(f"前5个值: {axis_data[:5]}")
                    
                    # 尝试读取channel_counts数据（注意是复数形式）
                    if "channel_counts" in points_group:
                        channel_data = points_group["channel_counts"][...]
                        print(f"channel_counts数据: shape={channel_data.shape}, dtype={channel_data.dtype}")
                        print(f"前3行数据:\n{channel_data[:3]}")
                
                # 访问分析结果（标量数据集）
                if "analysis_results" in f[dataset_path]:
                    analysis_data = f[f"{dataset_path}/analysis_results"][()]
                    print(f"analysis_results数据: {analysis_data}")
                
                # 访问其他标量数据集
                if "completed" in f[dataset_path]:
                    completed = f[f"{dataset_path}/completed"][()]
                    print(f"completed: {completed}")
                
                if "seed" in f[dataset_path]:
                    seed = f[f"{dataset_path}/seed"][()]
                    print(f"seed: {seed}")
                
                # 访问channels信息
                if "channels" in f[dataset_path]:
                    channels = f[f"{dataset_path}/channels"][()]
                    print(f"channels: {channels}")
                
                # 访问axes信息
                if "axes" in f[dataset_path]:
                    axes = f[f"{dataset_path}/axes"][()]
                    print(f"axes: {axes}")
        
        # 读取文件级别的属性
        print(f"\n文件属性: {dict(f.attrs)}")
        
        # 读取rid信息
        if "rid" in f:
            rid = f["rid"][()]
            print(f"运行ID (rid): {rid}")
            
        # 读取实验ID
        if "expid" in f:
            expid = f["expid"][()]
            print(f"实验ID: {expid}")
            
        # 读取运行时间和开始时间
        if "run_time" in f:
            run_time = f["run_time"][()]
            print(f"运行时间: {run_time}")
            
        if "start_time" in f:
            start_time = f["start_time"][()]
            print(f"开始时间: {start_time}")
            
    except Exception as e:
        print(f"读取数据时出错: {e}")
        print("请检查文件结构并调整访问路径")

    print("\n=== 文件结构分析完成 ===")

    # 读取并打印指定数据集的数据
    try:
        # 假设f是已经打开的h5py.File对象
        dataset_name = "datasets/ndscan.rid_402.points.channel_counts"
        if dataset_name in f:
            data = f[dataset_name][()]
            print(f"\n数据集 {dataset_name} 的内容如下：")
            print(data)
            print(f"数据形状: {data.shape}, 数据类型: {data.dtype}")
        else:
            print(f"数据集 {dataset_name} 不存在于文件中。")
    except Exception as e:
        print(f"读取 {dataset_name} 时出错: {e}")


 