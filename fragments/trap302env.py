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

        
        self.nv_dds_I = self.dds_1_0
        self.nv_dds_Q = self.dds_1_1
        self.nv_double_pass_532 = self.dds_1_2

        self.eom_14_7_switch = self.ttl4
        self.eom_2_1_switch = self.ttl5
        self.pmt_ccd_switch = self.ttl6
        self.mw_switch = self.ttl7
        self.ccd_trigger = self.ttl8
        self.magnetic_noise_switch = self.ttl9
        self.flag_experiment = self.ttl10
        self.nv_mw_switch = self.ttl11

    
    def host_setup(self):
        HardwareEnvScan.host_setup(self)

    def prepare(self):
        HardwareEnvScan.prepare(self)


    @kernel
    def device_setup(self):
        """device setup every time before run_once"""
        pass
    

    @kernel
    def device_cleanup(self):
        self.set_idle()

    @kernel
    def init_longtime_equipment(self, pmt_or_ccd_bool=True):
        self.core.break_realtime()
        self.core.reset()
        if pmt_or_ccd_bool:  
            self.pmt_ccd_switch.off()
            delay(5000*ms)
        else:
            self.pmt_ccd_switch.on()
            delay(5000*ms)
    

    @kernel
    def nv_laser_532nm_switch_control(self, switch='on'):
        if switch == 'on':
            self.nv_double_pass_532.sw.on()
        elif switch == 'off':
            self.nv_double_pass_532.sw.off()

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
    def magnetic_noise_switch_control(self, switch=False):
        """
        magnetic noise switch
        """
        if switch:
            self.magnetic_noise_switch.on()
        else:
            self.magnetic_noise_switch.off()


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

        self.laser370_sideband_control(sideband='14.7', enable=True)
        self.laser370_sideband_control(sideband='2.1', enable=False)
        self.laser370_switch_control(switch='on')

        self.double_pass_370.set_att(1.5*dB)
        self.double_pass_370.set(frequency=128*MHz, phase=0.0, amplitude = 0.2) # 2026.4.16我随便写的，有可能出错
        self.double_pass_370.sw.on()
        self.mw_tunefreq.sw.on() # dds source is on

        self.pmt_ccd_switch.on()
        self.mw_switch.off()
        self.magnetic_noise_switch.off()

        # AOM+532nm need to be heated up before use
        self.nv_laser_532nm_switch_control(switch='on')
        self.nv_double_pass_532.set_att(0*dB)
        self.nv_double_pass_532.set(frequency=200*MHz, phase=0.0, amplitude = 0.9) #to do
        
        self.nv_dds_I.sw.off()
        self.nv_dds_Q.sw.off()

        print("Trap302EnvScan Set Idle Done")
    
    @kernel
    def get_sampler(self):
        smp = [0.000]
        self.sampler0.sample(smp)
        return smp[0]
    