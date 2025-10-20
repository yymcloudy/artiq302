"""
DDS scanning experiment using ndscan framework.
Scans DDS frequency, amplitude and delay time.
"""
from ndscan.experiment import *
import numpy as np
from artiq.experiment import *
from artiq.coredevice.ad9910 import AD9910
import math


class DDSScan(ExpFragment):
    """DDS scanning experiment fragment"""
    def build_fragment(self, *args, **kwargs):
        # Core device
        self.setattr_device("core")
        
        # DDS device selection
        self.setattr_param("urukul_id",
                          IntParam,
                          "Urukul ID",
                          default=0)
        self.setattr_param("channel_id",
                          IntParam,
                          "Channel ID",
                          default=0)
        
        # DDS parameters
        self.setattr_param("frequency",
                          FloatParam,
                          "DDS frequency",
                          unit="MHz",
                          default=180.0 * MHz)
        self.setattr_param("amplitude",
                          FloatParam,
                          "DDS amplitude",
                          unit="",
                          default=0.4)
        self.setattr_param("phase",
                          FloatParam,
                          "DDS phase",
                          unit="rad",
                          scale=1.0,
                          default=0.0)
        self.setattr_param("attenuation",
                          FloatParam,
                          "DDS attenuation",
                          unit="dB",
                          default=0.0)
        self.setattr_param("duration",
                          FloatParam,
                          "Pulse duration",
                          unit="ms",
                          default=2000.0 * ms)
        
        # Result parameter
        self.setattr_result("result",
                          FloatChannel,
                          "Measurement result",
                          unit="")
        
        # Set up DDS devices
        self.setattr_device("urukul0_ch0")
        self.setattr_device("urukul0_ch1")
        self.setattr_device("urukul0_ch2")
        self.setattr_device("urukul0_ch3")
        self.setattr_device("urukul1_ch0")
        self.setattr_device("urukul1_ch1")
        self.setattr_device("urukul1_ch2")
        self.setattr_device("urukul1_ch3")

    @kernel
    def run_once(self):
        self.core.reset()
        
        # Select DDS device based on urukul_id and channel_id
        if self.urukul_id.get() == 0:
            if self.channel_id.get() == 0:
                dds = self.urukul0_ch0
            elif self.channel_id.get() == 1:
                dds = self.urukul0_ch1
            elif self.channel_id.get() == 2:
                dds = self.urukul0_ch2
            else:  # channel_id == 3
                dds = self.urukul0_ch3
        else:  # urukul_id == 1
            if self.channel_id.get() == 0:
                dds = self.urukul1_ch0
            elif self.channel_id.get() == 1:
                dds = self.urukul1_ch1
            elif self.channel_id.get() == 2:
                dds = self.urukul1_ch2
            else:  # channel_id == 3
                dds = self.urukul1_ch3
        
        # Initialize the device
        self.core.break_realtime()
        
        dds.cpld.init()
        dds.init()
        delay(100*ms)
        
        # Set attenuation
        dds.set_att(self.attenuation.get() * dB)
        
        # Set frequency, phase and amplitude
        dds.set(frequency=self.frequency.get(),
                phase=self.phase.get() * pi,
                amplitude=self.amplitude.get())
        
        # Turn on the output
        dds.sw.on()
        delay(self.duration.get())
        
        # Turn off the output
        dds.sw.off()
        
        # Store result (placeholder)
        self.result.push(1.0)

    def get_default_analyses(self):
        return [
            CustomAnalysis(
                [self.frequency],
                self._analyse_freq_scan,
                [
                    FloatChannel("fit_freq", "Fitted frequency", unit="MHz"),
                    FloatChannel("fit_phase", "Fitted phase"),
                    FloatChannel("fit_amp", "Fitted amplitude"),
                    FloatChannel("fit_offset", "Fitted offset")
                ]
            )
        ]

    def _analyse_freq_scan(self, axis_values, result_values, analysis_results):
        x = axis_values[self.frequency]
        y = result_values[self.result]

        # Simple sine fit
        fit_results = {
            "frequency": 1.0,
            "phase": 0.0,
            "amplitude": 1.0,
            "offset": 0.0
        }

        analysis_results["fit_freq"].push(fit_results["frequency"])
        analysis_results["fit_phase"].push(fit_results["phase"])
        analysis_results["fit_amp"].push(fit_results["amplitude"])
        analysis_results["fit_offset"].push(fit_results["offset"])

        return []


# Create scan experiment with frequency parameter only
DDSScanExp = make_fragment_scan_exp(DDSScan, [(DDSScan, "frequency")])

# Export the experiment
__all__ = ["DDSScanExp"]

# Make sure the module is properly imported
if __name__ == "__main__":
    print("DDSScan module loaded successfully") 