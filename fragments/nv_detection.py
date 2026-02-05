from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

class NVDetectionFragment(Trap302EnvScan):
    """nv_detection_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
                
    @kernel
    def device_setup(self):
        print("NVDetectionFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self):
        data = [0.000] * 8
        # self.nv_double_pass_532.set_att(0.0*dB)
        # self.nv_double_pass_532.set(frequency=220*MHz, phase=0.0, amplitude = 0.2)
        self.nv_mw_tunefreq.sw.off()


        self.nv_laser_532nm_switch_control(switch='on')
        delay(2*us)
        self.sampler0.sample(data)
        nv_count = data[7]
        delay(100*us) # insure RTIO
        self.nv_laser_532nm_switch_control(switch='off')
        print("nv_count: ", nv_count)

nv_detection_fragment = make_fragment_scan_exp(NVDetectionFragment)