from math import tan, acos


class Load:
    def __init__(self, circuit_label, meter=None):
        self._circuit_label = circuit_label
        self._p_in = None
        self._q_in = None
        self._power_factor = 0.95
        self._volt = None
        self._meter = meter

    @property
    def circuit_label(self):
        return self._circuit_label

    @property
    def p_in(self):
        return self._p_in

    @property
    def q_in(self):
        return self._q_in

    @property
    def volt(self):
        return self._volt

    @property
    def pf(self):
        return self._power_factor

    @property
    def meter(self):
        from src.models.meter import Meter
        return self._meter

    def set_demand(self, power):
        # It should be the active power, but for the purposes of my project I changed this and assumed the power is an apparent power
        self._p_in = power # * self._power_factor * 0.8
        # self._p_in = power

    def set_power_factor(self, pf):
        self._power_factor = pf

    def update(self, power, volt, power_factor=0.95):
        self.set_demand(power)
        self._volt = volt
        self.set_power_factor(power_factor)

    def get_output_power(self):
        self._q_in = self._p_in * tan(acos(self._power_factor))
        return self._p_in, self._q_in

    def step(self):
        return self.get_output_power()
