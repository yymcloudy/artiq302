from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp, OpaqueChannel
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

class MicrowaveFragment(Trap302EnvScan):
    """microwave_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("microwave_frequency", FloatParam, "Microwave frequency", default=180.0*MHz, unit="MHz")
        self.setattr_param("microwave_duration", FloatParam, "Microwave duration", default=100.0*us, unit="us")
        self.setattr_param("microwave_amplitude", FloatParam, "Microwave amplitude", default=0.3, unit="")
        self.setattr_param("microwave_phase", FloatParam, "Microwave phase", default=0.0, unit="")

    @kernel
    def device_setup(self):
        print("MicrowaveFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self):
        self.laser370_switch_control(switch='off')
        self.mw_tunefreq.set(frequency=self.microwave_frequency.get(), phase=self.microwave_phase.get(), amplitude = self.microwave_amplitude.get())
        self.mw_tunefreq.sw.on()
        self.mw_switch.on()
        delay(self.microwave_duration.get())
        self.mw_switch.off()
        self.mw_tunefreq.sw.off()

microwave_fragment = make_fragment_scan_exp(MicrowaveFragment)