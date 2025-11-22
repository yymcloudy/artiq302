from ndscan.experiment import ExpFragment, FloatParam, OpaqueChannel
from artiq.experiment import kernel, parallel
from artiq.language import delay
from artiq.language.units import us, ms, MHz


class _RabiBaseFragment(ExpFragment):
    """Common helpers shared by the Rabi sequence fragments."""

    def build_fragment(self):
        self.setattr_device("core")
        self.double_pass_370 = self.get_device("urukul0_ch0")
        self.mw_dds = self.get_device("urukul0_ch1")
        self.counter = self.get_device("ttl0")
        self.eom_14_7_switch = self.get_device("ttl4")
        self.eom_2_1_switch = self.get_device("ttl5")
        self.pmt_ccd_switch = self.get_device("ttl6")
        self.mw_switch = self.get_device("ttl7")
        self.laser370_switch = self.get_device("ttl8")

        self.setattr_param(
            "double_pass_frequency",
            FloatParam,
            "2 pass Frequency",
            default=133.0 * MHz,
            unit="MHz",
        )

    @kernel
    def laser370_switch_control(self, switch="on"):
        if switch == "on":
            with parallel:
                self.double_pass_370.sw.on()
        elif switch == "off":
            with parallel:
                self.double_pass_370.sw.off()

    @kernel
    def laser370_sideband_control(self, sideband="14.7", enable=True):
        if sideband == "14.7":
            if enable:
                self.eom_14_7_switch.off()
            else:
                self.eom_14_7_switch.on()
        elif sideband == "2.1":
            if enable:
                self.eom_2_1_switch.on()
            else:
                self.eom_2_1_switch.off()
        elif sideband == "cooling":
            with parallel:
                self.eom_14_7_switch.off()
                self.eom_2_1_switch.off()
        elif sideband == "pumping":
            with parallel:
                self.eom_14_7_switch.on()
                self.eom_2_1_switch.on()
        elif sideband == "detection":
            with parallel:
                self.eom_14_7_switch.on()
                self.eom_2_1_switch.off()


class RabiCoolingFragment(_RabiBaseFragment):
    def build_fragment(self):
        super().build_fragment()
        self.setattr_param(
            "cooling_time", FloatParam, "Cooling time", default=1000.0 * us, unit="us"
        )

    @kernel
    def run_once(self):
        self.core.reset()
        self.core.break_realtime()
        with parallel:
            self.double_pass_370.set(
                frequency=self.double_pass_frequency.get(),
                phase=0.0,
                amplitude=0.11,
            )
            self.laser370_sideband_control(sideband="14.7", enable=True)
            self.laser370_sideband_control(sideband="2.1", enable=False)
        self.laser370_switch_control(switch="on")
        delay(self.cooling_time.get())
        self.laser370_switch_control(switch="off")


class RabiPumpingFragment(_RabiBaseFragment):
    def build_fragment(self):
        super().build_fragment()
        self.setattr_param(
            "pumping_time", FloatParam, "Pumping time", default=100.0 * us, unit="us"
        )

    @kernel
    def run_once(self):
        self.core.reset()
        self.core.break_realtime()
        with parallel:
            self.double_pass_370.set(
                frequency=self.double_pass_frequency.get(),
                phase=0.0,
                amplitude=0.11,
            )
            self.laser370_sideband_control(sideband="14.7", enable=False)
            self.laser370_sideband_control(sideband="2.1", enable=True)
        self.laser370_switch_control(switch="on")
        delay(self.pumping_time.get())
        self.laser370_switch_control(switch="off")


class RabiPulseFragment(_RabiBaseFragment):
    def build_fragment(self):
        super().build_fragment()
        self.setattr_param(
            "mw_freq",
            FloatParam,
            "MW frequency",
            default=180.0 * MHz,
            unit="MHz",
        )
        self.setattr_param(
            "mw_duration",
            FloatParam,
            "MW duration",
            default=100.0 * us,
            unit="us",
        )
        self.setattr_param(
            "mw_amplitude",
            FloatParam,
            "MW amplitude",
            default=0.3,
            unit="",
        )

    @kernel
    def run_once(self):
        self.core.reset()
        self.core.break_realtime()
        self.laser370_switch_control(switch="off")
        self.mw_dds.set(
            frequency=self.mw_freq.get(),
            phase=0.0,
            amplitude=self.mw_amplitude.get(),
        )
        with parallel:
            self.mw_switch.on()
        delay(self.mw_duration.get())
        self.mw_switch.off()


class RabiDetectionFragment(_RabiBaseFragment):
    def build_fragment(self):
        super().build_fragment()
        self.setattr_param(
            "detection_time",
            FloatParam,
            "Detection time",
            default=500.0 * us,
            unit="us",
        )
        self.setattr_result("counts", OpaqueChannel, "Photon counts")
        self._pulse_fragment = None
        self.num_shots = 0

    def link_pulse_fragment(self, pulse_fragment):
        self._pulse_fragment = pulse_fragment

    def run_once(self):
        if self._pulse_fragment is None:
            raise ValueError("Pulse fragment not linked for detection.")
        detection_time = self.detection_time.get()
        mw_duration = self._pulse_fragment.mw_duration.get()
        mw_freq = self._pulse_fragment.mw_freq.get()
        self._run_detection(detection_time, mw_duration, mw_freq)
        self.num_shots += 1
        print("experiment_num_shots:", self.num_shots)

    @kernel
    def _run_detection(self, detection_time, mw_duration, mw_freq):
        self.core.reset()
        self.core.break_realtime()
        with parallel:
            self.double_pass_370.set(frequency=139 * MHz, phase=0.0, amplitude=0.08)
            self.laser370_sideband_control(sideband="14.7", enable=False)
            self.laser370_sideband_control(sideband="2.1", enable=False)
        self.laser370_switch_control(switch="on")
        with parallel:
            cnt = self.counter.gate_rising(detection_time)
            num = self.counter.count(cnt)
        delay(100 * us)
        self.double_pass_370.set(
            frequency=self.double_pass_frequency.get(), phase=0.0, amplitude=0.11
        )
        delay(1 * ms)
        self.core.reset()
        self.core.break_realtime()
        with parallel:
            self.laser370_sideband_control(sideband="14.7", enable=True)
            self.laser370_sideband_control(sideband="2.1", enable=False)
        self._push_counts(mw_duration, mw_freq, float(num))

    def _push_counts(self, mw_duration, mw_freq, num):
        self.counts.push([mw_duration, mw_freq, num])

