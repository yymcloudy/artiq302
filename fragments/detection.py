from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp, OpaqueChannel
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

class DetectionFragment(Trap302EnvScan):
    """detection_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("detection_time", FloatParam, "PMT Detection time", default=300.0*us, unit="us")
        self.setattr_param("ccd_detection_time", FloatParam, "CCD Detection time", default=1000.0*us, unit="us")
        self.setattr_param("detection_double_pass_frequency", FloatParam, "Detection double pass frequency", default=134*MHz, unit="MHz")
        self.setattr_result("results", OpaqueChannel)

    @kernel
    def device_setup(self):
        print("DetectionFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self, pmt_or_ccd_bool=True):
        with parallel:
            self.double_pass_370.set(frequency=self.detection_double_pass_frequency.get(), phase=0.0, amplitude = 0.54)
            self.laser370_sideband_control(sideband='14.7', enable=False)
            self.laser370_sideband_control(sideband='2.1', enable=False)
        delay(2*us)
        self.laser370_switch_control(switch='on')
        if pmt_or_ccd_bool:
            # pmt detection
            with parallel:
                cnt = self.counter.gate_rising(self.detection_time.get())
                num = self.counter.count(cnt)
            delay(100*us)
            # results push
            self.results.push(float(num))
            print("pmt_optical_num: ", num)  
        else:
            # ccd detection
            self.ccd_trigger.off()
            delay(self.ccd_detection_time.get())
            self.ccd_trigger.on()
            delay(1000*ms)
            self.results.push(1.0)
            print("CCD Image Saved")

detection_fragment = make_fragment_scan_exp(DetectionFragment)


# class DetectionADCFragment(Trap302EnvScan):
#     """detection_adc_fragment"""
#     def build_fragment(self):
#         Trap302EnvScan.build_fragment(self)
#         self.setattr_param("detection_time", FloatParam, "Detection time", default=300.0*us, unit="us")
#         self.setattr_param("detection_double_pass_frequency", FloatParam, "Detection double pass frequency", default=134*MHz, unit="MHz")
#         self.setattr_result("results", OpaqueChannel)

#     @kernel
#     def device_setup(self):
#         print("DetectionADCFragment: Device Setup")
#         self.core.break_realtime()
#         self.core.reset()

#     @kernel
#     def run_once(self):
#         with parallel:
#             self.double_pass_370.set(frequency=self.detection_double_pass_frequency.get(), phase=0.0, amplitude = 0.54)
#             self.laser370_sideband_control(sideband='14.7', enable=False)
#             self.laser370_sideband_control(sideband='2.1', enable=False)
#         delay(2*us)
#         self.laser370_switch_control(switch='on')
#         with parallel:
#             cnt = self.counter.gate_rising(self.detection_time.get())
#             num = self.counter.count(cnt)
#         delay(100*us)
#         # results push
#         #sample the voltage
#         data = [0.000] * 8
#         self.sampler0.sample(data)
#         voltage_driven = data[6]


#         self.results.push([float(num), float(voltage_driven)])
#         print("pmt_optical_num: ", num)
#         print("adc_voltage: ", voltage_driven)

# detection_adc_fragment = make_fragment_scan_exp(DetectionADCFragment)
