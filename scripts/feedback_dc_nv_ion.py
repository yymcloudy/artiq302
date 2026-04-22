from cmath import phase
from ndscan.experiment import ExpFragment, FloatParam, IntParam, make_fragment_scan_exp, OpaqueChannel
from artiq.experiment import kernel
from artiq.experiment import NumberValue

from artiq.language.units import *
from artiq.language import delay, sequential

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.nv_detection import NVDetectionFragment
from repository.fragments.nv_polarization import NVPolarizationFragment
from repository.fragments.nv_microwave import NVMicrowaveFragment


from repository.fragments.doppler_cooling import DopplerCoolingFragment
from repository.fragments.pumping import PumpingFragment
from repository.fragments.detection import DetectionFragment
from repository.fragments.microwave import MicrowaveFragment
from repository.fragments.magnetic_gen import MagneticGenFragment   

class FeedbackDCNVIon(Trap302EnvScan):
    """Feedback_DC_NV_Ion"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.ion_doppler_cooling = self.setattr_fragment("doppler_cooling", DopplerCoolingFragment)
        self.ion_pumping = self.setattr_fragment("pumping", PumpingFragment)
        self.ion_microwave_1 = self.setattr_fragment("ion_microwave_1", MicrowaveFragment)
        self.ion_microwave_2 = self.setattr_fragment("ion_microwave_2", MicrowaveFragment)
        self.ion_detection = self.setattr_fragment("detection", DetectionFragment)

        self.magnetic_gen = self.setattr_fragment("magnetic_gen", MagneticGenFragment)

        self.nv_polarization = self.setattr_fragment("nv_polarization", NVPolarizationFragment)
        self.nv_microwave = self.setattr_fragment("nv_microwave", NVMicrowaveFragment)
        self.nv_detection = self.setattr_fragment("nv_detection", NVDetectionFragment)

        self.setattr_result("results", OpaqueChannel)
        self.setattr_param("ion_evolution_time", FloatParam, "Ion evolution time", default=20.0*us, unit="us")
        self.setattr_argument("dds_switch_mode_idx", NumberValue(0, min=0, max=1, step=1, precision=0)) # for nv

    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.init_longtime_equipment(pmt_or_ccd_bool=True)
        self.n_shots = 0
        self.dds_switch_mode = ["dds_sw", "ttl"][int(self.dds_switch_mode_idx)]
        print("nv_microwave_dds_switch_mode: ", self.dds_switch_mode)

        self.magnetic_noise_type = "random_number"

    @kernel
    def device_setup(self):
        print("Feedback-DC-NV-Ion: Device Setup")
        self.core.break_realtime()
        self.core.reset()
        self.device_setup_nv_dds(dds_switch_mode=self.dds_switch_mode)

    @kernel
    def device_setup_nv_dds(self, dds_switch_mode="dds_sw"):
        self.nv_microwave.run_once(set=True, switch_mode="no pulse")
        if dds_switch_mode == "dds_sw":
            self.nv_mw_switch.on() # It will always be "on" during the whole experiment.
            self.nv_dds_I.sw.off()
            self.nv_dds_Q.sw.off()
        elif dds_switch_mode == "ttl":
            self.nv_mw_switch.off()
            self.nv_dds_I.sw.on() # It will always be "on" during the whole experiment.
            self.nv_dds_Q.sw.on() # It will always be "on" during the whole experiment.
    
    @kernel
    def init_longtime_equipment(self, pmt_or_ccd_bool=True):
        self.core.break_realtime()
        Trap302EnvScan.init_longtime_equipment(self, pmt_or_ccd_bool=pmt_or_ccd_bool)
    
    @kernel
    def run_once(self):
        
        if self.magnetic_noise_type == "random_number":
            # ramdom-number-generator-magnetic field 
            self.ttl9.off()
            delay(1*us)
            self.ttl9.on()
            delay(1*us)
            self.ttl9.off()
            delay(20*ms)
        else:
            pass

        
        # initializaton
        with parallel:
            with sequential:
                delay(19.8*ms)
                self.ion_doppler_cooling.run_once()
                self.ion_pumping.run_once()
            with sequential:
                self.nv_polarization.run_once(dds_switch_mode=self.dds_switch_mode)
                nv_count_1 = self.nv_detection.run_once(dds_switch_mode=self.dds_switch_mode, measure_shots=4)
        
        # Experiment Sequence
        with parallel:
            with sequential:
                self.ion_microwave_1.run_once()
                delay(self.ion_evolution_time.get())
            with sequential:
                self.nv_microwave.run_once(set=True, switch_mode="no pulse")
                self.nv_polarization.run_once(dds_switch_mode=self.dds_switch_mode)
                nv_count_2 = self.nv_detection.run_once(dds_switch_mode=self.dds_switch_mode, measure_shots=4)
        alpha = 0.01
        beta = 0.5
        phase_shift = (nv_count_2 - nv_count_1 - alpha) * beta
        self.ion_microwave_2.run_once(phase_shift=phase_shift)
        self.ion_detection.run_once()
        delay(100*us)

        self.n_shots += 1
        print("n_shots: ", self.n_shots)
        self.results.push([float(self.n_shots)])

feedback_dc_nv_ion = make_fragment_scan_exp(FeedbackDCNVIon) 