from ndscan.experiment import *
from oitg.errorbars import binom_onesided
from enum import Enum, unique
import random
import numpy as np
import time
from artiq.experiment import *
import math


class Readout(Fragment):
    def build_fragment(self):
        self.setattr_param("num_shots",
                           IntParam,
                           "Number of shots",
                           100,
                           is_scannable=False)
        self.setattr_param("mean_0", FloatParam, "Dark counts over readout duration",
                           0.1)
        self.setattr_param("mean_1", FloatParam, "Bright counts over readout duration",
                           20.0)
        self.setattr_param("threshold", IntParam, "Threshold", 5)

        self.setattr_result("counts", OpaqueChannel)
        self.setattr_result("p")
        self.setattr_result("p_err", display_hints={"error_bar_for": self.p.path})

    def simulate_shots(self, p):
        num_shots = self.num_shots.get()

        counts = np.empty(num_shots, dtype=np.int16)
        for i in range(num_shots):
            mean = self.mean_0.get() if random.random() > p else self.mean_1.get()
            counts[i] = np.random.poisson(mean)
        self.counts.push(counts)

        num_brights = np.sum(counts >= self.threshold.get())
        p, p_err = binom_onesided(num_brights, num_shots)
        self.p.push(p)
        self.p_err.push(p_err)


@unique
class InitialState(Enum):
    dark = "Dark"
    bright = "Bright"


class RabiFlopDDS(ExpFragment):
    def build_fragment(self):
        self.setattr_device("core")
        self.setattr_device("urukul0_ch0")
        self.setattr_fragment("readout", Readout)
        self.setattr_param("amplitude",
                           FloatParam,
                           "Amplitude",
                           0.5,
                           min=0.0)
        self.setattr_param("rabi_freq",
                           FloatParam,
                           "Rabi frequency",
                           1.0 * MHz,
                           unit="MHz",
                           min=0.0)
        self.setattr_param("duration",
                           FloatParam,
                           "Pulse duration",
                           500.0 ,
                           min=0.0)
        self.setattr_param("detuning", FloatParam, "Detuning", 0.0 * MHz, unit="MHz")
        self.setattr_param("initial_state", IntParam, "Initial state (0: dark, 1: bright)", 1, min=0, max=1)

    @kernel
    def device_setup(self):

        self.core.break_realtime()
        self.urukul0_ch0.cpld.init()
        self.urukul0_ch0.init()
        self.urukul0_ch0.set_att(0*dB)
        
    @kernel
    def dds_hold(self):
        self.core.break_realtime()
        self.urukul0_ch0.set(frequency=self.rabi_freq.get(),
                            phase=0.0,
                            amplitude=self.amplitude.get())
        self.urukul0_ch0.sw.on()
        delay(self.duration.get()*ms)
        self.urukul0_ch0.sw.off()
        delay(100*ms)


    def run_once(self):
        # Initialize DDS
        print("begins", self.rabi_freq.get(), self.duration.get())
        # self.device_setup()
        # self.prepare()
        self.dds_hold()
        
        # Calculate probability
        omega0 = 2 * np.pi * self.rabi_freq.get()
        delta = 2 * np.pi * self.detuning.get()
        omega = np.sqrt(omega0**2 + delta**2)
        p = (omega0 / omega * np.sin(omega / 2 * self.duration.get()))**2
        
        # Invert probability if initial state is bright
        if self.initial_state.get() == 1:  # 1 represents bright state
            p = 1 - p
            
        self.readout.simulate_shots(p)

    def get_default_analyses(self):
        return [
            OnlineFit("sinusoid",
                      data={
                          "x": self.duration,
                          "y": self.readout.p,
                          "y_err": self.readout.p_err,
                      },
                      constants={
                          "t_dead": 0,
                      })
        ]


# Create scan experiment
ScanRabiFlopDDS = make_fragment_scan_exp(RabiFlopDDS)
