from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp, OpaqueChannel
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

class DetectionFragment(Trap302EnvScan):
    """detection_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("detection_time", FloatParam, "Detection time", default=100.0*us, unit="us")
        self.setattr_result("results", OpaqueChannel)

    @kernel
    def device_setup(self):
        print("DetectionFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self):
        with parallel:
            self.double_pass_370.set(frequency=139*MHz, phase=0.0, amplitude = 0.08)
            self.laser370_sideband_control(sideband='14.7', enable=False)
            self.laser370_sideband_control(sideband='2.1', enable=False)
        self.laser370_switch_control(switch='on')
        with parallel:
            cnt = self.counter.gate_rising(self.detection_time.get())
            num = self.counter.count(cnt)
        delay(100*us)
        # results push
        self.results.push(float(num))
        print("pmt_optical_num: ", num)

detection_fragment = make_fragment_scan_exp(DetectionFragment)