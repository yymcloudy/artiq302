from ndscan.experiment import ExpFragment, FloatParam, IntParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.trap302env import Trap302EnvScan

from repository.fragments.doppler_cooling import DopplerCoolingFragment
from repository.fragments.pumping import PumpingFragment
from repository.fragments.detection import DetectionADCFragment
from repository.fragments.microwave import MicrowaveFragment

class MicroWave_Rabi_DC_noise(Trap302EnvScan):
    """MW_Rabi_DC_noise"""
    def build_fragment(self):
        Trap302EnvScan.build_fragment(self)
        self.doppler_cooling = self.setattr_fragment("doppler_cooling", DopplerCoolingFragment)
        self.pumping = self.setattr_fragment("pumping", PumpingFragment)
        self.detection = self.setattr_fragment("detection", DetectionADCFragment)
        self.microwave = self.setattr_fragment("microwave", MicrowaveFragment)

        self.setattr_param("pi_pulse_number", IntParam, "Pi pulse number", default=1, unit="")
    def prepare(self):
        Trap302EnvScan.prepare(self)
        self.n_shots = 0
        self.init_longtime_equipment(pmt=True)

    @kernel
    def device_setup(self):
        print("MicroWave_Rabi_DC_noise: Device Setup")
        self.core.break_realtime()
        self.core.reset()

    # @kernel
    # def device_cleanup(self):
    #     Trap302EnvScan.device_cleanup(self)

    @kernel
    def init_longtime_equipment(self, pmt=True):
        self.core.break_realtime()
        self.double_pass_370.set_att(1.5*dB)
        Trap302EnvScan.init_longtime_equipment(self, pmt=True)    

    @kernel
    def run_once(self):
        #sample the voltage
        data = [0.000] * 8
        self.sampler0.sample(data)
        voltage_driven = data[6]

        alpha = 1
        beta = -0.00453851
        voltage_offset = 0.0200958
        frequency_shift = beta*(voltage_driven - voltage_offset)

        beta2 = -0.000120802
        voltage_offset2 = 4.94527
        frequency_shift = frequency_shift + beta2*(voltage_driven - voltage_offset2)
        frequency_shift = alpha*frequency_shift
        delay(1000*us)

        # frequency_shift = 0

        self.doppler_cooling.run_once()
        self.pumping.run_once()
        self.microwave.run_once(frequency_shift=frequency_shift*MHz)
        self.detection.run_once()
        delay(100*us)
        self.n_shots += 1
        print("n_shots: ", self.n_shots)
        # print("voltage_driven: ", voltage_driven)
        print("frequency_shift: ", frequency_shift)

microwave_rabi_dc_noise = make_fragment_scan_exp(MicroWave_Rabi_DC_noise) 