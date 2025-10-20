"""
New DDS scanning experiment with improved hardware compatibility.
"""
from ndscan.experiment import *
from artiq.experiment import *
import math


class DDSScanNew(ExpFragment):
    """DDS scanning experiment fragment with improved hardware compatibility"""
    def build_fragment(self):
        # Set up devices
        self.setattr_device("core")
        self.setattr_device("urukul0_ch0")
        
        # Set scan parameters
        self.setattr_param("frequency",
                          FloatParam,
                          "Frequency",
                          unit="MHz",
                          default=180.0 * MHz,
                          min=0.0)
        self.setattr_param("amplitude",
                          FloatParam,
                          "Amplitude",
                          default=0.4,
                          min=0.0,
                          max=1.0)
        
        # Set fixed parameters
        self.setattr_param("phase",
                          FloatParam,
                          "Phase",
                          default=0.0)
        self.setattr_param("attenuation",
                          FloatParam,
                          "Attenuation",
                          unit="dB",
                          default=0.0)
        self.setattr_param("duration",
                          FloatParam,
                          "Pulse duration",
                          unit="ms",
                          default=1000.0)
        
        # Set result channel
        self.setattr_result("result", FloatChannel, "Measurement result")

    @kernel
    def prepare(self):
        """Initialize DDS once before scanning"""
        self.core.reset()
        self.urukul0_ch0.cpld.init()
        self.urukul0_ch0.init()
        delay(100*ms)
        
        # Set initial attenuation
        self.urukul0_ch0.set_att(self.attenuation.get() * dB)
        delay(200*ms)

    @kernel
    def run(self):
        # Set DDS parameters
        self.prepare()
        self.urukul0_ch0.set(frequency=self.frequency.get(),
                            phase=self.phase.get(),
                            amplitude=self.amplitude.get())
        delay(2000*ms)
        # Turn on output
        self.urukul0_ch0.sw.on()
        # delay(self.duration.get() * ms)
        delay(10000*ms)
        # Turn off output
        self.urukul0_ch0.sw.off()
        
        # Store result (for demonstration, we'll use amplitude as result)
        self.result.push(self.amplitude.get())
        delay(1000*ms)

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
DDSScanNewExp = make_fragment_scan_exp(DDSScanNew) 