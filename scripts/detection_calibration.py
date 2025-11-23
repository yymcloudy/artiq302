from ndscan.experiment import make_fragment_scan_exp, LinearGenerator
from ndscan.experiment import ExpFragment

from repository.fragments.ramsey import RamseyFragment
from repository.fragments.cooling import CoolingFragment
from repository.fragments.readout import ReadoutFragment

from artiq.experiment import*
from artiq.language.units import *

from repository.fragments.hwenv import HardwareEnvScan


class DetectionCalibration(HardwareEnvScan):
    def build_fragment(self):
        HardwareEnvScan.build_fragment(self)
        self.cool = self.setattr_fragment("cool", CoolingFragment)
        self.readout = self.setattr_fragment("readout", ReadoutFragment)

        self.exp_n = 0
    
    @kernel
    def run_once(self):
        self.cool.run_once()
        self.readout.run_once()
        delay(100*us)
        self.exp_n += 1
        print("experiment_num_shots: ", self.exp_n)

DetectionCalibrationScan = make_fragment_scan_exp(DetectionCalibration)