from ndscan.experiment import ExpFragment, FloatParam, IntParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.doppler_cooling import DopplerCoolingFragment
from repository.fragments.pumping import PumpingFragment
from repository.fragments.detection import DetectionFragment
from repository.fragments.microwave import MicrowaveFragment

class CPMG_XY8(Trap302EnvScan):
    """CPMG_XY8"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.doppler_cooling = self.setattr_fragment("doppler_cooling", DopplerCoolingFragment)
        self.pumping = self.setattr_fragment("pumping", PumpingFragment)
        self.detection = self.setattr_fragment("detection", DetectionFragment)
        self.pi_pulse_X = self.setattr_fragment("pi_pulse_X", MicrowaveFragment)
        self.pi_pulse_Y = self.setattr_fragment("pi_pulse_Y", MicrowaveFragment)
        self.Pi_by_2_pulse = self.setattr_fragment("Pi_by_2_pulse", MicrowaveFragment)

        self.setattr_param("tau", FloatParam, "tau", default=20.0*us, unit="us")
        self.setattr_param("n_XY8", IntParam, "Number of XY8 sequences", default=1, unit="")

    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.n_shots = 0
        self.init_longtime_equipment(pmt=True)

    @kernel
    def device_setup(self):
        print("CPMG_XY8: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def XY8_sequence(self):
        tau=self.tau.get()
        for i in range(2):
            delay(tau)
            self.pi_pulse_X.run_once()
            delay(tau)
            delay(tau)
            self.pi_pulse_Y.run_once()
            delay(tau)
        for i in range(2):
            delay(tau)
            self.pi_pulse_Y.run_once()
            delay(tau)
            delay(tau)
            self.pi_pulse_X.run_once()
            delay(tau)
    
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
        self.Pi_by_2_pulse.run_once()
        for i in range(self.n_XY8.get()):
            self.XY8_sequence()
        self.Pi_by_2_pulse.run_once()
        self.detection.run_once()
        delay(100*us)
        self.n_shots += 1
        print("n_shots: ", self.n_shots)

cpmg_xy8 = make_fragment_scan_exp(CPMG_XY8) 