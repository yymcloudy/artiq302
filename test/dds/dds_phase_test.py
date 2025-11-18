from artiq.experiment import*
import math

class DDS_TEST(EnvExperiment):
    """dds_1st_2_and_3_phase_test"""
    def build(self):
        self.setattr_device("core")
        # self.setattr_device("urukul0_ch0")
        # rename the device urukul0_ch0 to dds_0_0
        self.dds_0_2 = self.get_device("urukul0_ch2")
        self.dds_0_3 = self.get_device("urukul0_ch3")
        self.ttl9 = self.get_device("ttl9")

        
    @kernel
    def run(self):
        self.core.reset()                                     
        self.dds_0_2.cpld.init() 
        self.dds_0_3.cpld.init() 
        self.dds_0_2.init()  
        self.dds_0_3.init()  
        self.ttl9.output()

        delay(100*ms)

        attr0_ch0 = 0

        self.dds_0_2.set_att((attr0_ch0)*dB)
        self.dds_0_3.set_att((attr0_ch0)*dB)


        freq02 = 45
        freq03 = 45

        amp0_ch2 = 0.3
        amp0_ch3 = 0.3
        
        phase02 = 0.0 * math.pi
        phase03 = 0.5 * math.pi


        self.dds_0_2.set(frequency=freq02*MHz, phase=0.0, amplitude = amp0_ch2)
        self.dds_0_3.set(frequency=freq03*MHz, phase=0.2, amplitude = amp0_ch3)
        self.dds_0_2.sw.on()
        self.dds_0_3.sw.on()
        delay(1000*ms)


