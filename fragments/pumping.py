from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

class PumpingFragment(Trap302EnvScan):
    """pumping_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("pumping_time", FloatParam, "Pumping time", default=20.0*us, unit="us")
        self.setattr_param("pumping_double_pass_frequency", FloatParam, "Pumping double pass frequency", default=128*MHz, unit="MHz")

    @kernel
    def device_setup(self):
        print("PumpingFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()


    @kernel
    def run_once(self):
        with parallel:
            self.double_pass_370.set(frequency=self.pumping_double_pass_frequency.get(),phase=0.0, amplitude = 0.75)
            self.laser370_sideband_control(sideband='14.7', enable=False)
            self.laser370_sideband_control(sideband='2.1', enable=True)
        self.laser370_switch_control(switch='on')
        delay(self.pumping_time.get())
        self.laser370_switch_control(switch='off')

pumping_fragment = make_fragment_scan_exp(PumpingFragment)