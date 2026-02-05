from ndscan.experiment import ExpFragment, FloatParam, IntParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.doppler_cooling import DopplerCoolingFragment
from repository.fragments.pumping import PumpingFragment
from repository.fragments.detection import DetectionFragment
from repository.fragments.microwave import MicrowaveFragment

class Sigma_x_noise(Trap302EnvScan):
    """Sigma_x noise"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.doppler_cooling = self.setattr_fragment("doppler_cooling", DopplerCoolingFragment)
        self.pumping = self.setattr_fragment("pumping", PumpingFragment)
        self.detection = self.setattr_fragment("detection", DetectionFragment)
        self.microwave_1 = self.setattr_fragment("microwave_1", MicrowaveFragment)
        self.microwave_2 = self.setattr_fragment("microwave_2", MicrowaveFragment)
        # self.microwave_3 = self.setattr_fragment("microwave_3", MicrowaveFragment)


    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.n_shots = 0
        self.init_longtime_equipment(pmt=True)

    @kernel
    def device_setup(self):
        print("Sigma_x_noise: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    # @kernel
    # def device_cleanup(self):
    #     Trap302EnvScan.device_cleanup(self)

    @kernel
    def init_longtime_equipment(self, pmt=True):
        self.core.break_realtime()
        self.double_pass_370.set_att(1.5*dB)
        Trap302EnvScan.init_longtime_equipment(self, pmt=True)    

    @kernel
    def run_once(self):
        self.doppler_cooling.run_once()
        self.pumping.run_once()
        self.microwave_1.run_once()
        self.microwave_2.run_once()
        # self.microwave_3.run_once()
        self.detection.run_once()
        delay(100*us)
        self.n_shots += 1
        print("n_shots: ", self.n_shots)

sigma_x_noise = make_fragment_scan_exp(Sigma_x_noise) 