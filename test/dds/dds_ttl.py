from artiq.experiment import*
import math

class DDS_TEST(EnvExperiment):
    """dds_0_0_channel_test"""
    def build(self):
        self.setattr_device("core")
        # self.setattr_device("urukul0_ch0")
        # rename the device urukul0_ch0 to dds_0_0
        self.dds_1_3 = self.get_device("urukul1_ch3")
        self.flag_experiment = self.get_device("ttl11")
        self.nv_mw_switch = self.get_device("ttl11")
        
    @kernel
    def run(self):
        self.core.reset()                                     
        self.dds_1_3.cpld.init() 
        self.dds_1_3.init()  

        delay(100*ms)

        attr0_ch0 = 0
        self.dds_1_3.set_att((attr0_ch0)*dB)

        freq00 = 180
        amp0_ch0 = 0.4
        phase00=0.0 * math.pi # no pi!
        self.dds_1_3.set(frequency=freq00*MHz,phase=phase00, amplitude = amp0_ch0)
        self.dds_1_3.sw.on()
        delay(100*us)

        with parallel:
            self.flag_experiment.on()
            self.nv_mw_switch.pulse(1*us)
