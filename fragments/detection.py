from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp, OpaqueChannel
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

class DetectionFragment(Trap302EnvScan):
    """detection_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("detection_time", FloatParam, "Detection time", default=300.0*us, unit="us")
        self.setattr_param("detection_double_pass_frequency", FloatParam, "Detection double pass frequency", default=138*MHz, unit="MHz")
        self.setattr_result("results", OpaqueChannel)

    @kernel
    def device_setup(self):
        print("DetectionFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self):
        with parallel:
            self.double_pass_370.set(frequency=self.detection_double_pass_frequency.get(), phase=0.0, amplitude = 0.08)
            self.laser370_sideband_control(sideband='14.7', enable=False)
            self.laser370_sideband_control(sideband='2.1', enable=False)
        delay(2*us)
        self.laser370_switch_control(switch='on')
        with parallel:
            cnt = self.counter.gate_rising(self.detection_time.get())
            num = self.counter.count(cnt)
        delay(100*us)
        # results push
        self.results.push(float(num))
        print("pmt_optical_num: ", num)

detection_fragment = make_fragment_scan_exp(DetectionFragment)


class DetectionCCDFragment(Trap302EnvScan):
    """detection_ccd_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("detection_time", FloatParam, "Detection time", default=300.0*us, unit="us")
        self.setattr_param("detection_double_pass_frequency", FloatParam, "Detection double pass frequency", default=138*MHz, unit="MHz")
        self.setattr_result("results", OpaqueChannel)

    @kernel
    def device_setup(self):
        print("DetectionCCDFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self):
        with parallel:
            self.double_pass_370.set(frequency=self.detection_double_pass_frequency.get(), phase=0.0, amplitude = 0.08)
            self.laser370_sideband_control(sideband='14.7', enable=False)
            self.laser370_sideband_control(sideband='2.1', enable=False)
        delay(2*us)
        self.laser370_switch_control(switch='on')
        self.ccd_trigger.on()
        delay(self.detection_time.get())
        self.ccd_trigger.off()
        print("CCD Image Saved")

detection_ccd_fragment = make_fragment_scan_exp(DetectionCCDFragment)

class DetectionADCFragment(Trap302EnvScan):
    """detection_adc_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("detection_time", FloatParam, "Detection time", default=300.0*us, unit="us")
        self.setattr_param("detection_double_pass_frequency", FloatParam, "Detection double pass frequency", default=138*MHz, unit="MHz")
        self.setattr_result("results", OpaqueChannel)

    @kernel
    def device_setup(self):
        print("DetectionADCFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self):
        with parallel:
            self.double_pass_370.set(frequency=self.detection_double_pass_frequency.get(), phase=0.0, amplitude = 0.08)
            self.laser370_sideband_control(sideband='14.7', enable=False)
            self.laser370_sideband_control(sideband='2.1', enable=False)
        delay(2*us)
        self.laser370_switch_control(switch='on')
        with parallel:
            cnt = self.counter.gate_rising(self.detection_time.get())
            num = self.counter.count(cnt)
        delay(100*us)
        # results push
        #sample the voltage
        data = [0.000] * 8
        self.sampler0.sample(data)
        voltage_driven = data[6]


        self.results.push([float(num), float(voltage_driven)])
        print("pmt_optical_num: ", num)
        print("adc_voltage: ", voltage_driven)

detection_adc_fragment = make_fragment_scan_exp(DetectionADCFragment)
