from ndscan.experiment import ExpFragment, FloatParam, IntParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.nv_detection import NVDetectionFragment
from repository.fragments.nv_polarization import NVPolarizationFragment
from repository.fragments.nv_microwave import NVMicrowaveFragment

class NVMicrowave_Rabi(Trap302EnvScan):
    """NVMicrowave_Rabi"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.detection = self.setattr_fragment("detection", NVDetectionFragment)
        self.polarization = self.setattr_fragment("polarization", NVPolarizationFragment)
        self.microwave = self.setattr_fragment("microwave", NVMicrowaveFragment)


    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.n_shots = 0
        self.init_longtime_equipment(pmt=True)

    @kernel
    def device_setup(self):
        print("NVMicrowave_Rabi: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    # @kernel
    # def device_cleanup(self):
    #     Trap302EnvScan.device_cleanup(self)

    @kernel
    def init_longtime_equipment(self, pmt=True):
        self.core.break_realtime()
        Trap302EnvScan.init_longtime_equipment(self, pmt=True)    

    @kernel
    def run_once(self):
        self.n_shots += 1
        self.polarization.run_once()
        self.microwave.run_once()
        self.detection.run_once()
        delay(100*us)
        print("n_shots: ", self.n_shots)


nv_microwave_rabi = make_fragment_scan_exp(NVMicrowave_Rabi) 