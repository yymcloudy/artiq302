from ndscan.experiment import ExpFragment, FloatParam, IntParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay, now_mu

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.nv_detection import NVDetectionFragment
from repository.fragments.nv_polarization import NVPolarizationFragment
from repository.fragments.nv_microwave import NVMicrowaveFragment
from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING, PHASE_MODE_ABSOLUTE, PHASE_MODE_CONTINUOUS

class NVESRFragment(Trap302EnvScan):
    """nv_esr_fragment"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_param("nv_esr_frequency", FloatParam, "NV ESR frequency", default=170.0*MHz, unit="MHz")
        self.setattr_param("nv_esr_duration", FloatParam, "NV ESR duration", default=1.0*us, unit="us") 
        self.setattr_param("nv_esr_amplitude", FloatParam, "NV ESR amplitude", default=0.4, unit="")
        self.setattr_param("nv_esr_phase", FloatParam, "NV ESR phase", default=0.0, unit="")

    @kernel
    def device_setup(self):
        print("NVESRFragment: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    @kernel
    def run_once(self):
        data = [0.000] * 8
        T = now_mu()
        # self.nv_double_pass_532.set_att(0.0*dB)
        # self.nv_double_pass_532.set(frequency=220*MHz, phase=0.0, amplitude = 0.2)
        self.nv_dds_I.set(frequency=self.nv_esr_frequency.get(), phase=0.0, amplitude = self.nv_esr_amplitude.get(), phase_mode=PHASE_MODE_TRACKING, ref_time_mu=T)
        self.nv_dds_Q.set(frequency=self.nv_esr_frequency.get(), phase=0.0, amplitude = self.nv_esr_amplitude.get(), phase_mode=PHASE_MODE_TRACKING, ref_time_mu=T)
        
        self.nv_mw_switch.on()
        self.nv_double_pass_532.sw.on()
        with parallel:
            self.nv_dds_I.sw.on()
            self.nv_dds_Q.sw.on()

        delay(self.nv_esr_duration.get())
        self.sampler0.sample(data)
        esr_count = data[7]
        delay(1000*us) # insure RTIO

        with parallel:
            self.nv_dds_I.sw.off()
            self.nv_dds_Q.sw.off()
        self.nv_double_pass_532.sw.off()
        self.nv_mw_switch.off()

        print("esr_count: ", esr_count)
        return esr_count



nv_esr_fragment = make_fragment_scan_exp(NVESRFragment) 