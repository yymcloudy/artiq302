from artiq.language.core import kernel
from artiq.language.units import us

@kernel
def cool(core, ttl_cool, t_us: float):
    # 使用传入的 core/通道，避免对 self 绑定
    ttl_cool.on()
    delay(t_us*us)
    ttl_cool.off()

@kernel
def pulse_dds(dds, freq_hz: float, amp: float, t_us: float):
    dds.set(freq_hz, amplitude=amp)
    dds.sw.on()
    delay(t_us*us)  # 便于复用的时间换算
    dds.sw.off()
