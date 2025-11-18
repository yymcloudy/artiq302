from artiq.experiment import *
from artiq.language import delay
from artiq.language.units import ms, us, MHz
# seconds_to_mu, frequency_to_mu, power_to_mu
import math
import numpy as np
from numpy import int32
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from trapenv import TrapEnvScan
from scan_exp3 import BaseSequence_Rabi
from ndscan.experiment import *


class Set_Idle(BaseSequence_Rabi):
    """set_idle"""
    def build_fragment(self):
        BaseSequence_Rabi.build_fragment(self)
        print("Set_Idle Build Done")

    @kernel
    def prepare(self):
        print("Set_Idle Prepare Done")

    @kernel
    def run_once(self):
        BaseSequence_Rabi.set_idle(self)


Set_IdleExp = make_fragment_scan_exp(Set_Idle)
