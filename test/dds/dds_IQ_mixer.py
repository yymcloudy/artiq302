from artiq.experiment import*
import math

class DDS_IQ_MIXER_TEST(EnvExperiment):
    """dds_IQ_mixer_test"""
    def build(self):
        self.setattr_device("core")
        # self.setattr_device("urukul0_ch0")
        # rename the device urukul0_ch0 to dds_0_0
        self.dds_I = self.get_device("urukul1_ch0")
        self.dds_Q = self.get_device("urukul1_ch1")
        self.setattr_argument("phase", NumberValue(0, min=0, max=1, step=0.001))
        
    @kernel
    def run(self):
        self.core.reset()
        self.core.break_realtime()                                   
        self.dds_I.cpld.init() 
        self.dds_Q.cpld.init() 
        self.dds_I.init()  
        self.dds_Q.init()  

        delay(5*ms)

        attrI = 0
        attrQ = 0

        self.dds_I.set_att((attrI)*dB)
        self.dds_Q.set_att((attrQ)*dB)


        freqI = 170
        freqQ = 170

        ampI = 0.99
        ampQ = 0.99
        
        # N =20 
        # for i in range(0, N):
        #     phaseI=0.0
        #     phaseQ=1.0/N*i

        #     self.dds_I.set(frequency=freqI*MHz,phase=phaseI, amplitude = ampI)
        #     self.dds_Q.set(frequency=freqQ*MHz,phase=phaseQ, amplitude = ampQ)
        #     self.dds_I.sw.on()
        #     self.dds_Q.sw.on()
        #     delay(3000*ms)

        # self.dds_I.set(frequency=freqI*MHz, phase=0.0, amplitude = ampI)
        # self.dds_Q.set(frequency=freqQ*MHz, phase=self.phase, amplitude = ampQ)
        self.dds_I.sw.on()
        self.dds_Q.sw.on()
        delay(1000*ms)

        for i in range(0, 1, 10):
            with parallel:
                self.dds_I.set(frequency=freqI*MHz, phase=0.0, amplitude = ampI)
                self.dds_Q.set(frequency=freqQ*MHz, phase=i*1.0, amplitude = ampQ)
            delay(3000*ms)
            print("i: ", i)
