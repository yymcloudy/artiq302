"""
Urukul AD9910 延迟标定脚本

用于板级/通道级标定 sync_delay_seed 和 io_update_delay。
标定结果需手动写回 device_db，或通过 EEPROM 存储（需在 device_db 中配置 SyncDataEeprom）。

前提条件：
1. 标定前需先正常 init()：init() 负责 SPI 模式、PLL 配置和锁定检查
2. tune_sync_delay() 仅在 CPLD 配置了 sync_device 时可用，否则会报 "parent cpld does not drive SYNC"
3. tune_io_update_delay() 不依赖 sync，可独立运行

标定流程：
1. cpld.init() -> dds.init()
2. 若 CPLD 有 sync_device：运行 tune_sync_delay()，得到 (optimal_delay, window)
3. 运行 tune_io_update_delay()，得到 io_update_delay
4. 将 sync_delay_seed=optimal_delay、io_update_delay 写回 device_db 对应通道的 arguments
"""

from artiq.experiment import *


class UrukulDelayCalibration(EnvExperiment):
    """Urukul AD9910 sync_delay 与 io_update_delay 标定"""

    def build(self):
        self.setattr_device("core")
        self.setattr_argument("urukul_id", NumberValue(0, min=0, max=1, step=1, precision=0))
        self.setattr_argument("channel_id", NumberValue(0, min=0, max=3, step=1, precision=0))
        self.setattr_argument(
            "skip_sync",
            BooleanValue(True),
            "跳过 tune_sync_delay（当 CPLD sync_device 为 None 时必选）",
        )

        # 获取目标 DDS
        dds_names = [
            ["urukul0_ch0", "urukul0_ch1", "urukul0_ch2", "urukul0_ch3"],
            ["urukul1_ch0", "urukul1_ch1", "urukul1_ch2", "urukul1_ch3"],
        ]
        self.dds_name = dds_names[int(self.urukul_id)][int(self.channel_id)]
        self.setattr_device(self.dds_name)

    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()

        dds = getattr(self, self.dds_name)
        dds.cpld.init()
        dds.init()
        delay(50 * ms)

        sync_delay_seed = -1
        sync_window = -1
        io_update_delay = -1

        # 1. tune_sync_delay（仅当 CPLD 有 sync_device 时可用）
        if not self.skip_sync:
            dly, win = dds.tune_sync_delay()
            sync_delay_seed = dly
            sync_window = win
            self.set_dataset("sync_delay_seed", sync_delay_seed, broadcast=True)
            self.set_dataset("sync_window", sync_window, broadcast=True)
            delay(10 * ms)

        # 2. tune_io_update_delay（始终可运行）
        io_update_delay = dds.tune_io_update_delay()
        self.set_dataset("io_update_delay", io_update_delay, broadcast=True)

    def analyze(self):
        """在 host 端打印标定结果及 device_db 更新说明"""
        dds_name = self.dds_name
        sync_delay_seed = self.get_dataset("sync_delay_seed", -1) if not self.skip_sync else -1
        sync_window = self.get_dataset("sync_window", -1) if not self.skip_sync else -1
        io_update_delay = self.get_dataset("io_update_delay", -1)

        print("\n" + "=" * 60)
        print("Urukul AD9910 延迟标定结果")
        print("=" * 60)
        print(f"通道: {dds_name}")
        print(f"io_update_delay: {io_update_delay}")
        if not self.skip_sync:
            print(f"sync_delay_seed: {sync_delay_seed}  (window={sync_window}, 仅 seed 需写回)")
        else:
            print("sync_delay_seed: 已跳过（CPLD 无 sync_device 时无法标定）")
        print("=" * 60)
        print("\n请将以下内容加入 device_db 中对应通道的 arguments：")
        print(f'  "{dds_name}": {{')
        print('    ...')
        if not self.skip_sync:
            print(f'    "sync_delay_seed": {sync_delay_seed},')
        print(f'    "io_update_delay": {io_update_delay}')
        print("  }")
        print("\n或使用 EEPROM：将 sync_delay_seed 与 io_update_delay 写入 EEPROM 后，")
        print('在 arguments 中设置 "sync_delay_seed": "eeprom_urukulX:offset",')
        print('"io_update_delay": "eeprom_urukulX:offset"（两者需指向同一 EEPROM 地址）')
        print("=" * 60 + "\n")
