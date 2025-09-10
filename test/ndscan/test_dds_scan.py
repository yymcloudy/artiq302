"""
Test file for DDS scanning experiment.
"""
from ndscan.experiment import *
from artiq.experiment import *
import math
import numpy as np


class DDSScan(ExpFragment):
    """DDS scanning experiment fragment test"""
    def build_fragment(self):
        self.setattr_device("core")   
        # Set up DDS device
        self.setattr_device("urukul0_ch0")
        
        # Set scan parameters
        self.setattr_param("frequency",
                          FloatParam,
                          "Frequency",
                          180.0 * MHz,
                          unit="MHz",
                          min=0.0)
        self.setattr_param("amplitude",
                          FloatParam,
                          "Amplitude",
                          0.4,
                          min=0.0,
                          max=1.0)
        self.setattr_param("duration",
                          FloatParam,
                          "Pulse duration",
                          2000,
                          unit="ms",
                          min=0.0,
                          max=100000)
        # Set fixed parameters
        self.setattr_param("phase",
                          FloatParam,
                          "Phase",
                          0.0)
        self.setattr_param("attenuation",
                          FloatParam,
                          "Attenuation",
                          0.0,
                          unit="dB")
        
        
        # Set result channel
        self.setattr_result("result", FloatChannel, "Measurement result")

    @kernel
    def run_once(self):
        # Initialize DDS
        self.core.reset() 
        self.urukul0_ch0.cpld.init()
        self.urukul0_ch0.init()
        delay(100*ms)
        
        # Set attenuation
        self.urukul0_ch0.set_att(self.attenuation.get() * dB)
        
        # Calculate current frequency and amplitude
        freq = self.frequency.get()
        amp = self.amplitude.get()
        
        # Set DDS parameters
        self.urukul0_ch0.set(frequency=freq*Hz,
                            phase=0.0,
                            amplitude=amp)
        
        # Turn on output
        self.urukul0_ch0.sw.on()
        print(self.duration.get(), freq, amp)
        # delay(self.duration.get() * ms)
        delay(2000*ms)
        # Turn off output
        self.urukul0_ch0.sw.off()
        delay(100*ms)
        # Store result (for demonstration, we'll use amplitude as result)
        self.result.push(amp)
        delay(100*ms)

    def get_default_analyses(self):
        return [
            OnlineFit("sinusoid",
                      data={
                          "x": self.frequency,
                          "y": self.result,
                      },
                      constants={
                          "t_dead": 0,
                      })
        ]


# Create scan experiment
DDSScanExp = make_fragment_scan_exp(DDSScan)
