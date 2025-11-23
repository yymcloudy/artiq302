from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.doppler_cooling import DopplerCoolingFragment
from repository.fragments.pumping import PumpingFragment
from repository.fragments.detection import DetectionFragment

class Basic(Trap302EnvScan):
    """basic_sequence"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.doppler_cooling = self.setattr_fragment("doppler_cooling", DopplerCoolingFragment)
        self.pumping = self.setattr_fragment("pumping", PumpingFragment)
        self.detection = self.setattr_fragment("detection", DetectionFragment)

    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.n_shots = 0

    @kernel
    def device_setup(self):
        print("Basic sequence: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self):
        self.doppler_cooling.run_once()
        self.pumping.run_once()
        self.detection.run_once()
        delay(100*us)
        self.n_shots += 1
        print("n_shots: ", self.n_shots)

basic_sequence = make_fragment_scan_exp(Basic)