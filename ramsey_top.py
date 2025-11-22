from ndscan.experiment import make_fragment_scan_exp, LinearGenerator
from ndscan.experiment import ExpFragment

from repository.fragments.ramsey import RamseyFragment
from repository.fragments.cooling import CoolingFragment
from repository.fragments.readout import ReadoutFragment

from artiq.experiment import*
from artiq.language.units import *


class RamseyTop(ExpFragment):
    """ramsey top fragment
    """
    def build_fragment(self):
        
        self.cool = self.setattr_fragment("cool", CoolingFragment)
        self.ramsey = self.setattr_fragment("ramsey", RamseyFragment)
        self.readout = self.setattr_fragment("readout", ReadoutFragment)
        
        self.exp_n = 0
        # 默认扫描轴：t_wait 从 10us 到 1000us
        # self.set_default_scan(self.ramsey.t_wait, LinearGenerator(10.0, 1000.0, 50))

    def run_once(self):
        # 片段装配逻辑：每个点按此顺序执行
        self.cool.run_once()
        self.ramsey.run_once()
        self.readout.run_once()
        # delay(100*us)
        self.exp_n += 1
        print("experiment_num_shots: ", self.exp_n)


RamseyScan = make_fragment_scan_exp(RamseyTop)

