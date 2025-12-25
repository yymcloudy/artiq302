from queue import PriorityQueue
from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.doppler_cooling import DopplerCoolingFragment
from repository.fragments.pumping import PumpingFragment
from repository.fragments.detection import DetectionFragment
from repository.fragments.microwave import MicrowaveFragment

class TestLoop(Trap302EnvScan):
    """TestLoop"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.doppler_cooling = self.setattr_fragment("doppler_cooling", DopplerCoolingFragment)
        self.pumping = self.setattr_fragment("pumping", PumpingFragment)
        self.detection = self.setattr_fragment("detection", DetectionFragment)
        self.microwave = self.setattr_fragment("microwave", MicrowaveFragment)

    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.n_shots = 0
        self.init_longtime_equipment(pmt=True)

    @kernel
    def device_setup(self):
        print("TestLoop: Device Setup")
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
        smp = self.get_sampler()
        
        self.n_shots += 1
        print("n_shots: ", self.n_shots)
        print("smp: ", smp)

test_loop = make_fragment_scan_exp(TestLoop) 