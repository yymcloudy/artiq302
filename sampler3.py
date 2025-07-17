from artiq.experiment import *
import numpy as np

class SamplerTest(EnvExperiment):
    """Sampler Test"""

    def build(self):
        self.setattr_device("core")
        self.setattr_device("sampler0")

    @kernel
    def run(self):
        g = 0 # gain in mu

        self.core.reset()
        self.core.break_realtime()
        self.sampler0.init()
        delay(10*ms)
        # gains = self.sampler0.get_gains_mu()
        # print("Gains: ", gains)
        delay(10*ms)
        for i in range(8):
            delay(1*ms)
            self.sampler0.set_gain_mu(i, g) # set gain on Sampler channel i to 10**g

        delay(10*ms)
        
        # self.sampler2.get_gains_mu() returns all the gains as a int32
        # gains = self.sampler0.get_gains_mu()
        # delay(1*ms)
        # print("Gains: ", gains)
        delay(100*ms)
        for i in range(8):
            mask = (0b11 << (2*i)) # mask to extract gain of channel i, gains are 2 bits per channel
            print("Sampler channel ", i, " gain: ", (g & mask) >> (2*i))
            delay(100*ms)

        # initialize data container
        data = [0.0]*8

        # collect and show data
        self.sampler0.sample(data)
        for i in range(8):
            print("Voltage ", i, ": ", data[i], " V")
            delay(100*ms)