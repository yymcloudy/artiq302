from ndscan.experiment import ExpFragment, FloatParam
from artiq.experiment import *
from artiq.language.units import us
from artiq.language import delay


class RamseyFragment(ExpFragment):
    def build_fragment(self):
        self.setattr_device("core")
        # self.setattr_device("urukul0_ch0")
        self.mw_dds = self.get_device("urukul0_ch0")

        self.setattr_device("ttl10")
        self.mw_switch = self.ttl10
        self.setattr_param("t_wait", FloatParam, "Ramsey wait time", default=10.0, unit="us")
        self.setattr_param("t_pi2", FloatParam, "Pi/2 pulse duration", default=10.0, unit="us")
        self.setattr_param("mw_freq", FloatParam, "MW frequency", default=143.0, unit="MHz")
        self.setattr_param("mw_amp", FloatParam, "MW amplitude", default=0.3, unit="")
        self.setattr_param("mw_phase", FloatParam, "MW phase for second pulse", default=0.0, unit="")
    
    @kernel
    def device_setup(self):
        self.core.break_realtime()
        self.mw_dds.cpld.init()
        self.mw_dds.init()
        self.mw_dds.set_att(0*dB)

        self.mw_switch.output()

        delay(1000*us)
    
    @kernel
    def run_once(self):
        self.core.reset()
        self.core.break_realtime()
        
        # First pi/2 pulse
        self.mw_dds.set(frequency=self.mw_freq.get(), phase=0.0, amplitude=self.mw_amp.get())
        self.mw_switch.on()
        delay(self.t_pi2.get() * us)
        self.mw_switch.off()
        
        # Wait time (evolution)
        delay(self.t_wait.get() * us)
        
        # Second pi/2 pulse with phase
        self.mw_dds.set(frequency=self.mw_freq.get(), phase=self.mw_phase.get(), amplitude=self.mw_amp.get())
        self.mw_switch.on()
        delay(self.t_pi2.get() * us)
        self.mw_switch.off()
        
        delay(10 * us)

