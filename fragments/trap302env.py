from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

from repository.fragments.hwenv import HardwareEnvScan

class Trap302EnvScan(HardwareEnvScan):
    """trap302env_scan"""
    def build_fragment(self):
        """Here we list all the devices used in the trap302env_scan
        - counter: ttl0
        - control_aom_double_pass_370_laser: dds_0_0
        - microwave_frequency_tuner: dds_0_1
        - control_eom_14_7_switch: ttl4
        - control_eom_2_1_switch: ttl5
        - pmt_ccd_switch: ttl6
        - microwave_switch: ttl7
        """
        HardwareEnvScan.build_fragment(self)
        self.counter = self.ttl0

        self.double_pass_370 = self.dds_0_0
        self.mw_tunefreq = self.dds_0_1

        self.eom_14_7_switch = self.ttl4
        self.eom_2_1_switch = self.ttl5
        self.pmt_ccd_switch = self.ttl6
        self.mw_switch = self.ttl7
    
    def host_setup(self):
        HardwareEnvScan.host_setup(self)

    def prepare(self):
        HardwareEnvScan.prepare(self)


    @kernel
    def device_setup(self):
        pass
    
    @kernel
    def laser370_switch_control(self, switch='on'):
        """
        laser370 switch
        """
        if switch == 'on':
            self.double_pass_370.sw.on()
        elif switch == 'off':
            self.double_pass_370.sw.off()

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
    def set_idle(self):
        """set idle, this state is used for trapping 171Yb+ ions"""
        self.core.reset()
        self.core.break_realtime()

        self.laser370_switch_control(switch='on')
        self.laser370_sideband_control(sideband='14.7', enable=True)
        self.laser370_sideband_control(sideband='2.1', enable=False)

        self.double_pass_370.set_att(1.5*dB)
        self.double_pass_370.set(frequency=133*MHz, phase=0.0, amplitude = 0.11)
        self.double_pass_370.sw.on()
        self.mw_tunefreq.sw.on() # dds source is on

        self.pmt_ccd_switch.on()
        self.mw_switch.off()

        print("Trap302EnvScan Set Idle Done")

