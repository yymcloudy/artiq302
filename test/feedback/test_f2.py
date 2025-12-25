from artiq.experiment import *

class SamplerFeedbackTTL(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("sampler0")
        self.setattr_device("ttl_fb")
        self.threshold = 10_000  # 随便举例，用 ADC 原始字

    @kernel
    def one_shot(self) -> Tuple[int64, int64]:
        data = [0]*2   # 假设只用两个通道，长度必须为偶数
        self.core.break_realtime()

        # --- ADC 段 ---
        t0 = now_mu()
        self.sampler0.sample_mu(data)
        t_meas = now_mu()

        # --- 决策段 ---
        if data[0] > self.threshold:
            # 可以加一点逻辑，但不要写太 heavy
            pass

        # --- 输出 TTL ---
        t_fb = now_mu()
        self.ttl_fb.pulse(100*ns)

        # 返回两个差值（单位：mu）
        return t_meas - t0, t_fb - t_meas

    def run(self):
        self.set_dataset("adc_latency_mu", [], archive=True)
        self.set_dataset("proc_latency_mu", [], archive=True)

        shots = 100
        for _ in range(shots):
            adc_dt_mu, proc_dt_mu = self.one_shot()
            self.append_to_dataset("adc_latency_mu", adc_dt_mu)
            self.append_to_dataset("proc_latency_mu", proc_dt_mu)

        # 转成 us
        adc_mu = self.get_dataset("adc_latency_mu")
        proc_mu = self.get_dataset("proc_latency_mu")

        adc_us = [self.core.mu_to_seconds(x)*1e6 for x in adc_mu]
        proc_us = [self.core.mu_to_seconds(x)*1e6 for x in proc_mu]

        self.set_dataset("adc_latency_us", adc_us, archive=True)
        self.set_dataset("proc_latency_us", proc_us, archive=True)
