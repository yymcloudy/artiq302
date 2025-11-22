from ndscan.experiment import ExpFragment, FloatParam, OpaqueChannel
from artiq.experiment import kernel, parallel
from artiq.language.units import us, MHz, ms
from artiq.language import delay
from artiq.experiment import*

class ReadoutFragment(ExpFragment):
    def build_fragment(self):
        self.setattr_device("core")
        self.counter = self.get_device("ttl0")
        self.double_pass_370 = self.get_device("urukul0_ch0")

        self.eom_14_7_switch = self.get_device("ttl4")
        self.eom_2_1_switch = self.get_device("ttl5")
        
        self.setattr_param("t_readout", FloatParam, "Readout time", default=500.0, unit="us")
        self.setattr_param("double_pass_frequency", FloatParam, "2 pass Frequency", default=133.0, unit="MHz")
        self.setattr_result("counts", OpaqueChannel, "Photon counts")
    
    @kernel
    def device_setup(self):
        self.core.break_realtime()
        self.double_pass_370.cpld.init()
        self.double_pass_370.init()
        self.double_pass_370.set_att(0*dB)
        self.counter.input()
        self.eom_14_7_switch.output()
        self.eom_2_1_switch.output()
        delay(1000*us)
    
    @kernel
    def laser370_switch_control(self, switch='on'):
        """laser370 switch"""
        if switch == 'on':
            with parallel:
                self.double_pass_370.sw.on()
        elif switch == 'off':
            with parallel:
                self.double_pass_370.sw.off()
    
    @kernel
    def laser370_sideband_control(self, sideband='14.7', enable=True):
        """sideband of laser370"""
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
    
    def _push_counts(self, num):
        self.counts.push([float(num)])
    
    @kernel
    def run_once(self):
        # Setup detection laser: set frequency and sideband control in parallel
        self.core.reset()
        self.core.break_realtime()
        with parallel:
            self.laser370_sideband_control(sideband='14.7', enable=False)
            self.laser370_sideband_control(sideband='2.1', enable=False)
        self.double_pass_370.set(frequency=139*MHz, phase=0.0, amplitude=0.2)
        # Turn on laser
        self.laser370_switch_control(switch='on')
        
        # Gate counter and count in parallel
        with parallel:
            cnt = self.counter.gate_rising(self.t_readout.get() * us)
            num = self.counter.count(cnt)
        
        delay(100 * us)
        
        # Reset to cooling frequency
        self.double_pass_370.set(frequency=self.double_pass_frequency.get()*MHz, phase=0.0, amplitude=0.11)
        delay(1 * ms)
        
        # Reset core and break realtime
        self.core.reset()
        self.core.break_realtime()
        
        # Restore sideband settings
        with parallel:
            self.laser370_sideband_control(sideband='14.7', enable=True)
            self.laser370_sideband_control(sideband='2.1', enable=False)
        
        # Push result
        self._push_counts(num)

