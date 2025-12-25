from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.doppler_cooling import DopplerCoolingFragment
from repository.fragments.pumping import PumpingFragment
from repository.fragments.detection import DetectionFragment
from repository.fragments.microwave import MicrowaveFragment

class Empty(Trap302EnvScan):
    """Set Idle"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)

    def prepare(self):
        Trap302EnvScan.prepare(self)

    @kernel
    def device_setup(self):
        print("Empty: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    # @kernel
    # def device_cleanup(self):
    #     Trap302EnvScan.device_cleanup(self)

    @kernel
    def run_once(self):
        print("********Idle is going to set********")

empty = make_fragment_scan_exp(Empty) 