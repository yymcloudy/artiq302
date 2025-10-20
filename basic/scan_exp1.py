from artiq.experiment import *
from artiq.language import delay
from artiq.language.units import ms, us, MHz
# seconds_to_mu, frequency_to_mu, power_to_mu
import math
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from trapenv import TrapEnvScan
from ndscan.experiment import *

class Example0(TrapEnvScan):
    """example0_inherit_from_TrapEnvScan"""
    
    def build_fragment(self):
        TrapEnvScan.build_fragment(self)
        print("Example0 Build Done")
    
    @kernel
    def prepare(self):
        TrapEnvScan.prepare(self)
        print("Example0 Prepare Done")
    
    @kernel
    def run_once(self):
        TrapEnvScan.run_once(self)
        print("Example0 Run_Once Done")

# Create scan experiment
Example0Exp = make_fragment_scan_exp(Example0)