from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

class NVMicrowaveFragment(Trap302EnvScan):
    """nv_microwave_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("nv_microwave_frequency", FloatParam, "NV Microwave frequency", default=120.0*MHz, unit="MHz")
        self.setattr_param("nv_microwave_duration", FloatParam, "NV Microwave duration", default=1.0*us, unit="us") 
        self.setattr_param("nv_microwave_amplitude", FloatParam, "NV Microwave amplitude", default=0.3, unit="")
        self.setattr_param("nv_microwave_phase", FloatParam, "NV Microwave phase", default=0.0, unit="")

        
    @kernel
    def device_setup(self):
        print("NVMicrowaveFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self):
        self.nv_double_pass_532.sw.off()

        self.nv_mw_tunefreq.set(frequency=self.nv_microwave_frequency.get(), phase=self.nv_microwave_phase.get(), amplitude = self.nv_microwave_amplitude.get())
        self.nv_mw_tunefreq.sw.on()
        delay(self.nv_microwave_duration.get())
        self.nv_mw_tunefreq.sw.off()

nv_microwave_fragment = make_fragment_scan_exp(NVMicrowaveFragment)