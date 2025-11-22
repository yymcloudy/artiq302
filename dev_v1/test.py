import os
import sys

from artiq.experiment import EnvExperiment, kernel, delay, ms, parallel, sequential

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_CURRENT_DIR)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from dev_v1.tool import cool, pulse_dds

class Ramsey(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl15")
        self.dds_1_3 = self.get_device("urukul1_ch3")

        # 在 kernel 中会使用的“常量”放到属性里，并声明 invariant
        self.t_pi_us = 20.0

    @kernel
    def run(self):
        self.core.reset()

        # 预冷（调用独立模块里的 @kernel 函数）
        cool(self.core, self.ttl15, 200.0)

        # Ramsey π/2 - 等待 - π/2
        pulse_dds(self.dds_1_3, 12e6, 0.5, self.t_pi_us/2)
        delay(1.0*ms)
        pulse_dds(self.dds_1_3, 12e6, 0.5, self.t_pi_us/2)
