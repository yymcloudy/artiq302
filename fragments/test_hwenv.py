from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.hwenv import HardwareEnvScan

class TestHwenvFragment(HardwareEnvScan):
    """test hwenv fragment"""
    def build_fragment(self):
        HardwareEnvScan.build_fragment(self)
        self.ttl_test = self.ttl15
        self.dds_test = self.dds_1_3
        self.setattr_param("t_test", FloatParam, "Test time", default=100.0*us, unit="us")
        self.setattr_param("frequency", FloatParam, "Frequency", default=100.0*MHz, unit="MHz")
        self.setattr_param("amplitude", FloatParam, "Amplitude", default=0.1, unit="")
        self.setattr_param("phase", FloatParam, "Phase", default=0.0, unit="")
        self.exp_n = 0

    @kernel
    def device_setup(self):
        pass

    @kernel
    def run_once(self):
        self.core.reset()
        self.core.break_realtime()
        self.ttl_test.on()
        self.dds_test.set(frequency=self.frequency.get(), phase=self.phase.get(), amplitude=self.amplitude.get())
        self.dds_test.sw.on()
        delay(self.t_test.get())
        self.ttl_test.off()
        self.dds_test.sw.off()
        delay(100*us)
        self.exp_n += 1
        print("experiment_num_shots: ", self.exp_n)

test_hwenv_fragment = make_fragment_scan_exp(TestHwenvFragment)
