from artiq.experiment import*

class ALL_DEVICE(EnvExperiment):
    """all_device"""
    def build(self):
        # initialize
        self.setattr_device("core")
        # urukul dds initialization
        self.setattr_device("urukul0_ch0")
        self.setattr_device("urukul0_ch1")
        self.setattr_device("urukul0_ch2")
        self.setattr_device("urukul0_ch3")
        self.setattr_device("urukul1_ch0")
        self.setattr_device("urukul1_ch1")
        self.setattr_device("urukul1_ch2")
        self.setattr_device("urukul1_ch3")

        # ttl input initialization
        self.setattr_device("ttl0")
        self.setattr_device("ttl1")
        self.setattr_device("ttl2")
        self.setattr_device("ttl3")

        # ttl output initialization
        self.setattr_device("ttl4")
        self.setattr_device("ttl5")
        self.setattr_device("ttl6")
        self.setattr_device("ttl7")
        self.setattr_device("ttl8")
        self.setattr_device("ttl9")
        self.setattr_device("ttl10")
        self.setattr_device("ttl11")
        self.setattr_device("ttl12")
        self.setattr_device("ttl13")
        self.setattr_device("ttl14")
        self.setattr_device("ttl15")

        pmt_init = [0 for _ in range(50)]
        self.setattr_dataset("pmt_readlist", pmt_init)

   
    @kernel
    def run(self):
        self.prepare()
        self.urukul0_ch0.set(frequency=200*MHz,phase=0*math.pi, amplitude = 0.4)
        self.urukul0_ch1.set(frequency=200*MHz,phase=0*math.pi, amplitude = 0.4)
        self.urukul0_ch2.set(frequency=200*MHz,phase=0*math.pi, amplitude = 0.4)
        self.urukul0_ch3.set(frequency=200*MHz,phase=0*math.pi, amplitude = 0.4)
        self.urukul1_ch0.set(frequency=180*MHz,phase=0*math.pi, amplitude = 0.4)
        self.urukul1_ch1.set(frequency=180*MHz,phase=0*math.pi, amplitude = 0.4)
        self.urukul1_ch2.set(frequency=180*MHz,phase=0*math.pi, amplitude = 0.4)
        self.urukul1_ch3.set(frequency=180*MHz,phase=0*math.pi, amplitude = 0.4)


    @kernel
    def prepare(self):
        self.core.reset()
        # urukul dds initialization
        self.urukul0_ch3.cpld.init()                           
        self.urukul0_ch1.cpld.init()
        self.urukul0_ch2.cpld.init()
        self.urukul0_ch0.cpld.init() 
        self.urukul1_ch3.cpld.init()                           
        self.urukul1_ch1.cpld.init()
        self.urukul1_ch2.cpld.init()
        self.urukul1_ch0.cpld.init()   
        self.urukul0_ch3.init()                
        self.urukul0_ch0.init()
        self.urukul0_ch1.init()
        self.urukul0_ch2.init()
        self.urukul1_ch3.init()                
        self.urukul1_ch0.init()
        self.urukul1_ch1.init()
        self.urukul1_ch2.init() 
        delay(100*ms)
        # dds attenuation
        attr0_ch0 = 0
        attr0_ch1 = 0
        attr0_ch2 = 0
        attr0_ch3 = 0
        attr1_ch0 = 0
        attr1_ch1 = 0
        attr1_ch2 = 0
        attr1_ch3 = 0

        self.urukul0_ch0.set_att((attr0_ch0)*dB)
        self.urukul0_ch1.set_att((attr0_ch1)*dB)
        self.urukul0_ch2.set_att((attr0_ch2)*dB)
        self.urukul0_ch3.set_att((attr0_ch3)*dB)
        self.urukul1_ch0.set_att((attr1_ch0)*dB)
        self.urukul1_ch1.set_att((attr1_ch1)*dB)
        self.urukul1_ch2.set_att((attr1_ch2)*dB)
        self.urukul1_ch3.set_att((attr1_ch3)*dB)
        delay(100*ms)

        # ttl input
        self.ttl0.input()
        self.ttl1.input()
        self.ttl2.input()
        self.ttl3.input()
        delay(100*ms)
        # ttl output
        self.ttl4.output()
        self.ttl5.output()
        self.ttl6.output()
        self.ttl7.output()
        self.ttl8.output()
        self.ttl9.output()
        self.ttl10.output()
        self.ttl11.output()
        self.ttl12.output()
        self.ttl13.output()
        self.ttl14.output()
        self.ttl15.output()
        delay(100*ms)
