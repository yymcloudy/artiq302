from ndscan.experiment import ExpFragment, FloatParam, make_fragment_scan_exp
from artiq.experiment import kernel

from artiq.language.units import *
from artiq.language import delay

class TestBareFragment(ExpFragment): 
    """test bare fragment"""
    def build_fragment(self):        
        self.setattr_device("core")        
        self.setattr_device("ttl15")        
        self.setattr_param("t_cool", FloatParam, "Cooling time", default=200.0*us, unit="us")

    def prepare(self):
        self.exp_n = 0

    @kernel    
    def device_setup(self):        
        self.core.reset()
    
    @kernel    
    def run_once(self):
        
        self.ttl15.on()
        delay(self.t_cool.get())
        self.ttl15.off()

        delay(100*us)
        self.exp_n += 1
        print("experiment_num_shots: ", self.exp_n)

test_bare_fragment = make_fragment_scan_exp(TestBareFragment)

