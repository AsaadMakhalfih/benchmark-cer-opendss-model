from src.models.pv_panel import PVPanels
from src.models.inverter import Inverter, HybridInverter
from src.models.battery import Battery
from src.models.meter import Meter


class PVSystem:
    def __init__(self, circuit_label: int = None, pvpanels: PVPanels = None, inverter: Inverter | HybridInverter = None, meter: Meter = None):
        self._circuit_label = circuit_label
        self._inverter = inverter
        self._pvpanels = pvpanels
        self._irrad = None
        self._temp = None
        self._volt = None
        self._q_out = None
        self._p_out = None
        self._meter = meter
        self._dc_generation = 0.0  # updating the dc generation register.
        self._dc_curtailment = 0.0
        self._ac_potential_output = 0.0
        self._ac_curtailment = 0.0

    @property
    def circuit_label(self):
        return self._circuit_label

    @property
    def p_out(self):
        return self._p_out

    @property
    def q_out(self):
        return self._q_out

    @property
    def volt(self):
        return self._volt

    @property
    def inverter(self):
        return self._inverter

    @property
    def meter(self):
        return self._meter

    @property
    def dc_generation(self):
        return self._dc_generation

    @property
    def ac_potential_output(self):
        return self._ac_potential_output

    @property
    def ac_curtailment(self):
        return self._ac_curtailment

    @property
    def dc_curtailment(self):
        return self._dc_curtailment

    def get_potential_pv_inverter_generation(self, p_pv):
        if self._inverter.status(p_pv):
            if p_pv * self._inverter.get_inverter_eff(p_pv) > self.inverter.rated_kva:
                return self.inverter.rated_kva
            else:
                return p_pv * self._inverter.get_inverter_eff(p_pv)
        else:
            return 0

    def get_max_dc_input_power(self):
        return self.inverter.get_pdc_from_efficiency(self.inverter.rated_kva)

    def get_output_power(self):
        p_dc = self._pvpanels.get_dc_power(self._irrad, self._temp)
        self._dc_generation = p_dc
        self._dc_curtailment = max(p_dc - self.get_max_dc_input_power(), 0)
        self._ac_potential_output = self.get_potential_pv_inverter_generation(p_dc)
        self._p_out, self._q_out = self._inverter.get_output_power(p_dc, self._volt)
        self._ac_curtailment = self._ac_potential_output - self._p_out
        return self._p_out, self._q_out

    def update(self, irrad, temp, volt):
        self._irrad = irrad
        self._temp = temp
        self._volt = volt

    def step(self):
        return self.get_output_power()

    @classmethod
    def get_output_power_cls(cls, s_inv, pmpp, irrad, temp):
        """This method serves as a baseline and generalised model of the PV system, used for OPF calculations"""
        pdc = PVPanels.get_dc_power_cls(pmpp, irrad, temp)
        return Inverter.get_output_power_cls(pdc, s_inv)


class HybridPVSystem(PVSystem):
    def __init__(self, circuit_label: int = None, pvpanels: PVPanels = None, battery: Battery = None, inverter: HybridInverter = None, meter: Meter = None):
        super().__init__(circuit_label, pvpanels, inverter, meter)
        self._battery = battery

    @property
    def battery(self):
        return self._battery

    def update(self, irrad, temp, volt):
        self._irrad = irrad
        self._temp = temp
        self._volt = volt
        self.inverter.update_battery_power_limits(self._battery.max_charge_power(), self._battery.max_discharge_power())

    def get_output_power(self, time_step=None):
        p_pv = self._pvpanels.get_dc_power(self._irrad, self._temp)
        self._dc_generation = p_pv
        load = self.meter.get_total_load_power() + max(0, self.meter.get_total_ev_power())
        """
        battery_power: charging (+), discharging (-)
        """
        p_batt = self.inverter.get_battery_power(p_pv, load, self._volt, time_step)
        if p_batt >= 0:
            self._battery.charge(p_batt)
        else:
            self._battery.discharge(p_batt)
        p_inv_dc = p_pv - p_batt
        self._dc_curtailment = max(p_inv_dc - self.get_max_dc_input_power(), 0)
        self._p_out, self._q_out = self.inverter.get_output_power(p_inv_dc, self._volt)

        self.update_ac_curtailment(p_pv, p_batt)
        return self._p_out, self._q_out

    def step(self, time_step=None):
        return self.get_output_power(time_step)

    # def update_dc_curtailment(self, p_pv, p_batt):
    #     if p_pv > 0:
    #         if p_batt > 0:
    #             self._ac_potential_output = self.get_potential_pv_inverter_generation(max(0, p_pv - p_batt))
    #             if self._ac_potential_output > 0:
    #                 self._ac_curtailment = self._ac_potential_output - self._p_out
    #             else:
    #                 self._ac_curtailment = 0.0
    #         else:
    #             self._ac_potential_output = self.get_potential_pv_inverter_generation(p_pv + abs(p_batt))
    #             self._ac_curtailment = self._ac_potential_output - self._p_out
    #     else:
    #         if p_batt > 0:
    #             self._ac_potential_output = 0.0
    #             self._ac_curtailment = 0.0
    #         else:
    #             self._ac_potential_output = self.get_potential_pv_inverter_generation(abs(p_batt))
    #             self._dc_curtailment = 0.0

    def update_ac_curtailment(self, p_pv, p_batt):
        if p_pv > 0:
            if p_batt > 0:
                self._ac_potential_output = self.get_potential_pv_inverter_generation(max(0, p_pv - p_batt))
                if self._ac_potential_output > 0:
                    self._ac_curtailment = self._ac_potential_output - self._p_out
                else:
                    self._ac_curtailment = 0.0
            else:
                self._ac_potential_output = self.get_potential_pv_inverter_generation(p_pv + abs(p_batt))
                self._ac_curtailment = self._ac_potential_output - self._p_out
        else:
            if p_batt > 0:
                self._ac_potential_output = 0.0
                self._ac_curtailment = 0.0
            else:
                self._ac_potential_output = self.get_potential_pv_inverter_generation(abs(p_batt))
                self._ac_curtailment = 0.0
