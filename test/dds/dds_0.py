from artiq.experiment import*
import math

class DDS_TEST(EnvExperiment):
    """dds_0_0_channel_test"""
    def build(self):
        self.setattr_device("core")
        self.dds_0_0 = self.get_device("urukul0_ch0")
        
    @kernel
    def run(self):
        self.core.reset()                                     
        self.dds_0_0.cpld.init() 
        self.dds_0_0.init()  

        delay(100*ms)

        attr0_ch0 = 0

        self.dds_0_0.set_att((attr0_ch0)*dB)


        freq00 = 180

        amp0_ch0 = 0.4
        
        phase00=0.0 * math.pi


    
        self.dds_0_0.set(frequency=freq00*MHz,phase=phase00, amplitude = amp0_ch0)
        # with parallel:
        self.dds_0_0.sw.on()

        delay(2000*ms)

        # with parallel:
        self.dds_0_0.sw.off()
