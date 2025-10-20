from artiq.experiment import *
#sends simple pulses out of the TTL ports; this is done sequentially
#minimum pulse width = 5ns
class TTL_Output(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl12")
        self.setattr_device("ttl14")
        self.setattr_device("ttl15")
        self.setattr_device("ttl1")
    @kernel
    def run(self):
        self.core.reset()
        self.ttl12.output()
        self.ttl14.output()
        self.ttl15.output()
        self.ttl1.output()
    
        # self.ttl1.on()
        # delay(2*ms) #delay to prevent RTIO underflow
        # self.ttl1.off()
        for i in range(40000):
        # while True:
            # self.ttl12.pulse(5*us)

            # 0
            with parallel:
                self.ttl12.off()
                self.ttl14.off()
                self.ttl15.off()
                delay(50*us)
            # 7
            with parallel:
                self.ttl12.on()
                self.ttl14.on()
                self.ttl15.on()
                self.ttl1.on()
                delay(50*us)
            # 1
            with parallel:
                self.ttl12.off()
                self.ttl14.off()
                self.ttl15.off()
                delay(50*us)
            # 6
            with parallel:
                self.ttl12.off()
                self.ttl14.off()
                self.ttl15.on()
                delay(50*us)
            # 2
            with parallel:
                self.ttl12.on()
                self.ttl14.off()
                self.ttl15.off()
                delay(50*us)
            # 5
            with parallel:
                self.ttl12.on()
                self.ttl14.on()
                self.ttl15.on()
                delay(50*us)
            # 3
            with parallel:
                self.ttl12.off()
                self.ttl14.on()
                self.ttl15.off()
                delay(50*us)
            # 4
            with parallel:
                self.ttl12.on()
                self.ttl14.off()
                self.ttl15.on()
                self.ttl1.off()
                delay(50*us)




            # delay(5*us)
            # self.ttl14.pulse(5*us)
            # delay(10*us)
            # self.ttl14.pulse(10*us)

