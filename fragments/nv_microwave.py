from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

class NVMicrowaveFragment(Trap302EnvScan):
    """nv_microwave_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("nv_microwave_frequency", FloatParam, "NV Microwave frequency", default=170.0*MHz, unit="MHz")
        self.setattr_param("nv_microwave_duration", FloatParam, "NV Microwave duration", default=1.0*us, unit="us") 
        self.setattr_param("nv_microwave_amplitude", FloatParam, "NV Microwave amplitude", default=0.3, unit="")
        self.setattr_param("nv_microwave_phase", FloatParam, "NV Microwave phase", default=0.0, unit="")

    @kernel
    def device_setup(self):
        print("NVMicrowaveFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self, IQ_phase=0.78, phase_shift=0.0, switch_mode="dds_sw", set=True):
        # print("phase=",self.nv_microwave_phase.get())
        
        if set:
            self.nv_dds_I.set(frequency=self.nv_microwave_frequency.get(), phase=(phase_shift+self.nv_microwave_phase.get())%1.0, amplitude = self.nv_microwave_amplitude.get())
            # self.nv_dds_Q.set(frequency=self.nv_microwave_frequency.get(), phase=(IQ_phase+phase_shift+self.nv_microwave_phase.get())%1.0, amplitude = self.nv_microwave_amplitude.get())
            
        # with parallel:
        #     self.nv_dds_I.sw.on()
        #     self.nv_dds_Q.sw.on()
        # delay(80*ns)
        # delay(self.nv_microwave_duration.get())
        # with parallel:
        #     self.nv_dds_I.sw.off()
        #     self.nv_dds_Q.sw.off()
        delay_time_code = self.nv_microwave_duration.get()
        if switch_mode == "dds_sw":
            self.nv_dds_I.sw.pulse(delay_time_code)
        elif switch_mode == "ttl":
            self.nv_mw_switch.pulse(delay_time_code)
        
        elif switch_mode == "no pulse":
            pass
        else:
            print("error switch_mode: ", switch_mode)

nv_microwave_fragment = make_fragment_scan_exp(NVMicrowaveFragment)