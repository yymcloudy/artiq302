from artiq.experiment import *
from artiq.language import now_mu
from artiq.coredevice.ad9910 import PHASE_MODE_TRACKING

class DDS_2_Channel_Test(EnvExperiment):
    """dds_phase_test"""
    def build(self):
        self.setattr_device("core")
        self.setattr_device("urukul1_ch0")
        self.setattr_device("urukul1_ch1")
        # self.setattr_param("frequency", NumberValue(180, min=0, max=400, step=1, precision=0))

    @kernel
    def run(self):
        self.core.reset()
        T = now_mu()
        frequency = 128.5
        phase = 0.0
        self.urukul1_ch0.set(frequency=frequency*MHz, phase=0.0, amplitude=0.99, phase_mode=PHASE_MODE_TRACKING, ref_time_mu=T)
        self.urukul1_ch1.set(frequency=frequency*MHz, phase=phase, amplitude=0.3, phase_mode=PHASE_MODE_TRACKING, ref_time_mu=T)
        with parallel:
            self.urukul1_ch0.sw.on()
            self.urukul1_ch1.sw.on()
        delay(50000*ms)
        with parallel:
            self.urukul1_ch0.sw.off()
            self.urukul1_ch1.sw.off()