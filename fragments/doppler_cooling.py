from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

class DopplerCoolingFragment(Trap302EnvScan):
    """doppler_cooling_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("cooling_time", FloatParam, "Cooling time", default=1000.0*us, unit="us")
        self.setattr_param("cooling_double_pass_frequency", FloatParam, "Cooling double pass frequency", default=133*MHz, unit="MHz")

    @kernel
    def device_setup(self):
        print("DopplerCoolingFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self):
        with parallel:
            self.double_pass_370.set(frequency=self.cooling_double_pass_frequency.get(),phase=0.0, amplitude = 0.11)
            self.laser370_sideband_control(sideband='14.7', enable=True)
            self.laser370_sideband_control(sideband='2.1', enable=False)
        self.laser370_switch_control(switch='on')
        delay(self.cooling_time.get())
        self.laser370_switch_control(switch='off')

doppler_cooling_fragment = make_fragment_scan_exp(DopplerCoolingFragment)