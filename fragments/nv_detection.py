from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan
import math

class NVDetectionFragment(Trap302EnvScan):
    """nv_detection_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("nv_detection_duration", FloatParam, "NV Detection duration", default=5*us, unit="us")
                
    @kernel
    def device_setup(self):
        print("NVDetectionFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self, dds_switch_mode="dds_sw", measure_shots=1):
        data = [0.000] * 2
        nv_count_reg = [0.000] * measure_shots
        nv_sum = 0.0
        nv_max = -1e6
        nv_min = 1e6

        # self.nv_double_pass_532.set_att(0.0*dB)
        # self.nv_double_pass_532.set(frequency=220*MHz, phase=0.0, amplitude = 0.2)
        if dds_switch_mode == "dds_sw":
            self.nv_dds_I.sw.off()
            self.nv_dds_Q.sw.off()
        elif dds_switch_mode == "ttl":
            self.nv_mw_switch.off()


        self.nv_laser_532nm_switch_control(switch='on')
        delay(self.nv_detection_duration.get())

        if measure_shots == 1:
            self.sampler0.sample(data)
            delay(2000*us)
            self.nv_laser_532nm_switch_control(switch='off')
            return data[1]
        else:
            for i in range(measure_shots):
                self.sampler0.sample(data)
                nv_count_reg[i] = data[1]
                nv_sum += nv_count_reg[i]
                if nv_count_reg[i] > nv_max:
                    nv_max = nv_count_reg[i]
                if nv_count_reg[i] < nv_min:
                    nv_min = nv_count_reg[i]
                delay(3*us)
            delay(2000*us) # insure RTIO
            self.nv_laser_532nm_switch_control(switch='off')

            # print("nv_count: ", nv_count)
            return (nv_sum-(nv_max+nv_min))/(measure_shots-2)
            # return nv_sum/measure_shots

nv_detection_fragment = make_fragment_scan_exp(NVDetectionFragment)