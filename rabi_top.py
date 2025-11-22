from ndscan.experiment import ExpFragment, make_fragment_scan_exp, LinearGenerator
from artiq.language import delay
from artiq.language.units import us

from repository.fragments.rabi import (
    RabiCoolingFragment,
    RabiPumpingFragment,
    RabiPulseFragment,
    RabiDetectionFragment,
)


class RabiTop(ExpFragment):
    """Rabi experiment assembled from modular fragments."""

    def build_fragment(self):
        self.cool = self.setattr_fragment("cool", RabiCoolingFragment)
        self.pump = self.setattr_fragment("pump", RabiPumpingFragment)
        self.pulse = self.setattr_fragment("pulse", RabiPulseFragment)
        self.detect = self.setattr_fragment("detect", RabiDetectionFragment)
        self.detect.link_pulse_fragment(self.pulse)

        self.exp_n = 0
        # self.set_default_scan(
        #     self.pulse.mw_duration, LinearGenerator(10.0, 200.0, 30)
        # )

    def run_once(self):
        self.cool.run_once()
        self.pump.run_once()
        self.pulse.run_once()
        self.detect.run_once()
        delay(100 * us)
        self.exp_n += 1
        print("experiment_num_shots:", self.exp_n)


RabiScan = make_fragment_scan_exp(RabiTop)

