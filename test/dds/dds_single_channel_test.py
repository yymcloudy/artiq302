from artiq.experiment import *
import math

class DDS_Single_Channel_Test(EnvExperiment):
    """dds_single_channel_test"""
    def build(self):
        self.setattr_device("core")
        
        # Add parameters for DDS channel selection
        self.setattr_argument("urukul_id", NumberValue(0, min=0, max=1, step=1, precision=0))
        self.setattr_argument("channel_id", NumberValue(0, min=0, max=3, step=1, precision=0))
        
        # Add parameters for DDS settings
        self.setattr_argument("frequency", NumberValue(180, min=0, max=400, step=1, precision=0))
        self.setattr_argument("amplitude", NumberValue(0.4, min=0, max=1, step=0.1, precision=1))
        self.setattr_argument("phase", NumberValue(0, min=0, max=2, step=0.1, precision=1))
        self.setattr_argument("duration", NumberValue(2000, min=0, max=10000, step=100, precision=0))
        self.setattr_argument("attenuation", NumberValue(0, min=0, max=31.5, step=0.5, precision=1))
        
        # Set up all DDS devices
        self.setattr_device("urukul0_ch0")
        self.setattr_device("urukul0_ch1")
        self.setattr_device("urukul0_ch2")
        self.setattr_device("urukul0_ch3")
        self.setattr_device("urukul1_ch0")
        self.setattr_device("urukul1_ch1")
        self.setattr_device("urukul1_ch2")
        self.setattr_device("urukul1_ch3")

    @kernel
    def run(self):
        self.core.reset()
        
        # Select DDS device based on urukul_id and channel_id
        if self.urukul_id == 0:
            if self.channel_id == 0:
                dds = self.urukul0_ch0
            elif self.channel_id == 1:
                dds = self.urukul0_ch1
            elif self.channel_id == 2:
                dds = self.urukul0_ch2
            else:  # channel_id == 3
                dds = self.urukul0_ch3
        else:  # urukul_id == 1
            if self.channel_id == 0:
                dds = self.urukul1_ch0
            elif self.channel_id == 1:
                dds = self.urukul1_ch1
            elif self.channel_id == 2:
                dds = self.urukul1_ch2
            else:  # channel_id == 3
                dds = self.urukul1_ch3
        
        # Initialize the device
        dds.cpld.init()
        dds.init()
        delay(100*ms)
        
        # Set attenuation
        dds.set_att(self.attenuation * dB)
        
        # Set frequency, phase and amplitude
        dds.set(frequency=self.frequency * MHz,
                phase=self.phase * math.pi,
                amplitude=self.amplitude)
        
        # Turn on the output
        dds.sw.on()
        delay(self.duration*ms)
        
        # Turn off the output
        dds.sw.off()

        # Print current settings (moved outside kernel)
        self.print_settings()

    def print_settings(self):
        print("DDS Settings for Urukul" + "%d" % self.urukul_id + " Channel" + "%d" % self.channel_id + ":")
        print("Frequency: " + "%d" % self.frequency + " MHz")
        print("Amplitude: " + "%.1f" % self.amplitude)
        print("Phase: " + "%.1f" % self.phase + "π")
        print("Attenuation: " + "%.1f" % self.attenuation + " dB")