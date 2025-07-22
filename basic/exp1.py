from artiq.experiment import *
from artiq.language import delay
from artiq.language.units import ms, us, MHz
import math
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from trapenv import TrapEnv, TrapEnvScan
from ndscan.experiment import *

class Example0(TrapEnvScan):
    """example0_inherit_from_TrapEnvScan"""
    
    def build_fragment(self):
        TrapEnvScan.build_fragment(self)
        print("Example0 Build Done")
    
    @kernel
    def prepare(self):
        TrapEnvScan.prepare(self)
        print("Example0 Prepare Done")
    
    @kernel
    def run_once(self):
        TrapEnvScan.run_once(self)
        print("Example0 Run_Once Done")

# Create scan experiment
Example0Exp = make_fragment_scan_exp(Example0)

class Example1(TrapEnv):
    """example1_inherit_from_TrapEnv"""
    
    def build(self):
        TrapEnv.build(self)
        self.counter = self.ttl0
        self.double_pass_370 = self.dds_0_0
        self.eom_14_7_switch = self.ttl4
        self.eom_2_1_switch = self.ttl5

        self.num = 9
        self.cnt = 99
        print("Example1 Build Done")

    @kernel
    def set_idle(self):
        TrapEnv.set_idle(self)
        delay(100*ms)
        self.double_pass_370.set(frequency=131*MHz,phase=0.0*math.pi, amplitude = 0.4)
        self.double_pass_370.sw.on()
        self.eom_14_7_switch.on()
        self.eom_2_1_switch.off()
        print("Example1 Set_Idle Done")
    
    @kernel
    def cooling(self):
        self.eom_14_7_switch.on()
        self.eom_2_1_switch.off()
        delay(1*ms)

    @kernel
    def pumping(self):
        self.eom_14_7_switch.off()
        self.eom_2_1_switch.on()
        delay(1*ms)

    @kernel
    def detection(self):
        self.eom_14_7_switch.off()
        self.eom_2_1_switch.off()
        delay(1*ms)
        with parallel:
            cnt = self.counter.gate_rising(100*ms)
            num = self.counter.count(cnt)
        print(num)
        delay(10*ms)

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

        n_samples = 50
        data = [0.000] * 8
        
        for i in range(n_samples):
            with parallel:
                cnt = self.counter.gate_rising(100*ms)
                num = self.counter.count(cnt)
            delay(100*ms)
            self.sampler0.sample(data)
            delay(100*ms)
            print(data)
            print(num)
            delay(100*ms)
            #self.mutate_dataset("exp1_data", i, data[1])
            delay(100*ms)
        
        for i in range(n_samples):
            self.cooling()
            self.pumping()
            self.detection()
        
        # Let all devices go back to idle
        self.set_idle()


class Example2(TrapEnv):
    """example2_inherit_from_TrapEnv"""
    
    def build(self):
        TrapEnv.build(self)
        self.counter = self.ttl0
        self.double_pass_370 = self.dds_0_0
        self.eom_14_7_switch = self.ttl4
        self.eom_2_1_switch = self.ttl5

        self.num = 9
        self.cnt = 99
        print("Example1 Build Done")

    @kernel
    def set_idle(self):
        TrapEnv.set_idle(self)
        delay(100*ms)
        self.double_pass_370.set(frequency=131*MHz,phase=0.0*math.pi, amplitude = 0.4)
        self.double_pass_370.sw.on()
        self.eom_14_7_switch.on()
        self.eom_2_1_switch.off()
        print("Example1 Set_Idle Done")
    
    @kernel
    def cooling(self):
        self.eom_14_7_switch.on()
        self.eom_2_1_switch.off()
        delay(1*ms)

    @kernel
    def pumping(self):
        self.eom_14_7_switch.off()
        self.eom_2_1_switch.on()
        delay(1*ms)

    @kernel
    def detection(self):
        self.eom_14_7_switch.off()
        self.eom_2_1_switch.off()
        delay(1*ms)
        with parallel:
            cnt = self.counter.gate_rising(100*ms)
            num = self.counter.count(cnt)
        print(num)
        delay(10*ms)

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

        n_samples = 50
        data = [0.000] * 8
        
        for i in range(n_samples):
            with parallel:
                cnt = self.counter.gate_rising(100*ms)
                num = self.counter.count(cnt)
            delay(100*ms)
            self.sampler0.sample(data)
            delay(100*ms)
            print(data)
            print(num)
            delay(100*ms)
            #self.mutate_dataset("exp1_data", i, data[1])
            delay(100*ms)
        
        for i in range(n_samples):
            self.cooling()
            self.pumping()
            self.detection()
        
        # Let all devices go back to idle
        self.set_idle()