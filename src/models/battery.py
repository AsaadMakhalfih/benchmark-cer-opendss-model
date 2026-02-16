class Battery:
    def __init__(self, circuit_label=None, capacity=13.5, soc=0.1, min_soc=0.1, charger_eff=0.98, charger_power=5.0, step_size=None):
        self._circuit_label = circuit_label
        self._capacity = capacity
        self._soc = max(soc, min_soc)
        self._min_soc = min_soc
        self._charger_eff = charger_eff
        self._charger_power = charger_power
        self._step_size = step_size
        self._battery_state = 0

    @property
    def circuit_label(self):
        return self._circuit_label

    @property
    def capacity(self):
        return self._capacity

    @property
    def soc(self):
        return self._soc

    @property
    def stored_energy(self):
        return self._soc * self._capacity

    def charge(self, power):
        power = abs(power)
        ch_power = min(power, self.max_charge_power())
        self._soc = self._soc + ch_power * self._charger_eff * (self._step_size / 60) / self._capacity

    def discharge(self, power):
        power = abs(power)
        disch_power = min(power, self.max_discharge_power())
        self._soc = self._soc - disch_power * (self._step_size / 60) / self._capacity / self._charger_eff

    def max_charge_power(self):
        available_power = (1.0 - self._soc) * self._capacity / (self._step_size / 60) / self._charger_eff
        return min(self._charger_power, available_power)

    def max_discharge_power(self):
        available_power = self._charger_eff * (self._soc - self._min_soc) * self._capacity / (self._step_size / 60)
        return min(self._charger_power, available_power)
