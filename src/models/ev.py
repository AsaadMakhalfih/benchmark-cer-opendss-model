from src.models.inverter import EVInverter, EVInverterSettings
from src.models.battery import Battery
from src.models.vehicle import Vehicle


class EVSystem:
    def __init__(self, circuit_label, vehicle: Vehicle, battery: Battery, inverter: EVInverter):
        self._circuit_label = circuit_label
        self._vehicle = vehicle
        self._battery = battery
        self._inverter = inverter
        self._volt = 1.0
        self._q_in = 0.0
        self._p_in = 0.0

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
    def inverter(self):
        return self._inverter

    @property
    def battery(self):
        return self._battery

    def get_energy_per_distance(self):
        return self._battery.capacity / self._vehicle.battery_range

    def update(self, volt):
        self._volt = volt
        self.inverter.update_battery_power_limits(self.get_energy_per_distance(), self._battery.max_charge_power(), self._battery.max_discharge_power())

    def get_output_power(self, time_step=None):
        distance = self._vehicle.get_distance()
        is_at_home = self._vehicle.check_ev_at_home(time_step)
        """
        battery_power: charging (+), discharging (-)
        """
        p_batt = self.inverter.get_battery_power(self._volt, is_at_home, distance, time_step)
        if p_batt >= 0:
            self._battery.charge(p_batt)
            p_inv_dc = p_batt
        else:
            self._battery.discharge(p_batt)
            if is_at_home:
                p_inv_dc = p_batt
            else:
                p_inv_dc = 0.0

        self._p_in, self._q_in = self.inverter.get_output_power(p_inv_dc, self._volt)
        return self._p_in, self._q_in

    def step(self, time_step=None):
        return self.get_output_power(time_step)
