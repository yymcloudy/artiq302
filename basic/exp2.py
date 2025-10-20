from artiq.experiment import *
from artiq.language import delay
from artiq.language.units import ms, us, MHz
# seconds_to_mu, frequency_to_mu, power_to_mu
import math
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from trapenv import TrapEnv, TrapEnvScan
from ndscan.experiment import *


class Example2(TrapEnv):
    """example2_inherit_from_TrapEnv_for_simple_experiment"""
    def prepare(self):
        # self.ms_mu = seconds_to_mu(100*ms)
        ...
    
    def build(self):
        TrapEnv.build(self)
        self.counter = self.ttl0
        self.double_pass_370 = self.dds_0_0
        self.eom_14_7_switch = self.ttl4
        self.eom_2_1_switch = self.ttl5

        self.num = 9
        self.cnt = 99
        print("Example2 Build Done")

    @kernel
    def set_idle(self):
        TrapEnv.set_idle(self)
        delay(100*ms)
        self.double_pass_370.set(frequency=131*MHz,phase=0.0*math.pi, amplitude = 0.4)
        self.double_pass_370.sw.on()
        self.eom_14_7_switch.off()
        self.eom_2_1_switch.off()
        print("Example2 Set_Idle Done")
    
    @kernel
    def cooling(self):
        # with parallel:
        #     self.eom_14_7_switch.on()
        #     self.eom_2_1_switch.off() 
        self.eom_14_7_switch.off()
        self.eom_2_1_switch.off()
        delay(100*ms)

    @kernel
    def pumping(self):
        self.eom_14_7_switch.on()
        self.eom_2_1_switch.on()
        delay(500*us)

    @kernel
    def detection(self):
        self.eom_14_7_switch.on()
        self.eom_2_1_switch.off()

        data = np.array([0]*10)

        # delay(500*us)
        with parallel:
            cnt = self.counter.gate_rising(100*us)
            num = self.counter.count(cnt)
            print(num)
            data[0]=num
        delay(100*us)

    @kernel
    def sample_data(self):
        data = [0.000] * 8
        self.sampler0.sample(data)
        print(data)

    @kernel
    def run(self):
        """
        运行实验
        """
        # 初始化所有设备
        self.force_init_all()
        self.set_idle()

        self.core.reset()
        self.core.break_realtime()

        n_samples = 10000
        data = [0.000] * 8
        numlist = np.array([0.000] * 10)
        
        # for i in range(n_samples):
        #     with parallel:
        #         cnt = self.counter.gate_rising(100*ms)
        #         num = self.counter.count(cnt)
        #     delay(100*ms)
        #     self.sampler0.sample(data)
        #     delay(100*ms)
        #     print(data)
        #     print(num)
        #     delay(100*ms)
        #     # delay_mu(100 * self.ms_mu)
        #     # delay(100*mu)
        #     #self.mutate_dataset("exp1_data", i, data[1])
        #     delay(100*ms)
        
        for i in range(n_samples):
            self.cooling()
            self.pumping()
            self.detection()
            print(i)
            delay(10*ms)
        
        # Let all devices go back to idle
        self.set_idle()