from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan
import math

class NVFluorescenceFragment(Trap302EnvScan):
    """nv_fluorescence_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("nv_fluorescence_duration", FloatParam, "NV Fluorescence duration", default=5*us, unit="us")
                
    @kernel
    def device_setup(self):
        print("NVFluorescenceFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self):
        data = [0.000] * 2

        self.nv_mw_switch.off()
        
        # self.nv_laser_532nm_switch_control(switch='on')
        delay(self.nv_fluorescence_duration.get())
        self.sampler0.sample(data)
        delay(3*us) # insure RTIO
        #self.nv_laser_532nm_switch_control(switch='off')
        return data[1]

nv_fluorescence_fragment = make_fragment_scan_exp(NVFluorescenceFragment)