from artiq.experiment import *
#sends simple pulses out of the TTL ports; this is done sequentially
#minimum pulse width = 5ns
class TTL_Output_10(EnvExperiment):
    """output_10"""
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl10")

    @kernel
    def run(self):
        self.core.reset()
        self.ttl10.output()
        # self.ttl14.on()
        # delay(2*ms) #delay to prevent RTIO underflow
        # self.ttl14.off()
        for i in range(10_000_000):
            for j in range(20, 40, 10):
                self.ttl10.on()
                delay(40*ns)
                self.ttl10.off()
                delay(2*us)

