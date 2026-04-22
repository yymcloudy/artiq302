from artiq.experiment import *
#sends simple pulses out of the TTL ports; this is done sequentially
#minimum pulse width = 5ns
class TTL_Output_one(EnvExperiment):
    """output_one"""
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl11")

    @kernel
    def run(self):
        self.core.reset()
        self.ttl11.output()
        # self.ttl14.on()
        # delay(2*ms) #delay to prevent RTIO underflow
        # self.ttl14.off()
        for i in range(10_000_000):
            for j in range(20, 40, 10):
                self.ttl11.on()
                delay(200*ns)
                self.ttl11.off()
                delay(2000*ns)

