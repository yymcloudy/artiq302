from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.doppler_cooling import DopplerCoolingFragment
from repository.fragments.pumping import PumpingFragment
from repository.fragments.detection import DetectionFragment
from repository.fragments.microwave import MicrowaveFragment

class MW_Ramsey(Trap302EnvScan):
    """MW_Ramsey"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.doppler_cooling = self.setattr_fragment("doppler_cooling", DopplerCoolingFragment)
        self.pumping = self.setattr_fragment("pumping", PumpingFragment)
        self.microwave_1 = self.setattr_fragment("microwave_1", MicrowaveFragment)
        self.microwave_2 = self.setattr_fragment("microwave_2", MicrowaveFragment)
        self.detection = self.setattr_fragment("detection", DetectionFragment)
        
        self.setattr_param("evolution_time", FloatParam, "Evolution time", default=20.0*us, unit="us")
    
    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.n_shots = 0

    @kernel
    def device_setup(self):
        print("MW_Ramsey: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self):
        self.doppler_cooling.run_once()
        self.pumping.run_once()
        self.microwave_1.run_once()
        delay(self.evolution_time.get())
        self.microwave_2.run_once()
        self.detection.run_once()
        delay(100*us)
        self.n_shots += 1
        print("n_shots: ", self.n_shots)

mw_ramsey = make_fragment_scan_exp(MW_Ramsey)