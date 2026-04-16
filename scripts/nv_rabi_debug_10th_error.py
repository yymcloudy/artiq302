from ndscan.experiment import ExpFragment, FloatParam, IntParam, make_fragment_scan_exp, OpaqueChannel
from artiq.experiment import kernel
from artiq.experiment import NumberValue

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.nv_detection import NVDetectionFragment
from repository.fragments.nv_polarization import NVPolarizationFragment
from repository.fragments.nv_microwave import NVMicrowaveFragment

class NVMicrowave_Rabi(Trap302EnvScan):
    """NVMicrowave_Rabi"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_result("results", OpaqueChannel)
        self.detection = self.setattr_fragment("detection", NVDetectionFragment)
        self.polarization = self.setattr_fragment("polarization", NVPolarizationFragment)
        self.microwave = self.setattr_fragment("microwave", NVMicrowaveFragment)
        self.setattr_argument("dds_switch_mode_idx", NumberValue(0, min=0, max=1, step=1, precision=0))
        
        # self.dds_switch_mode = "dds_sw"
        # self.dds_switch_mode = "ttl"

    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.n_shots = 0
        self.init_longtime_equipment(pmt_or_ccd_bool=True)
        self.dds_switch_mode = ["dds_sw", "ttl"][int(self.dds_switch_mode_idx)]

    @kernel
    def device_setup(self):
        print("NVMicrowave_Rabi: Device Setup")
        self.core.break_realtime()
        self.core.reset()
        self.device_setup_dds(dds_switch_mode=self.dds_switch_mode)
        # self.core.break_realtime()
        # self.core.reset()
    
    @kernel
    def device_setup_dds(self, dds_switch_mode="dds_sw"):
        # set dds's amp, freq, phase the same as microwave 1....
        self.microwave.run_once(set=True, switch_mode="no pulse")

        if dds_switch_mode == "dds_sw":
            self.nv_mw_switch.on() # It will always be "on" during the whole experiment.
            self.nv_dds_I.sw.off()
            self.nv_dds_Q.sw.off()
        elif dds_switch_mode == "ttl":
            self.nv_mw_switch.off()
            self.nv_dds_I.sw.on() # It will always be "on" during the whole experiment.
            self.nv_dds_Q.sw.on() # It will always be "on" during the whole experiment.
        delay(20*ms)

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
        
        self.polarization.run_once(dds_switch_mode=self.dds_switch_mode)
        # delay(9000*us)
        nv_count_1 = self.detection.run_once(dds_switch_mode=self.dds_switch_mode, measure_shots=4)
        delay(5*us)
        
        self.microwave.run_once(switch_mode=self.dds_switch_mode)
        
        nv_count_2 = self.detection.run_once(dds_switch_mode=self.dds_switch_mode, measure_shots=4)
        

        print("n_shots: ", self.n_shots)
        self.results.push([float(nv_count_1), float(nv_count_2)])


nv_microwave_rabi = make_fragment_scan_exp(NVMicrowave_Rabi) 