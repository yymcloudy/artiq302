from ndscan.experiment import ExpFragment, FloatParam, IntParam, make_fragment_scan_exp, OpaqueChannel
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.nv_detection import NVDetectionFragment
from repository.fragments.nv_polarization import NVPolarizationFragment
from repository.fragments.nv_microwave import NVMicrowaveFragment

class NVMicrowave_Ramsey_AMP(Trap302EnvScan):
    """NVMicrowave_Ramsey_AMP"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.setattr_result("results", OpaqueChannel)
        self.detection = self.setattr_fragment("detection", NVDetectionFragment)
        self.polarization = self.setattr_fragment("polarization", NVPolarizationFragment)
        # self.microwave_v_amp = self.setattr_fragment("microwave_v_amp", NVMicrowaveFragment)
        self.setattr_param("ramsey_delay", FloatParam, "Ramsey delay", default=5*us, unit="us")
        self.setattr_param("nv_microwave_frequency", FloatParam, "NV Microwave frequency", default=170.0*MHz, unit="MHz")
        self.setattr_param("nv_microwave_duration", FloatParam, "NV Microwave duration", default=1.0*us, unit="us") 
        self.setattr_param("nv_microwave_amplitude", FloatParam, "NV Microwave amplitude", default=0.3, unit="")
        self.setattr_param("nv_microwave_phase", FloatParam, "NV Microwave phase", default=0.0, unit="")
        self.phase_shift_test = 0.0



    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.n_shots = 0
        self.init_longtime_equipment(pmt_or_ccd_bool=True)

    @kernel
    def device_setup(self):
        print("NVMicrowave_Ramsey: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    # @kernel
    # def device_cleanup(self):
    #     Trap302EnvScan.device_cleanup(self)

    @kernel
    def init_longtime_equipment(self, pmt_or_ccd_bool=True):
        self.core.break_realtime()
        Trap302EnvScan.init_longtime_equipment(self, pmt_or_ccd_bool=pmt_or_ccd_bool)    

    @kernel
    def run_once(self):
        # initial
        IQ_phase = 0.78
        self.phase_shift_test = self.ramsey_delay.get() * (1.0 *MHz)
        self.nv_dds_I.set(frequency=self.nv_microwave_frequency.get(), amplitude = 0.0, phase=0.0)
        self.nv_dds_Q.set(frequency=self.nv_microwave_frequency.get(), amplitude = 0.0, phase=IQ_phase%1.0)

        with parallel:
            self.nv_dds_I.sw.on()
            self.nv_dds_Q.sw.on()

        self.n_shots += 1
        self.polarization.run_once()
        nv_count_1 = self.detection.run_once()
        delay(5*us)
        
        # ramsey microwave pulses
        with parallel:
            self.nv_dds_I.set(frequency=self.nv_microwave_frequency.get(), amplitude = self.nv_microwave_amplitude.get(), phase=0.0)
            self.nv_dds_Q.set(frequency=self.nv_microwave_frequency.get(), amplitude = self.nv_microwave_amplitude.get(), phase=IQ_phase%1.0)
        delay(self.nv_microwave_duration.get())
        with parallel:
            self.nv_dds_I.set(frequency=self.nv_microwave_frequency.get(), amplitude = 0.0, phase = 0.0)
            self.nv_dds_Q.set(frequency=self.nv_microwave_frequency.get(), amplitude = 0.0, phase = IQ_phase%1.0)

        delay(self.ramsey_delay.get())

        

        with parallel:
            self.nv_dds_I.set(frequency=self.nv_microwave_frequency.get(), amplitude = self.nv_microwave_amplitude.get(), phase=self.phase_shift_test%1.0)
            self.nv_dds_Q.set(frequency=self.nv_microwave_frequency.get(), amplitude = self.nv_microwave_amplitude.get(), phase=(IQ_phase+self.phase_shift_test)%1.0)
        delay(self.nv_microwave_duration.get())
        with parallel:
            self.nv_dds_I.set(frequency=self.nv_microwave_frequency.get(), amplitude = 0.0, phase = 0.0)
            self.nv_dds_Q.set(frequency=self.nv_microwave_frequency.get(), amplitude = 0.0, phase = IQ_phase%1.0)



        ############
        nv_count_2 = self.detection.run_once()

        print("n_shots: ", self.n_shots)
        self.results.push([float(nv_count_1), float(nv_count_2)])


nv_microwave_ramsey_amp = make_fragment_scan_exp(NVMicrowave_Ramsey_AMP) 