import h5py

#验证一下h5文件可以被读取

# 指定h5文件路径
file_path = r"D:\yangyuanming\artiq_control\302adc_dds2_ttl2\experiment\results\2025-08-10\15\000000289-Example2.h5"
file_path = r"D:\yangyuanming\artiq_control\302adc_dds2_ttl2\experiment\results\2025-08-06\20\000000236-Example2.h5"
# 打开h5文件并读取数据
with h5py.File(file_path, "r") as f:
    print("文件中的所有主键和数值：")
    def print_h5_structure(name, obj):
        if isinstance(obj, h5py.Dataset):
            print(f"数据集: {name}, shape: {obj.shape}, dtype: {obj.dtype}")
            try:
                data = obj[()]
                # 如果数据集很大，只显示前几个元素
                if data.size > 10:
                    print(f"前10个数值: {data.flat[:10]}")
                else:
                    print(f"数值: {data}")
            except Exception as e:
                print(f"读取数据集时出错: {e}")
        elif isinstance(obj, h5py.Group):
            print(f"组: {name}")
    f.visititems(print_h5_structure)

    f.visititems(print_h5_structure)

    # 如果你想读取某个具体数据集，可以这样：
    # data = f["你的数据集路径"][:]
    # print(data)
