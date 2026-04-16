from ndscan.experiment import ExpFragment, FloatParam, IntParam, make_fragment_scan_exp, OpaqueChannel
from artiq.experiment import kernel, NumberValue

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.nv_detection import NVDetectionFragment
from repository.fragments.nv_polarization import NVPolarizationFragment
from repository.fragments.nv_microwave import NVMicrowaveFragment

class NVMicrowave_Ramsey(Trap302EnvScan):
    """NVMicrowave_Ramsey"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_result("results", OpaqueChannel)
        self.detection = self.setattr_fragment("detection", NVDetectionFragment)
        self.polarization = self.setattr_fragment("polarization", NVPolarizationFragment)
        self.microwave_1 = self.setattr_fragment("microwave1", NVMicrowaveFragment)
        self.microwave_2 = self.setattr_fragment("microwave2", NVMicrowaveFragment)
        self.setattr_param("ramsey_delay", FloatParam, "Ramsey delay", default=5*us, unit="us")
        self.setattr_argument("dds_switch_mode_idx", NumberValue(0, min=0, max=1, step=1, precision=0))

        ### set dds switch mode
        # self.dds_switch_mode = "dds_sw"
        # self.dds_switch_mode = "ttl"

    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.n_shots = 0
        self.init_longtime_equipment(pmt_or_ccd_bool=True)
        self.dds_switch_mode = ["dds_sw", "ttl"][int(self.dds_switch_mode_idx)]

    @kernel
    def device_setup(self):
        print("NVMicrowave_Ramsey: Device Setup")
        self.core.break_realtime()
        self.core.reset()

        self.device_setup_dds(self.dds_switch_mode)


    @kernel
    def device_setup_dds(self, dds_switch_mode="dds_sw"):
        # set dds's amp, freq, phase the same as microwave 1....
        self.microwave_1.run_once(set=True, switch_mode="no pulse")

        if dds_switch_mode == "dds_sw":
            self.nv_mw_switch.on() # It will always be "on" during the whole experiment.
            self.nv_dds_I.sw.off()
            self.nv_dds_Q.sw.off()
        elif dds_switch_mode == "ttl":
            self.nv_mw_switch.off()
            self.nv_dds_I.sw.on() # It will always be "on" during the whole experiment.
            self.nv_dds_Q.sw.on() # It will always be "on" during the whole experiment.

    # @kernel
    # def device_cleanup(self):
    #     Trap302EnvScan.device_cleanup(self)

    @kernel
    def init_longtime_equipment(self, pmt_or_ccd_bool=True):
        self.core.break_realtime()
        Trap302EnvScan.init_longtime_equipment(self, pmt_or_ccd_bool=pmt_or_ccd_bool)    

    @kernel
    def run_once(self):
        
        self.n_shots += 1
        self.flag_experiment.pulse(1*us)

        self.polarization.run_once(dds_switch_mode=self.dds_switch_mode)
        nv_count_1 = self.detection.run_once(dds_switch_mode=self.dds_switch_mode)
        delay(5*us)
        
        self.flag_experiment.pulse(1*us)
        self.microwave_1.run_once(
            set=True, # 可以改成false试试看，因为在device_setup_dds中已经设置好了
            switch_mode=self.dds_switch_mode
            )

        delay(self.ramsey_delay.get())
   
        self.microwave_2.run_once(
            set=False, 
            switch_mode=self.dds_switch_mode
            )
        nv_count_2 = self.detection.run_once(dds_switch_mode=self.dds_switch_mode)

        print("n_shots: ", self.n_shots)
        self.results.push([float(nv_count_1), float(nv_count_2)])


nv_microwave_ramsey = make_fragment_scan_exp(NVMicrowave_Ramsey) 