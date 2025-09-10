from artiq.experiment import *

class TTL_input(EnvExperiment):
    """
    ttl0->3 arbitrary_input_channel_count
    """
    def build(self):
        self.setattr_device("core")
        
        # Add parameter for TTL channel selection
        self.setattr_argument("ttl_channel", NumberValue(0, min=0, max=3, step=1, precision=0))
    
        # 设置所有的设备
        self.setattr_device("ttl0")
        self.setattr_device("ttl1")
        self.setattr_device("ttl2")
        self.setattr_device("ttl3")

        pmt_init = [0 for _ in range(50)]
        self.setattr_dataset("pmt_readlist", pmt_init)

    @kernel
    def run(self):
        self.core.reset()
        # 使用if-else选择TTL设备
        if self.ttl_channel == 0:
            ttl = self.ttl0
        elif self.ttl_channel == 1:
            ttl = self.ttl1
        elif self.ttl_channel == 2:
            ttl = self.ttl2
        else:  # self.ttl_channel == 3
            ttl = self.ttl3
        ttl.input()
        self.core.break_realtime()
        pmt_temp = [0 for _ in range(50)]
        pmt_temp[1] = 500
        self.set_dataset("pmt_readlist", pmt_temp, broadcast=True)
        while True:
            delay(10*ms)
            with parallel:
                cnt = ttl.gate_rising(100*ms)
                num = ttl.count(cnt)
            
            pmt_temp[2:-1] = pmt_temp[3:]
            pmt_temp[-1] = num
            self.set_dataset("pmt_readlist", pmt_temp, broadcast=True)

            delay(100*ms)
            print(num) 