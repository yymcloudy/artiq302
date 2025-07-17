from artiq.experiment import *

class TTL_input(EnvExperiment):
    """
    pmt_count
    """
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl2")
        self.setattr_device("ttl13")

        pmt_init = [0 for _ in range(50)]
        self.setattr_dataset("pmt_readlist", pmt_init)

    @kernel
    def run(self):
        self.core.reset()
        self.ttl2.input()
        self.ttl13.output()
        self.core.break_realtime()
        pmt_temp = [0 for _ in range(50)]
        pmt_temp[1] = 500
        self.set_dataset("pmt_readlist", pmt_temp, broadcast=True)
        while True:
            delay(10*ms)
            with parallel:
                cnt = self.ttl2.gate_rising(100*ms)
                num = self.ttl2.count(cnt)
            
            pmt_temp[2:-1] = pmt_temp[3:]
            pmt_temp[-1] = num
            self.set_dataset("pmt_readlist", pmt_temp, broadcast=True)

            delay(100*ms)
            print(num)
        # print(h)