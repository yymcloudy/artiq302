from artiq.experiment import *
# TTL output test for channels 4 to 15
class TTL_Output_All(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        for i in range(4, 16):
            self.setattr_device(f"ttl{i}")

    @kernel
    def run(self):
        self.core.reset()
        for i in range(4, 16):
            getattr(self, f"ttl{i}").output()
        for j in range(40000):
            # All off
            with parallel:
                for i in range(4, 16):
                    getattr(self, f"ttl{i}").off()
                delay(50*us)
            # All on
            with parallel:
                for i in range(4, 16):
                    getattr(self, f"ttl{i}").on()
                delay(50*us)
            # Even on, odd off
            with parallel:
                for i in range(4, 16):
                    if i % 2 == 0:
                        getattr(self, f"ttl{i}").on()
                    else:
                        getattr(self, f"ttl{i}").off()
                delay(50*us)
            # Odd on, even off
            with parallel:
                for i in range(4, 16):
                    if i % 2 == 1:
                        getattr(self, f"ttl{i}").on()
                    else:
                        getattr(self, f"ttl{i}").off()
                delay(50*us)