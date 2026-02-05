from ndscan.experiment import ExpFragment, FloatParam, IntParam, make_fragment_scan_exp, OpaqueChannel
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

class MagneticGenFragment(Trap302EnvScan):
    """magnetic_gen_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("magnetic_switch", IntParam, "Magnetic switch", default=0, unit="", min=0, max=100)   

    @kernel
    def device_setup(self):
        print("MagneticGenFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    # @kernel
    # def run_once(self):
        
    #     self.magnetic_noise_switch_control(switch=(self.magnetic_switch.get()==1))

    @kernel
    def run_once(self, magnetic_0=0):
        magnetic_switch = self.magnetic_switch.get()
        if magnetic_switch != magnetic_0:
            self.magnetic_noise_switch_control(switch=False)
            delay(1*us)
            self.magnetic_noise_switch_control(switch=True)
            delay(1*us)
            self.magnetic_noise_switch_control(switch=False)
            delay(1*us)
        
        magnetic_0 = magnetic_switch
        return magnetic_0
        
magnetic_gen_fragment = make_fragment_scan_exp(MagneticGenFragment)