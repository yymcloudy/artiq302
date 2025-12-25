# 裸机代码
# 伪代码_V1
from re import T
from artiq.experiment import *
from artiq.language.units import us, MHz
from artiq.language.core import delay, now_mu

class SamplerFeedbackLatency(EnvExperiment):
    """SamplerFeedbackLatency"""
    def build(self):
        self.setattr_device("core")
        self.setattr_device("sampler0") # ADC
        self.ttl13 = self.get_device("ttl13")     # 用于触发示波器 & 模拟输入信号
        self.ttl14 = self.get_device("ttl14")     # 反馈输出 (TTL)
        self.dds_1_1 = self.get_device("urukul1_ch1") # 反馈输出 (DDS)
        
        # 定义采样缓冲区 (读取1个通道)
        self.sample_buffer = [0.00]

    @kernel
    def run(self):
        self.core.reset()
        
        # 初始化硬件
        self.sampler0.init()
        # 设置 Sampler 增益 (根据实际情况调整)
        for i in range(8):
            self.sampler0.set_gain_mu(i, 0) 
            
        self.dds_1_1.cpld.init()
        self.dds_1_1.init()
        self.dds_1_1.sw.off()
        self.dds_1_1.set(100*MHz) # 预设频率
        
        self.core.break_realtime()
        
        while True:
            self.measure_latency()
            delay(50*ms)

    @kernel
    def measure_latency(self):
        # --- 步骤 1: 制造刺激 (Stimulus) ---
        # 产生一个上升沿，作为 T0。
        # 假设我们将 ttl0 物理连接到了 sampler0 的通道0
        self.ttl13.pulse(100*us) 
        
        # --- 步骤 2: 采样 (Sampling) ---
        # 我们希望在 pulse 开启期间进行采样
        # 这里的时序非常微妙，我们回退一点时间游标，确保采样发生在 pulse 期间
        # 注意：sampler.sample 是阻塞函数，它会推进时间游标
        t0 = self.core.get_rtio_counter_mu()
        t_start_sampling = now_mu()
        
        # 指令 Sampler 立即采样
        # 这里的延迟主要由这一行代码产生
        self.sampler0.sample(self.sample_buffer)
        # Sampler读数通常是 Volts (float)
        val = self.sample_buffer[0]
        t1 = self.core.get_rtio_counter_mu()
        t_finished_sampling = now_mu()
        
        # --- 步骤 3: 逻辑判断 ---
        # 检查通道0的电压是否超过阈值 (例如 1.0V)
        
        t2 = 0
        t_finished_feedback = 0

        # val = val + 0.5
        if val > -0.5:
            # --- 步骤 4A: TTL 反馈 ---
            # delay(2*us)
            # self.ttl14.on()
            # t_finished_feedback = now_mu()
            # delay(10*us)
            # self.ttl14.off()
            
            # --- 步骤 4B: DDS 反馈 (二选一测试) ---
            # 改变频率 (较慢)
            self.dds_1_1.set(200*MHz, amplitude=0.4, phase=0.1)
            # 开启 RF 开关 (较快)
            self.dds_1_1.sw.on()
            t2 = self.core.get_rtio_counter_mu()
            t_finished_feedback = now_mu()
            
        else:
            # 保持时序稳定
            delay(10*us)

        
        
        delay(100*ms)
        print(val)
        print("t_finished_sampling - t_start_sampling: ", t_finished_sampling - t_start_sampling)
        print("t_finished_feedback - t_start_sampling: ", t_finished_feedback - t_start_sampling)
        print("t1 - t0: ", t1 - t0)
        print("t2 - t0: ", t2 - t0)
        delay(100*ms)

        # --- 调试信息：计算软件耗时 ---
        # 可以在 dashboard log 看到 tick 差值，换算成 us
        # dt = t_finished_sampling - t_start_sampling
        # print(dt)