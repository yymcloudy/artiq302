from ndscan.experiment import *
from artiq.experiment import *
from artiq.language.units import ms, us, MHz, dB

@kernel
def dds_pulse(dds, delay):
    dds.sw.on()
    delay(delay)
    dds.sw.off()



@kernel
def laser370_switch(dds_laser_switch, switch='on'):
    if switch == 'on':
        dds_laser_switch.sw.on()
    elif switch == 'off':
        dds_laser_switch.sw.off()



@kernel
def laser370_sideband(ttl_eom_14_7_switch, ttl_eom_2_1_switch, sideband='14.7', enable=True):
    if sideband == '14.7':
        if enable:
            ttl_eom_14_7_switch.off()
        else:
            ttl_eom_14_7_switch.on()
    elif sideband == '2.1':
        if enable:
            ttl_eom_2_1_switch.on()
        else:
            ttl_eom_2_1_switch.off()

@kernel
def microwave_pulse(dds_mw_gate, ttl_mw_gate, t_mw, mw_freq, mw_phase=0.0, amplitude=0.3):
    """
    mw gate function: set the one of the mixed two frequency of mw, turn on the ttl and wait for the duration of mw, then turn off the ttl
    Args:
        dds_mw_gate: the dds device for mw
        ttl_mw_gate: the ttl device for mw
        mw_freq: the frequency of mw
        t_mw: the duration of mw
    """
    dds_mw_gate.set(frequency=mw_freq, phase=mw_phase, amplitude = amplitude)
    ttl_mw_gate.on()
    delay(t_mw)
    ttl_mw_gate.off()

