from ndscan.experiment import ExpFragment, FloatParam, IntParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.doppler_cooling import DopplerCoolingFragment
from repository.fragments.pumping import PumpingFragment
from repository.fragments.detection import DetectionFragment
from repository.fragments.microwave import MicrowaveFragment

class MicroWave_Rabi(Trap302EnvScan):
    """MW_Rabi"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.doppler_cooling = self.setattr_fragment("doppler_cooling", DopplerCoolingFragment)
        self.pumping = self.setattr_fragment("pumping", PumpingFragment)
        self.detection = self.setattr_fragment("detection", DetectionFragment)
        self.microwave = self.setattr_fragment("microwave", MicrowaveFragment)

        self.setattr_param("pi_pulse_number", IntParam, "Pi pulse number", default=1, unit="")
        self.setattr_param("pmt_or_ccd", IntParam, "pmt_or_ccd", default=1, min=0, max=1)

    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.n_shots = 0
        self.pmt_or_ccd_bool = (self.pmt_or_ccd.get() == 1)
        self.init_longtime_equipment(pmt_or_ccd_bool=self.pmt_or_ccd_bool)

    @kernel
    def device_setup(self):
        print("MicroWave_Rabi: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    # @kernel
    # def device_cleanup(self):
    #     Trap302EnvScan.device_cleanup(self)

    @kernel
    def init_longtime_equipment(self, pmt_or_ccd_bool=True):
        self.core.break_realtime()
        self.double_pass_370.set_att(1.5*dB)
        Trap302EnvScan.init_longtime_equipment(self, pmt_or_ccd_bool=pmt_or_ccd_bool)    

    @kernel
    def run_once(self):
        self.doppler_cooling.run_once()
        self.pumping.run_once()
        for i in range(self.pi_pulse_number.get()):
            self.microwave.run_once()
            delay(0.1*us)
        self.detection.run_once(pmt_or_ccd_bool=self.pmt_or_ccd_bool)
        delay(100*us)
        self.n_shots += 1
        print("n_shots: ", self.n_shots)

microwave_rabi = make_fragment_scan_exp(MicroWave_Rabi) 