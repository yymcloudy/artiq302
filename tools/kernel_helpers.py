from ndscan.experiment import *
from artiq.experiment import *
from artiq.language.units import ms, us, MHz, dB

@kernel
def cooling(core, ttl_cool, t_us: float):
    """冷却函数：打开TTL开关，等待指定时间后关闭"""
    delay(100*us)
    ttl_cool.on()
    delay(100 * us)
    ttl_cool.off()

