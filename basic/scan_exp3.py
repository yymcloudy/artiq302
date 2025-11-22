from artiq.experiment import *
from artiq.language import delay
from artiq.language.units import ms, us, MHz#, frequency_to_mu, power_to_mu ,seconds_to_mu
import math
import numpy as np
from numpy import int32
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from trapenv import TrapEnvScan
from ndscan.experiment import *


class BaseSequence_Rabi(TrapEnvScan):
    """rabi mw scan BaseSequence"""
    num_shots = 0
    def build_fragment(self):
        TrapEnvScan.build_fragment(self)
        # add devices
        self.counter = self.ttl0

        self.double_pass_370 = self.dds_0_0
        self.mw_tunefreq = self.dds_0_1

        self.eom_14_7_switch = self.ttl4
        self.eom_2_1_switch = self.ttl5
        self.pmt_ccd_switch = self.ttl6
        self.mw_switch = self.ttl7
        self.laser370_switch = self.ttl8 # not used
        
        # add parameters
        self.setattr_param("double_pass_frequency", FloatParam, "2 pass Frequency", default=133.0*MHz, unit="MHz")
        self.setattr_param("use_pmt_to_detect_or_no", IntParam, "use_pmt_to_detect_or_no", default=1, min=0, max=1)
        self.setattr_param("cooling_time", FloatParam, "Cooling time", default=1000.0*us, unit="us")
        self.setattr_param("pumping_time", FloatParam, "Pumping time", default=100.0*us, unit="us")
        self.setattr_param("detection_time", FloatParam, "Detection time", default=500.0*us, unit="us")
        self.setattr_param("mw_freq", FloatParam, "MW frequency", default=180.0*MHz, unit="MHz")
        self.setattr_param("mw_duration", FloatParam, "MW duration", default=100.0*us, unit="us")
        # add dataset
        # self.setattr_result("counts")
        # self.setattr_dataset("counts", IntChannel)
        self.setattr_result("counts", OpaqueChannel)

        print("BaseSequence Build Done")

    @kernel
    def set_idle(self):
        self.core.reset()
        self.core.break_realtime()

        self.double_pass_370.set_att(1.5*dB)
        self.double_pass_370.set(frequency=self.double_pass_frequency.get(), phase=0.0, amplitude = 0.11)
        self.double_pass_370.sw.on()
        self.mw_tunefreq.sw.off()

        # 未来可删除此行，用于调试
        # self.mw_tunefreq.set(frequency=140*MHz,phase=0.0, amplitude = 0.20)

        self.laser370_sideband_control(sideband='14.7', enable=True)
        self.laser370_sideband_control(sideband='2.1', enable=False)
        self.pmt_ccd_switch.on()
        self.mw_switch.off()
        print("BaseSequence Set Idle Done")

        
    @kernel
    def laser370_switch_control(self, switch='on'):
        """
        laser370 switch
        """
        if switch == 'on':
            with parallel:
                self.double_pass_370.sw.on()
                # self.laser370_switch.on()
        elif switch == 'off':
            with parallel:
                self.double_pass_370.sw.off()
                # self.laser370_switch.off()


    @kernel
    def laser370_sideband_control(self, sideband='14.7', enable=True):
        """
        sideband of laser370: each system has different switch method
        For exanple, at 302 cryogenic trap, sideband of 14.7 GHz is on when ttl is off, and sideband of 2.1 GHz is on when ttl is on
        """
        if sideband == '14.7':
            if enable:
                self.eom_14_7_switch.off()
            else:
                self.eom_14_7_switch.on()
        elif sideband == '2.1':
            if enable:
                self.eom_2_1_switch.on()
            else:
                self.eom_2_1_switch.off()
        elif sideband == 'cooling':
            with parallel:
                self.eom_14_7_switch.off()
                self.eom_2_1_switch.off()
        elif sideband == 'pumping':
            with parallel:
                self.eom_14_7_switch.on()
                self.eom_2_1_switch.on()
        elif sideband == 'detection':
            with parallel:
                self.eom_14_7_switch.on()
                self.eom_2_1_switch.off()

    @kernel
    def prepare(self):
        # self.us_mu = seconds_to_mu(1*us)
        TrapEnvScan.prepare(self)
        # TrapEnvScan.set_idle(self) # to be improved
        self.core.break_realtime()
        self.core.reset()

        # open 370 double pass laser
        self.double_pass_370.set_att(1.5*dB) # to be improved
        self.double_pass_370.set(frequency=133*MHz,phase=0.0, amplitude = 0.11)
        self.double_pass_370.sw.on()

        # self.mw_tunefreq.set(self.mw_freq.get())
        self.mw_tunefreq.set(frequency=self.mw_freq.get(), phase=0.0,amplitude = 0.2)
        self.mw_tunefreq.sw.on()

        self.eom_14_7_switch.off()
        self.eom_2_1_switch.off()
        self.pmt_ccd_switch.off()
        delay(9000*ms)
        print("BaseSequence Prepare Done")
    
    @kernel
    def device_cleanup(self):
        delay(1000*ms)
        self.set_idle()
    
    @kernel
    def cooling(self):
        with parallel:
            self.double_pass_370.set(frequency=self.double_pass_frequency.get(),phase=0.0, amplitude = 0.11)
            self.laser370_sideband_control(sideband='14.7', enable=True)
            self.laser370_sideband_control(sideband='2.1', enable=False)
        self.laser370_switch_control(switch='on')
        delay(self.cooling_time.get())
        self.laser370_switch_control(switch='off')
    
    @kernel
    def pumping(self):
        with parallel:
            self.double_pass_370.set(frequency=self.double_pass_frequency.get(),phase=0.0, amplitude = 0.11)
            self.laser370_sideband_control(sideband='14.7', enable=False)
            self.laser370_sideband_control(sideband='2.1', enable=True)
        self.laser370_switch_control(switch='on')
        delay(self.pumping_time.get())
        self.laser370_switch_control(switch='off')
    
    def _push_counts(self, num):
        self.counts.push(num)
    

    @kernel
    def mw_gate(self):
        self.laser370_switch_control(switch='off')
        self.mw_tunefreq.set(frequency=self.mw_freq.get(), phase=0.0, amplitude = 0.3) # to do: change dds source
        with parallel:
            self.mw_switch.on()
        delay(self.mw_duration.get())
        self.mw_switch.off()

    @kernel
    def detection(self):
        with parallel:
            self.double_pass_370.set(frequency=139*MHz,phase=0.0, amplitude = 0.08)
            self.laser370_sideband_control(sideband='14.7', enable=False)
            self.laser370_sideband_control(sideband='2.1', enable=False)
        self.laser370_switch_control(switch='on')
        with parallel:
            cnt = self.counter.gate_rising(self.detection_time.get())
            num = self.counter.count(cnt)
        delay(100*us)
        self.double_pass_370.set(frequency=self.double_pass_frequency.get(),phase=0.0, amplitude = 0.11)
        
        delay(1*ms)

        # results analysis
        self.core.reset()
        self.core.break_realtime()

        with parallel:
            self.laser370_sideband_control(sideband='14.7', enable=True)
            self.laser370_sideband_control(sideband='2.1', enable=False)
        
        # self._push_counts([self.pumping_time.get(), float(num)])
        self._push_counts([self.mw_duration.get(), self.mw_freq.get(), float(num)])
        print("experiment_num_shots: ", self.num_shots)
        print("optical_num: ", num)
        self.num_shots += 1

    @kernel
    def run_once(self):
        self.core.reset()
        self.core.break_realtime()
        self.cooling()
        self.pumping()
        self.mw_gate()
        self.detection()
        # Longer delay means more safety; shorter delay means faster execution.
        delay(100*us)
        # print("BaseSequence Run_Once Done")
    
    # def analysis(self):
    #     fit.
    #     fit result save to h5

BaseSequenceExp = make_fragment_scan_exp(BaseSequence_Rabi)



