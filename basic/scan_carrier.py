from artiq.experiment import *
from artiq.language import delay
from artiq.language.units import ms, us, MHz
# seconds_to_mu, frequency_to_mu, power_to_mu
import math
import numpy as np
from numpy import int32
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from trapenv import TrapEnvScan
from ndscan.experiment import *


class BaseSequence_Carrier(TrapEnvScan):
    """carrier frequency scan code"""
    # This sequence contains the 2 stage of cooling subsequence.
    # The first stage is the cooling subsequence, which is used to cool the atom to the ground state.
    # The second stage is scanning the frequence of the carrier, making the counts attached to the maximum.
    
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
        self.laser370_switch = self.ttl8 
        
        # add parameters
        # self.setattr_param("frequency", FloatParam, "Frequency", default=180.0*MHz, unit="MHz")
        self.setattr_param("use_pmt_to_detect_or_no", IntParam, "use_pmt_to_detect_or_no", default=1, min=0, max=1)
        self.setattr_param("cooling_time", FloatParam, "Cooling time", default=1000.0*us, unit="us")
        self.setattr_param("carrier_scan_time", FloatParam, "Carrier scan time", default=50.0*us, unit="us")
        self.setattr_param("carrier_scan_freq", FloatParam, "Carrier scan frequency", default=180.0*MHz, unit="MHz")
        # add dataset
        # self.setattr_result("counts")
        # self.setattr_dataset("counts", IntChannel)
        self.setattr_result("counts", OpaqueChannel)

        print("BaseSequence Build Done")


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
        TrapEnvScan.prepare(self)
        # TrapEnvScan.set_idle(self) # to be improved
        self.core.break_realtime()
        self.core.reset()

        # open 370 double pass laser
        self.double_pass_370.set_att(1.5*dB) # to be improved
        self.double_pass_370.set(frequency=130*MHz,phase=0.0, amplitude = 0.1)
        self.double_pass_370.sw.on()

        self.eom_14_7_switch.off()
        self.eom_2_1_switch.off()
        self.pmt_ccd_switch.off()
        delay(9000*ms)
        print("BaseSequence Prepare Done")
    
    @kernel
    def device_cleanup(self):
        delay(1000*ms)
        self.double_pass_370.set_att(1.5*dB)
        self.double_pass_370.set(frequency=133*MHz,phase=0.0, amplitude = 0.1)
        self.double_pass_370.sw.on()
        self.laser370_sideband_control(sideband='14.7', enable=True)
        self.laser370_sideband_control(sideband='2.1', enable=False)
        self.pmt_ccd_switch.on()
        print("BaseSequence Device Cleanup Done")
    
    @kernel
    def cooling(self):
        self.laser370_switch_control(switch='on')
        with parallel:
            self.laser370_sideband_control(sideband='14.7', enable=True)
            self.laser370_sideband_control(sideband='2.1', enable=False)
            self.double_pass_370.set(frequency=133*MHz,phase=0.0, amplitude = 0.11)
        delay(self.cooling_time.get())

    def _push_counts(self, num):
        self.counts.push(num)

    @kernel
    def carrier_scan(self):
        with parallel:
            self.laser370_sideband_control(sideband='14.7', enable=False)
            self.laser370_sideband_control(sideband='2.1', enable=False)
            self.double_pass_370.set(frequency=self.carrier_scan_freq.get(),phase=0.0, amplitude = 0.1)
        self.laser370_switch_control(switch='on')
        with parallel:
            cnt = self.counter.gate_rising(self.carrier_scan_time.get())
            num = self.counter.count(cnt)
        delay(1*ms)

        self.core.reset()
        self.core.break_realtime()
        self._push_counts([self.carrier_scan_freq.get(), float(num)])


    @kernel
    def run_once(self):
        self.core.reset()
        self.core.break_realtime()
        self.cooling()
        self.carrier_scan()
        delay(100*us)
        self.num_shots += 1
        print("this is the ", self.num_shots," experiment.")
        print("BaseSequence_Carrier Run_Once Done")

BaseSequence_CarrierExp = make_fragment_scan_exp(BaseSequence_Carrier)

