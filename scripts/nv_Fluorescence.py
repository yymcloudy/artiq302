from ndscan.experiment import ExpFragment, FloatParam, IntParam, make_fragment_scan_exp, OpaqueChannel
from artiq.experiment import kernel
from artiq.experiment import NumberValue

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.nv_fluorescence import NVFluorescenceFragment

class NVFluorescence(Trap302EnvScan):
    """NVFluorescence"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_result("results", OpaqueChannel)
        self.fluorescence = self.setattr_fragment("fluorescence", NVFluorescenceFragment)
        self.setattr_param("timeline", FloatParam, "Timeline",default=100, unit="")

    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.n_shots = 0
        self.init_longtime_equipment(pmt_or_ccd_bool=True)

    @kernel
    def device_setup(self):
        print("NVFluorescence: Device Setup")
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
        self.n_shots += 1
        
        nv_count = self.fluorescence.run_once()
        
        print("n_shots: ", self.n_shots)
        self.results.push([float(nv_count)])


nv_fluorescence = make_fragment_scan_exp(NVFluorescence) 