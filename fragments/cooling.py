from ndscan.experiment import ExpFragment, FloatParam
from artiq.experiment import kernel
from repository.tools.kernel_helpers import cooling


class CoolingFragment(ExpFragment):    
    def build_fragment(self):        
        self.setattr_device("core")        
        self.setattr_device("ttl15")        
        self.setattr_param("t_cool", FloatParam, "Cooling time", default=200.0, unit="us")
    
    @kernel    
    def device_setup(self):        
        self.core.reset()
        self.core.break_realtime()
    
    @kernel    
    def run_once(self):
        self.core.reset()
        self.core.break_realtime()
        cooling(self.core, self.ttl15, self.t_cool.get())