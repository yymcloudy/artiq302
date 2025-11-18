from artiq.experiment import *
from artiq.language import delay
from artiq.language.units import ms, us, MHz, dB
import math
from ndscan.experiment import *


class TrapEnvScan(ExpFragment):
    """trapenv_scan"""
    def build_fragment(self):
        self.setattr_device("core")
        # Set up scan parameters
        self.setattr_param("frequency",
                          FloatParam,
                          "Frequency",
                          180.0 * MHz,
                          unit="MHz",
                          min=0.0)
        
        # Set up devices
        self.dds_0_0 = self.get_device("urukul0_ch0")
        self.dds_0_1 = self.get_device("urukul0_ch1")
        self.dds_0_2 = self.get_device("urukul0_ch2")
        self.dds_0_3 = self.get_device("urukul0_ch3")
        self.dds_1_0 = self.get_device("urukul1_ch0")
        self.dds_1_1 = self.get_device("urukul1_ch1")
        self.dds_1_2 = self.get_device("urukul1_ch2")
        self.dds_1_3 = self.get_device("urukul1_ch3")

        self.ttl0 = self.get_device("ttl0")
        self.ttl1 = self.get_device("ttl1")
        self.ttl2 = self.get_device("ttl2")
        self.ttl3 = self.get_device("ttl3")
        self.ttl4 = self.get_device("ttl4")
        self.ttl5 = self.get_device("ttl5")
        self.ttl6 = self.get_device("ttl6")
        self.ttl7 = self.get_device("ttl7")
        self.ttl8 = self.get_device("ttl8")
        self.ttl9 = self.get_device("ttl9")
        self.ttl10 = self.get_device("ttl10")
        self.ttl11 = self.get_device("ttl11")
        self.ttl12 = self.get_device("ttl12")
        self.ttl13 = self.get_device("ttl13")
        self.ttl14 = self.get_device("ttl14")
        self.ttl15 = self.get_device("ttl15")

        self.sampler0 = self.get_device("sampler0")
        print("TrapEnvScan Build Done")

    @kernel
    def prepare(self):
        self.core.reset()
        self.dds_0_0.cpld.init()
        self.dds_0_1.cpld.init()
        self.dds_0_2.cpld.init()
        self.dds_0_3.cpld.init()
        self.dds_1_0.cpld.init()
        self.dds_1_1.cpld.init()
        self.dds_1_2.cpld.init()
        self.dds_1_3.cpld.init()
        self.dds_0_0.init()
        self.dds_0_1.init()
        self.dds_0_2.init()
        self.dds_0_3.init()
        self.dds_1_0.init()
        self.dds_1_1.init()
        self.dds_1_2.init()
        self.dds_1_3.init()
        self.ttl0.input()
        self.ttl1.input()
        self.ttl2.input()
        self.ttl3.input()
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
        self.sampler0.init()
        self.sampler0.set_gain_mu(7,0)

        print("TrapEnvScan Prepare Done")

    @kernel
    def set_idle(self):
        self.core.reset()
        self.core.break_realtime()
        
        self.dds_0_0.set_att(0.5*dB)
        self.dds_0_0.set(frequency=133*MHz, phase=0.0, amplitude = 0.2)
        self.dds_0_0.sw.on()

        self.dds_0_1.sw.off()

        self.dds_0_2.sw.off() # not used 
        self.dds_0_3.sw.off()
        self.dds_1_0.sw.off()
        self.dds_1_1.sw.off()
        self.dds_1_2.sw.off()
        self.dds_1_3.sw.off()

        self.ttl4.off() # when ttl4 is off, the 14.7G sideband is open.
        self.ttl5.off() # when ttl5 is off, the 2.1G sideband is closed.
        self.ttl6.on() # when ttl6 is on, the viewer is ccd, or the viewer is pmt.
        self.ttl7.off()
        self.ttl8.off() # not used 
        self.ttl9.off()
        self.ttl10.off()
        self.ttl11.off()
        self.ttl12.off()
        self.ttl13.off()
        self.ttl14.off()
        self.ttl15.off()
        delay(100*ms)
        print("TrapEnvScan Set_Idle Done")

    @kernel
    def run_once(self):
        """to be rewritten in different experiments"""
        self.core.reset()
        delay(100*ms)
        self.dds_0_0.set(frequency=self.frequency.get()*MHz,phase=0.0*math.pi, amplitude = 0.4)
        self.dds_0_0.sw.on()
        delay(100*ms)
        self.dds_0_0.sw.off()
        print(self.frequency.get())
        print("TrapEnvScan Run_Once Done")

# Create scan experiment
TrapEnvScanExp = make_fragment_scan_exp(TrapEnvScan)

class TrapEnv(EnvExperiment):
    """trapenv"""
    doppler_dds_center_f = 210*MHz
    qubit_dds_center_f = 200*MHz
    repump_dds_center_f = 200*MHz
    depump_dds_center_f = 80*MHz
    raman_dds_center_f = 170*MHz

    def build(self):
        self.setattr_device("core")

        self.dds_0_0 = self.get_device("urukul0_ch0")
        self.dds_0_1 = self.get_device("urukul0_ch1")
        self.dds_0_2 = self.get_device("urukul0_ch2")
        self.dds_0_3 = self.get_device("urukul0_ch3")
        self.dds_1_0 = self.get_device("urukul1_ch0")
        self.dds_1_1 = self.get_device("urukul1_ch1")
        self.dds_1_2 = self.get_device("urukul1_ch2")
        self.dds_1_3 = self.get_device("urukul1_ch3")

        self.ttl0 = self.get_device("ttl0")
        self.ttl1 = self.get_device("ttl1")
        self.ttl2 = self.get_device("ttl2")
        self.ttl3 = self.get_device("ttl3")
        self.ttl4 = self.get_device("ttl4")
        self.ttl5 = self.get_device("ttl5")
        self.ttl6 = self.get_device("ttl6")
        self.ttl7 = self.get_device("ttl7")
        self.ttl8 = self.get_device("ttl8")
        self.ttl9 = self.get_device("ttl9")
        self.ttl10 = self.get_device("ttl10")
        self.ttl11 = self.get_device("ttl11")
        self.ttl12 = self.get_device("ttl12")
        self.ttl13 = self.get_device("ttl13")
        self.ttl14 = self.get_device("ttl14")
        self.ttl15 = self.get_device("ttl15")

        self.sampler0 = self.get_device("sampler0")
        print("Fundamental Build Done")

    
    @kernel
    def force_init_all(self):
        self.core.reset()
        # dds init
        self.dds_0_0.cpld.init()
        self.dds_0_1.cpld.init()
        self.dds_0_2.cpld.init()
        self.dds_0_3.cpld.init()
        self.dds_1_0.cpld.init()
        self.dds_1_1.cpld.init()
        self.dds_1_2.cpld.init()
        self.dds_1_3.cpld.init()
        self.dds_0_0.init()
        self.dds_0_1.init()
        self.dds_0_2.init()
        self.dds_0_3.init()
        self.dds_1_0.init()
        self.dds_1_1.init()
        self.dds_1_2.init()
        self.dds_1_3.init()

        # dds attenuation
        self.dds_0_0.set_att(0*dB)
        self.dds_0_1.set_att(0*dB)
        self.dds_0_2.set_att(0*dB)
        self.dds_0_3.set_att(0*dB)
        self.dds_1_0.set_att(0*dB)
        self.dds_1_1.set_att(0*dB)
        self.dds_1_2.set_att(0*dB)
        self.dds_1_3.set_att(0*dB)

        # ttl init
        self.ttl0.input()
        self.ttl1.input()
        self.ttl2.input()
        self.ttl3.input()
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

        self.sampler0.init()
        print("Fundamental Force_Init_All Done")
        
    @kernel
    def set_idle(self):
        print("setting idle...")
        self.core.break_realtime()
        # 给所有dds和ttl设置一个状态
        # self.dds_0_0.sw.off()
        # self.dds_0_1.sw.off()
        # self.dds_0_2.sw.off()
        # self.dds_0_3.sw.off()
        # self.dds_1_0.sw.off()
        # self.dds_1_1.sw.off()
        # self.dds_1_2.sw.off()
        # self.dds_1_3.sw.off()
        # self.dds_0_0.set(frequency=150*MHz,phase=0.0*math.pi, amplitude = 0.4)
        # self.dds_0_1.set(frequency=150*MHz,phase=0.0*math.pi, amplitude = 0.4)
        # self.dds_0_2.set(frequency=150*MHz,phase=0.0*math.pi, amplitude = 0.4)
        # self.dds_0_3.set(frequency=150*MHz,phase=0.0*math.pi, amplitude = 0.4)
        # self.dds_1_0.set(frequency=150*MHz,phase=0.0*math.pi, amplitude = 0.4)
        # self.dds_1_1.set(frequency=150*MHz,phase=0.0*math.pi, amplitude = 0.4)
        # self.dds_1_2.set(frequency=150*MHz,phase=0.0*math.pi, amplitude = 0.4)
        # self.dds_1_3.set(frequency=150*MHz,phase=0.0*math.pi, amplitude = 0.4)
        self.dds_0_0.sw.off()
        self.dds_0_1.sw.off()
        self.dds_0_2.sw.off()
        self.dds_0_3.sw.off()
        self.dds_1_0.sw.off()
        self.dds_1_1.sw.off()
        self.dds_1_2.sw.off()
        self.dds_1_3.sw.off()
        self.ttl4.off()
        self.ttl5.off()
        self.ttl6.off()
        self.ttl7.off()
        self.ttl8.off()
        self.ttl9.off()
        self.ttl10.off()
        self.ttl11.off()
        self.ttl12.off()
        self.ttl13.off()
        self.ttl14.off()
        self.ttl15.off()
        print("Fundamental Set_Idle Done")

    @kernel
    def run(self):
        """
        This function is used to run the experiment. 
        Test the basic function of the general trap environment.
        """
        self.force_init_all()
        self.set_idle()
        ttl = self.ttl0
        self.core.break_realtime()
        pmt_temp = [0 for _ in range(50)]
        pmt_temp[1] = 500
        self.set_dataset("pmt_readlist", pmt_temp, broadcast=True)
        
        smp_data = [0.000]*1
        
        while True:
            delay(50*ms)
            with parallel:
                cnt = ttl.gate_rising(100*ms)
                num = ttl.count(cnt)
            
            pmt_temp[2:-1] = pmt_temp[3:]
            pmt_temp[-1] = num
            # self.set_dataset("pmt_readlist", pmt_temp, broadcast=True)

            # delay(100*ms)
            # print(num)

            delay(10*us)
            self.sampler0.sample(smp_data)
            print(smp_data)
            


