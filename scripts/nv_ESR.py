from ndscan.experiment import ExpFragment, FloatParam, IntParam, make_fragment_scan_exp, OpaqueChannel
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.nv_detection import NVDetectionFragment
from repository.fragments.nv_polarization import NVPolarizationFragment
from repository.fragments.nv_esr import NVESRFragment

class NVESR(Trap302EnvScan):
    """NVESR"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_result("results", OpaqueChannel)
        self.polarization = self.setattr_fragment("polarization", NVPolarizationFragment)
        self.esr = self.setattr_fragment("esr", NVESRFragment)
        self.detection = self.setattr_fragment("detection", NVDetectionFragment)

    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.n_shots = 0
        self.init_longtime_equipment(pmt_or_ccd_bool=True)

    @kernel
    def device_setup(self):
        print("NVESR: Device Setup")
        self.core.break_realtime()
        self.core.reset()


    # @kernel
    # def device_cleanup(self):
    #     Trap302EnvScan.device_cleanup(self)

    @kernel
    def init_longtime_equipment(self, pmt_or_ccd_bool=True):
        self.core.break_realtime()
        Trap302EnvScan.init_longtime_equipment(self, pmt_or_ccd_bool=pmt_or_ccd_bool)    

    @kernel
    def run_once(self):
        self.polarization.run_once()
        # delay(10*ms)
        nv_polar_count = self.detection.run_once()
        # delay(30*ms)
        # nv_polar_count = 0
        delay(5*us)
        nv_esr_count = self.esr.run_once()
        # delay(10*ms)
        # nv_esr_count = 0

        # self.nv_double_pass_532.sw.on()
        self.n_shots += 1
        print("n_shots: ", self.n_shots)

        self.results.push([float(nv_polar_count), float(nv_esr_count)])

nv_esr = make_fragment_scan_exp(NVESR) 