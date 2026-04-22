from ndscan.experiment import ExpFragment, FloatParam, IntParam, make_fragment_scan_exp
from artiq.experiment import kernel
from artiq.experiment import TInt32
import random
from artiq.language.units import *
from artiq.language import delay, now_mu

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.doppler_cooling import DopplerCoolingFragment
from repository.fragments.pumping import PumpingFragment
from repository.fragments.detection import DetectionFragment
from repository.fragments.microwave import MicrowaveFragment
from repository.fragments.magnetic_gen import MagneticGenFragment   



class MW_Ramsey_DC_Feedback(Trap302EnvScan):
    """MW_Ramsey_DC_Feedback"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.doppler_cooling = self.setattr_fragment("doppler_cooling", DopplerCoolingFragment)
        self.pumping = self.setattr_fragment("pumping", PumpingFragment)
        self.microwave_1 = self.setattr_fragment("microwave_1", MicrowaveFragment)
        self.microwave_2 = self.setattr_fragment("microwave_2", MicrowaveFragment)
        self.detection = self.setattr_fragment("detection", DetectionFragment)
        self.magnetic_gen = self.setattr_fragment("magnetic_gen", MagneticGenFragment)
        self.setattr_param("evolution_time", FloatParam, "Evolution time", default=20.0*us, unit="us")
        self.setattr_param("detune_freq", FloatParam, "Detune frequency", default=1*kHz, unit="kHz")

    
    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.init_longtime_equipment(pmt_or_ccd_bool=True)
        self.n_shots = 0


    @kernel
    def device_setup(self):
        print("MW_Ramsey_DC_Feedback: Device Setup")
        self.core.break_realtime()
        self.core.reset()



    @kernel
    def run_once(self):
        self.core.break_realtime()
        self.core.reset()

        # drive the TTL port to change the voltage
        self.ttl9.off()
        delay(1*us)
        self.ttl9.on()
        delay(1*us)
        self.ttl9.off()
        delay(10*us)

        data = [0.000] * 8


        self.doppler_cooling.run_once()
        self.pumping.run_once()
        self.microwave_1.run_once()
        delay(self.evolution_time.get())
        # phase_shift = self.second_pulse_phase.get()
        phase_shift = 0.0

        self.sampler0.sample(data)
        voltage_driven = data[6]
        alpha = 1.0
        voltage_offset = 1.4
        phase_shift = (voltage_driven - voltage_offset) * alpha
        delay(10*us)
        
        self.microwave_2.run_once(phase_shift=phase_shift)
        self.detection.run_once()
        delay(100*us)
        self.n_shots += 1
        print("n_shots: ", self.n_shots)
        print("voltage_driven: ", voltage_driven)
        print("phase_shift: ", phase_shift)

mw_ramsey = make_fragment_scan_exp(MW_Ramsey_DC_Feedback)