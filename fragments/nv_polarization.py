from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

class NVPolarizationFragment(Trap302EnvScan):
    """nv_polarization_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("polarization_time", FloatParam, "NV polarization time", default=400.0*us, unit="us")

    @kernel
    def device_setup(self):
        print("NVPolarizationFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self):
        self.nv_double_pass_532.set_att(0.0*dB)
        self.nv_double_pass_532.set(frequency=220*MHz, phase=0.0, amplitude = 0.2)
        self.nv_mw_tunefreq.sw.off()

        self.nv_laser_532nm_switch_control(switch='on')    
        delay(self.polarization_time.get())
        self.nv_laser_532nm_switch_control(switch='off')

nv_polarization_fragment = make_fragment_scan_exp(NVPolarizationFragment)