import numpy as np
from math import sin, acos, sqrt, hypot, copysign
from scipy.optimize import root_scalar
from typing import Tuple


class StaticExportLimit:
    def __init__(self, export_limit):
        self._export_limit = export_limit

    @property
    def static_export_limit(self):
        return self._export_limit


class VoltWatt:
    def __init__(self, volt_watt_curve=None):
        if volt_watt_curve is None:
            volt_watt_curve = [[1, 1.07, 1.1], [1, 1, 0.2]]
        self._volt_watt_curve = volt_watt_curve

    def get_active_power_pu(self, volt):
        return np.interp(volt, self._volt_watt_curve[0], self._volt_watt_curve[1], left=self._volt_watt_curve[1][0], right=self._volt_watt_curve[1][-1])


class VoltVar:
    def __init__(self, volt_var_curve=None):
        if volt_var_curve is None:
            volt_var_curve = [[0.9, 0.95, 1.0, 1.05, 1.1], [0.6, 0, 0, 0, -0.6]]
        self._volt_var_curve = volt_var_curve

    def get_reactive_power_pu(self, volt):
        return np.interp(volt, self._volt_var_curve[0], self._volt_var_curve[1], left=self._volt_var_curve[1][0], right=self._volt_var_curve[1][-1])


class ConstantPowerFactor:
    def __init__(self, power_factor):
        self._power_factor = power_factor

    @property
    def constant_power_factor(self):
        return self._power_factor


class V2GEVCharging:
    def __init__(self, charging_times: list[tuple] = None, discharging_times: list[tuple] = None, step_size=None):
        self._charging_times = charging_times or [(10, 15)]
        self._discharging_times = discharging_times or [(15, 21)]
        self._step_size = step_size

    @property
    def charging_times(self):
        return self._charging_times

    @property
    def discharging_times(self):
        return self._discharging_times

    @property
    def step_size(self):
        return self._step_size


class ManagedEVCharging:
    def __init__(self, charging_times: list[tuple] = None, step_size=None):
        self._charging_times = charging_times or [(10, 15)]
        self._step_size = step_size

    @property
    def charging_times(self):
        return self._charging_times

    @property
    def step_size(self):
        return self._step_size


class UnmanagedEVCharging:
    def __init__(self, step_size=None):
        self._step_size = step_size

    @property
    def step_size(self):
        return self._step_size


class InverterSettings:
    def __init__(self):
        self._static_export_limit_settings = None
        self._volt_var_settings = None
        self._volt_watt_settings = None
        self._constant_power_factor_settings = None
        self._output_priority = 0
        self._en_export_limit = False
        self._en_volt_watt = False
        self._en_volt_var = False
        self._en_power_factor = False
        self._en_night_mode = True

    @property
    def en_export_limit(self):
        return self._en_export_limit

    @property
    def en_volt_watt(self):
        return self._en_volt_watt

    @property
    def en_volt_var(self):
        return self._en_volt_var

    @property
    def en_power_factor(self):
        return self._en_power_factor

    @property
    def en_night_mode(self):
        return self._en_night_mode

    def enable_static_export_limit(self, export_limit_settings: StaticExportLimit):
        self._static_export_limit_settings = export_limit_settings
        self._en_export_limit = True

    def enable_volt_watt(self, volt_watt_settings: VoltWatt):
        self._volt_watt_settings = volt_watt_settings
        self._en_volt_watt = True

    def enable_volt_var(self, volt_var_settings: VoltVar):
        self._volt_var_settings = volt_var_settings
        self._en_volt_var = True

    def enable_constant_power_factor(self, constant_power_factor_settings: ConstantPowerFactor):
        self._constant_power_factor_settings = constant_power_factor_settings
        self._en_power_factor = True

    def enable_night_mode(self):
        self._en_night_mode = True

    def set_output_priority(self, priority: str):
        if priority.lower() == 'watt':
            self._output_priority = 0
        elif priority.lower() == 'var':
            self._output_priority = 1
        elif priority.lower() == 'pf':
            self._output_priority = 2

    @property
    def static_export_limit(self):
        if self._en_export_limit:
            return self._static_export_limit_settings.static_export_limit
        else:
            return 0

    @property
    def power_factor(self):
        return self._constant_power_factor_settings.constant_power_factor

    @property
    def output_priority(self):
        return self._output_priority

    @property
    def watt_priority(self):
        if self.output_priority == 0:
            return True
        return False

    @property
    def var_priority(self):
        if self.output_priority == 1:
            return True
        return False

    @property
    def pf_priority(self):
        if self.output_priority == 2:
            return True
        return False


class Inverter:
    def __init__(self, circuit_label=None, rated_kva=6.0, eff_curve=None, cut_in=0.1, cut_out=0.1, inverter_settings: InverterSettings = None):
        self._circuit_label = circuit_label
        if eff_curve is None:
            eff_curve = [[0.1, 0.2, 0.4, 1.0], [0.86, 0.9, 0.93, 0.97]]
        self._rated_kva = rated_kva
        self._eff_curve = eff_curve
        self._cut_in = cut_in
        self._cut_out = cut_out
        self._inverter_settings = inverter_settings
        self._p_out = 0.0
        self._q_out = 0.0

    @property
    def circuit_label(self):
        return self._circuit_label

    @property
    def vw_enabled(self):
        return self._inverter_settings.en_volt_watt

    @property
    def vv_enabled(self):
        return self._inverter_settings.en_volt_var

    @property
    def el_enabled(self):
        return self._inverter_settings.en_export_limit

    @property
    def pf_enabled(self):
        return self._inverter_settings.en_power_factor

    @property
    def p_out(self):
        return self._p_out

    @property
    def q_out(self):
        return self._q_out

    @property
    def rated_kva(self):
        return self._rated_kva

    def get_inverter_eff(self, p_dc):
        pdc_pu = p_dc / self._rated_kva
        if pdc_pu > 1.0:
            pdc_pu = 1.0
        return np.interp(pdc_pu, self._eff_curve[0], self._eff_curve[1])

    def status(self, p_dc):
        if self._cut_in < self._cut_out:
            raise ValueError("cut-in value must be greater than or equal to cut-out value")
        if p_dc >= self._cut_in * self._rated_kva / 100:
            return True
        elif p_dc < self._cut_out * self._rated_kva / 100:
            return False
        return False

    def p_lim_min(self, volt) -> float:
        """
        :param volt:
        :return: Gives back the potential possible output of the inverter in kVA
        """
        if self.vw_enabled:
            if self.el_enabled:
                return min(self._rated_kva * self._inverter_settings.static_export_limit, self._rated_kva * self._inverter_settings._volt_watt_settings.get_active_power_pu(volt))
            return self._rated_kva * self._inverter_settings._volt_watt_settings.get_active_power_pu(volt)
        elif self.el_enabled:
            return self._rated_kva * self._inverter_settings.static_export_limit
        elif self.pf_enabled:
            return self._rated_kva * self._inverter_settings.power_factor
        else:
            return self._rated_kva

    def p_ac_desired(self, p_dc, volt) -> float:
        if not self.status(p_dc):
            return 0
        elif p_dc * self.get_inverter_eff(p_dc) >= self.p_lim_min(volt):
            return self.p_lim_min(volt)
        else:
            return p_dc * self.get_inverter_eff(p_dc)

    def q_ac_desired(self, p_dc, volt) -> float:
        if not self.status(p_dc) and not self._inverter_settings.en_night_mode:
            return 0.0
        elif self.pf_enabled:
            return self._rated_kva * sin(acos(self._inverter_settings.power_factor))
        elif self.vv_enabled:
            return self._rated_kva * self._inverter_settings._volt_var_settings.get_reactive_power_pu(volt)
        else:
            return 0.0

    def get_output_power(self, p_dc, volt) -> [float, float]:
        p_ac_desired = self.p_ac_desired(p_dc, volt)
        q_ac_desired = self.q_ac_desired(p_dc, volt)

        s_desired = hypot(p_ac_desired, q_ac_desired)
        if s_desired > self._rated_kva:
            # Determine if P and Q are set by mandatory functions
            mandatory_p = self.vw_enabled or self.el_enabled
            mandatory_q = self.vv_enabled or self._inverter_settings.en_power_factor

            if mandatory_p and mandatory_q:
                # Both P and Q are from mandatory settings: scale proportionally
                scale_factor = self._rated_kva / s_desired
                active_power = p_ac_desired * scale_factor
                reactive_power = q_ac_desired * scale_factor
            elif mandatory_p:
                # P is mandatory, adjust Q within remaining capacity
                active_power = p_ac_desired
                max_q = sqrt(self._rated_kva ** 2 - active_power ** 2)
                reactive_power = np.clip(q_ac_desired, -max_q, max_q)
            elif mandatory_q:
                # Q is mandatory, adjust P within remaining capacity
                reactive_power = q_ac_desired
                max_p = sqrt(self._rated_kva ** 2 - reactive_power ** 2)
                active_power = np.clip(p_ac_desired, -max_p, max_p)
            else:
                # No mandatory settings; use priority flags
                if self._inverter_settings.watt_priority:
                    active_power = np.clip(p_ac_desired, -self._rated_kva, self._rated_kva)
                    max_q = sqrt(self._rated_kva ** 2 - active_power ** 2)
                    reactive_power = np.clip(q_ac_desired, -max_q, max_q)
                elif self._inverter_settings.var_priority:
                    reactive_power = np.clip(q_ac_desired, -self._rated_kva, self._rated_kva)
                    max_p = sqrt(self._rated_kva ** 2 - reactive_power ** 2)
                    active_power = np.clip(p_ac_desired, -max_p, max_p)
                elif self._inverter_settings.pf_priority:
                    active_power = self._rated_kva * self._inverter_settings.power_factor
                    reactive_power = self._rated_kva * sin(acos(self._inverter_settings.power_factor))
                else:
                    # Default to watt priority if no priority specified
                    active_power = np.clip(p_ac_desired, -self._rated_kva, self._rated_kva)
                    max_q = sqrt(self._rated_kva ** 2 - active_power ** 2)
                    reactive_power = np.clip(q_ac_desired, -max_q, max_q)
        else:
            active_power = p_ac_desired
            reactive_power = q_ac_desired

        self._p_out = active_power
        self._q_out = reactive_power

        return active_power, reactive_power

    def get_pdc_from_efficiency(self, p_ac) -> float:
        """
        Returns the input p_dc that gives the desired p_ac.
        """

        def func(p_dc):
            return p_dc * self.get_inverter_eff(p_dc) - p_ac

        result = root_scalar(func, bracket=[0, 7.2])  # Change to pmpp
        if result.converged:
            return result.root
        else:
            raise ValueError(f"Could not find p_dc for output {p_ac}")

    @classmethod
    def get_output_power_cls(cls, p_dc: float, rated_kva: float, eff_curve: list = None, cut_in: float = 0.1, cut_out: float = 0.1) -> float:
        """
        Simplified inverter model (no Volt-Var/Watt, power factor, etc.).
        Returns active (P) power in kW.
        """
        # Default efficiency curve (pu DC power vs. efficiency)
        if eff_curve is None:
            eff_curve = [[0.1, 0.2, 0.4, 1.0], [0.86, 0.9, 0.93, 0.97]]
        # Check if inverter is ON (based on cut-in/out thresholds)
        cut_in_threshold = cut_in * rated_kva / 100  # Convert % to kW threshold
        cut_out_threshold = cut_out * rated_kva / 100
        if p_dc < cut_in_threshold or p_dc < cut_out_threshold:
            return 0.0  # Inverter OFF
        # Compute efficiency
        pdc_pu = min(p_dc / rated_kva, 1.0)  # Cap DC input power at rated kVA
        efficiency = np.interp(pdc_pu, eff_curve[0], eff_curve[1])
        # Compute active power (capped at rated kVA)
        p_out = min(p_dc * efficiency, rated_kva)
        return p_out


class MaximiseSelfConsumptionSettings:
    """
    Feeding the load from the pv generation and charging the battery from the excess pv-load energy, or feeding the load from battery when pv is low.
    For now this has no other options. Some options that can be incorporated include: activation time, charging form grid or pv only ... etc.
    """
    pass


class TimeOfUseSettings:
    """
    Charging the battery with pv excess and grid when the time is in the given interval, and discharge at the given interval.
    This class can accommodate more options such as priority, charging from grid or pv only ... etc.
    """

    def __init__(self, charging_times=None, discharging_times=None, step_size=None):
        if discharging_times is None:
            discharging_times = [15, 21]
        if charging_times is None:
            charging_times = [10, 15]
        self._charging_times = charging_times
        self._discharging_times = discharging_times
        if step_size is None:
            step_size = None
        self._step_size = step_size

    @property
    def charging_times(self):
        return self._charging_times

    @property
    def discharging_times(self):
        return self._discharging_times

    @property
    def step_size(self):
        return self._step_size


class HybridInverterSettings(InverterSettings):
    def __init__(self):
        super().__init__()  # to be completed, but we need to add another field for the charging volt-watt curve :)
        self._charging_volt_watt_settings = None
        self._maximise_self_consumption_settings = None
        self._time_of_use_settings = None
        self._en_charging_volt_watt = False
        self._en_maximise_self_consumption_settings = False
        self._en_time_of_use_settings = False

    @property
    def en_maximise_self_consumption(self):
        return self._en_maximise_self_consumption_settings

    @property
    def en_time_of_use(self):
        return self._en_time_of_use_settings

    @property
    def en_charging_volt_watt(self):
        return self._en_charging_volt_watt

    def enable_charging_volt_watt_settings(self, charging_volt_watt_settings: VoltWatt):
        self._charging_volt_watt_settings = charging_volt_watt_settings
        self._en_charging_volt_watt = True

    def enable_maximise_self_consumption_settings(self, maximise_self_consumption_settings: MaximiseSelfConsumptionSettings):
        self._maximise_self_consumption_settings = maximise_self_consumption_settings
        self._en_maximise_self_consumption_settings = True

    def enable_time_of_use_settings(self, time_of_use_settings: TimeOfUseSettings):
        self._time_of_use_settings = time_of_use_settings
        self._en_time_of_use_settings = True

    @property
    def charging_times(self):
        if self._en_time_of_use_settings:
            return self._time_of_use_settings.charging_times
        return None

    @property
    def discharging_times(self):
        if self._en_time_of_use_settings:
            return self._time_of_use_settings.discharging_times
        return None

    @property
    def step_size(self):
        if self._en_time_of_use_settings:
            return self._time_of_use_settings.step_size
        return None


class EVInverterSettings(InverterSettings):
    def __init__(self):
        super().__init__()  # to be completed, but we need to add another field for the charging volt-watt curve :)
        self._charging_volt_watt_settings = None
        self._en_charging_volt_watt = False
        self._unmanaged_charging = None
        self._managed_charging = None
        self._v2g_charging = None
        self._en_unmanaged_charging = False
        self._en_managed_charging = False
        self._en_v2g_charging = False

    @property
    def en_charging_volt_watt(self):
        return self._en_charging_volt_watt

    @property
    def en_unmanaged_charging(self):
        return self._en_unmanaged_charging

    @property
    def en_managed_charging(self):
        return self._en_managed_charging

    @property
    def en_v2g_charging(self):
        return self._en_v2g_charging

    def enable_charging_volt_watt_settings(self, charging_volt_watt_settings: VoltWatt):
        self._charging_volt_watt_settings = charging_volt_watt_settings
        self._en_charging_volt_watt = True

    def enable_unmanaged_charging(self, unmanaged_charging: UnmanagedEVCharging):
        self._unmanaged_charging = unmanaged_charging
        self._en_unmanaged_charging = True

    def enable_managed_charging(self, managed_charging: ManagedEVCharging):
        self._managed_charging = managed_charging
        self._en_managed_charging = True

    def enable_v2g_charging(self, v2g_charging: V2GEVCharging):
        self._v2g_charging = v2g_charging
        self._en_v2g_charging = True

    @property
    def charging_times(self):
        if self._en_managed_charging:
            return self._managed_charging.charging_times
        elif self._en_v2g_charging:
            return self._v2g_charging.charging_times
        else:
            return None

    @property
    def discharging_times(self):
        if self._en_v2g_charging:
            return self._v2g_charging.discharging_times
        else:
            return None

    @property
    def step_size(self):
        if self._en_managed_charging:
            return self._managed_charging.step_size
        elif self._en_v2g_charging:
            return self._v2g_charging.step_size
        elif self._en_unmanaged_charging:
            return self._unmanaged_charging.step_size
        return None


class HybridInverter(Inverter):
    def __init__(self, circuit_label=None, rated_kva=6, eff_curve=None, cut_in=0.1, cut_out=0.1, hybrid_inverter_settings: HybridInverterSettings = None):
        super().__init__(circuit_label, rated_kva, eff_curve, cut_in, cut_out, hybrid_inverter_settings)
        self._hybrid_inverter_settings = hybrid_inverter_settings
        self._battery_power = 0.0
        self._max_battery_charge_power = None
        self._max_battery_discharge_power = None

    @property
    def battery_power(self):
        return self._battery_power

    @property
    def vw_ch_enabled(self):
        return self._hybrid_inverter_settings.en_charging_volt_watt

    def update_battery_power_limits(self, max_charge: float, max_discharge: float) -> None:
        self._max_battery_charge_power = max_charge
        self._max_battery_discharge_power = max_discharge

    def max_input_ac_power(self, volt):
        return self._rated_kva  # sqrt(self._rated_kva ** 2 - self.q_ac_desired(0.5 * self._rated_kva, volt) ** 2)
        # If no VARs when charging from grid then max input AC power is the rated power
        # Till now we have no VARs when charging, maybe to be adjusted in the future.
        # the 0.5 * self._rated_kva just to make the q_ac_desired method pass the status ON condition

    def p_ch_lim_min(self, volt) -> float:
        if self.vw_ch_enabled:
            return self.max_input_ac_power(volt) * self._hybrid_inverter_settings._charging_volt_watt_settings.get_active_power_pu(volt)
        else:
            return self.max_input_ac_power(volt)

    def get_battery_power(self, p_pv, load, volt, time_step):
        """
        battery_power: charging (+), discharging (-)
        """
        self._battery_power = - self.get_battery_power_to_inverter(p_pv, load, volt, time_step) + self.get_pv_power_to_battery(p_pv, load, volt, time_step) + \
                              self.get_inverter_power_to_battery(p_pv, load, volt, time_step)

        return self._battery_power

    def get_output_power(self, p_dc, volt) -> Tuple[float, float]:
        """
        This is an overridden version of the get_output_power from the Inverter class.
        The main difference is this should account for the battery power.
        """
        if p_dc >= 0.0:
            return super().get_output_power(p_dc, volt)
        else:
            self._p_out = - self.get_ac_from_efficiency_for_charging(abs(p_dc))
            self._q_out = 0.0
            return self._p_out, self._q_out
            # No VArs when charging from grid?? Maybe this is sth related to night mode, but should be adjusted in the future.

    def get_dc_power_to_meet_load(self, p_pv, load, volt) -> float:
        if load >= super().get_output_power(self.get_pdc_from_efficiency(self._rated_kva), volt)[0]:
            # if load is greater than the possible output of the inverter, then that's the max power.
            return self.get_pdc_from_efficiency(super().get_output_power(p_pv, volt)[0])
        return self.get_pdc_from_efficiency(load)

    def get_battery_power_to_inverter(self, p_pv, load=None, volt=None, time_step=None) -> float:
        if self._hybrid_inverter_settings.en_maximise_self_consumption:
            p_dc_required = self.get_dc_power_to_meet_load(p_pv, load, volt)
            return min(max(0.0, p_dc_required - p_pv), self._max_battery_discharge_power)
        elif self._hybrid_inverter_settings.en_time_of_use:
            if self._hybrid_inverter_settings.discharging_times[0] <= time_step * (self._hybrid_inverter_settings.step_size / 60) < \
                    self._hybrid_inverter_settings.discharging_times[1]:
                return min(max(0, self.get_pdc_from_efficiency(super().get_output_power(self.get_pdc_from_efficiency(self._rated_kva), volt)[0]) - p_pv),
                           self._max_battery_discharge_power)
                # discharge the remaining room between the available pv and max dc input
            return 0.0

    def get_pv_power_to_battery(self, p_pv, load=None, volt=None, time_step=None) -> float:
        if self._hybrid_inverter_settings.en_maximise_self_consumption:
            p_dc_required = self.get_dc_power_to_meet_load(p_pv, load, volt)
            return min(max(0.0, p_pv - p_dc_required), self._max_battery_charge_power)
        elif self._hybrid_inverter_settings.en_time_of_use:
            if self._hybrid_inverter_settings.charging_times[0] <= time_step * (self._hybrid_inverter_settings.step_size / 60) < self._hybrid_inverter_settings.charging_times[1]:
                return min(p_pv, self._max_battery_charge_power)
            return 0.0

    def get_inverter_power_to_battery(self, p_pv, load=None, volt=None, time_step=None) -> float:
        if self._hybrid_inverter_settings.en_maximise_self_consumption:
            return 0.0
        elif self._hybrid_inverter_settings.en_time_of_use:
            if self._hybrid_inverter_settings.charging_times[0] <= time_step * (self._hybrid_inverter_settings.step_size / 60) < self._hybrid_inverter_settings.charging_times[1]:
                if self._max_battery_charge_power - self.get_pv_power_to_battery(p_pv, load, volt, time_step) > 0.0:
                    p_ch_dc_required = self._max_battery_charge_power - self.get_pv_power_to_battery(p_pv, load, volt, time_step)
                    p_ch_dc_available = self.p_ch_lim_min(volt) * self.get_inverter_eff(self.p_ch_lim_min(volt))
                    return min(p_ch_dc_available, p_ch_dc_required)
            return 0.0

    def get_ac_from_efficiency_for_charging(self, p_dc) -> float:
        """
        Returns the input p_dc that gives the desired p_ac.
        """

        def func(p_ac):
            return p_ac * self.get_inverter_eff(p_ac) - p_dc

        result = root_scalar(func, bracket=[0, self._rated_kva])
        if result.converged:
            return result.root
        else:
            raise ValueError(f"Could not find p_dc for output {p_dc}")

    def set_battery_power(self, battery_power: float) -> None:
        """
        To be set after running the battery model to see how much power it can either charge or discharge.
        :param battery_power: if charging (+), elif discharging (-)
        :return: None
        """
        self._battery_power = battery_power


class EVInverter(Inverter):
    def __init__(self, circuit_label=None, rated_kva=6.0, eff_curve=None, cut_in=0.1, cut_out=0.1, ev_inverter_settings: EVInverterSettings = None):
        super().__init__(circuit_label, rated_kva, eff_curve, cut_in, cut_out, ev_inverter_settings)
        self._ev_inverter_settings = ev_inverter_settings
        self._battery_power = None
        self._energy_per_distance = None
        self._max_battery_charge_power = None
        self._max_battery_discharge_power = None

    @property
    def vw_ch_enabled(self):
        return self._ev_inverter_settings.en_charging_volt_watt

    def update_battery_power_limits(self, energy_per_distance: float, max_charge: float, max_discharge: float) -> None:
        self._energy_per_distance = energy_per_distance
        self._max_battery_charge_power = max_charge
        self._max_battery_discharge_power = max_discharge

    def max_input_ac_power(self, volt):
        return self._rated_kva  # sqrt(self._rated_kva ** 2 - self.q_ac_desired(0.5 * self._rated_kva, volt) ** 2)
        # the 0.5 * self._rated_kva just to make the q_ac_desired method pass the status ON condition

    def p_ch_lim_min(self, volt) -> float:
        if self.vw_ch_enabled:
            return self.max_input_ac_power(volt) * self._ev_inverter_settings._charging_volt_watt_settings.get_active_power_pu(volt)
        else:
            return self.max_input_ac_power(volt)

    def get_battery_power(self, volt, is_at_home, distance, time_step):
        """
        battery_power: charging (+), discharging (-)
        """
        self._battery_power = - self.get_battery_power_to_inverter(volt, is_at_home, time_step) - self.get_battery_power_to_wheel(is_at_home, distance) + \
                              self.get_inverter_power_to_battery(volt, is_at_home, time_step)

        return self._battery_power

    def get_output_power(self, p_dc, volt) -> Tuple[float, float]:
        """
        This is an overridden version of the get_output_power from the Inverter class.
        The main difference is this should account for the battery power.
        """
        if p_dc >= 0.0:
            return self.get_ac_from_efficiency_for_charging(p_dc), 0.0
            # No VArs when charging?? Maybe this is sth related to night mode, but should be adjusted in the future.
        else:
            p, q = super().get_output_power(abs(p_dc), volt)
            return -p, -q

    def get_battery_power_to_inverter(self, volt=None, is_at_home: bool = None, time_step=None) -> float:
        if self._ev_inverter_settings.en_unmanaged_charging:
            return 0.0
        elif self._ev_inverter_settings.en_managed_charging:
            return 0.0
        elif self._ev_inverter_settings.en_v2g_charging:
            if is_at_home:
                if self.check_ev_in_discharging_times(time_step):
                    return min(self.get_pdc_from_efficiency(super().get_output_power(self._max_battery_discharge_power, volt)[0]),
                               self._max_battery_discharge_power)  # inverter kva is equal to battery charger power
                return 0.0
            return 0.0

    def get_battery_power_to_wheel(self, is_at_home: bool, distance: float) -> float:
        if not is_at_home:
            return min(distance * self._energy_per_distance / (self._ev_inverter_settings.step_size / 60), self._max_battery_discharge_power)
        return 0.0

    def get_inverter_power_to_battery(self, volt: float, is_at_home: bool, time_step: float) -> float:
        if self._ev_inverter_settings.en_unmanaged_charging:
            if is_at_home:
                return min(self.p_ch_lim_min(volt) * self.get_inverter_eff(self.p_ch_lim_min(volt)), self._max_battery_charge_power)
            return 0.0
        elif self._ev_inverter_settings.en_managed_charging:
            if is_at_home:
                if self.check_ev_in_charging_times(time_step):
                    return min(self.p_ch_lim_min(volt) * self.get_inverter_eff(self.p_ch_lim_min(volt)), self._max_battery_charge_power)
                return 0.0
            return 0.0
        elif self._ev_inverter_settings.en_v2g_charging:
            if is_at_home:
                if self.check_ev_in_charging_times(time_step):
                    return min(self.p_ch_lim_min(volt) * self.get_inverter_eff(self.p_ch_lim_min(volt)), self._max_battery_charge_power)
                return 0.0
            return 0.0

    def get_pdc_from_efficiency(self, p_ac) -> float:
        """
        Returns the input p_dc that gives the desired p_ac.
        """

        def func(p_dc):
            return p_dc * self.get_inverter_eff(p_dc) - p_ac

        result = root_scalar(func, bracket=[0, 7.2])
        if result.converged:
            return result.root
        else:
            raise ValueError(f"Could not find p_dc for output {p_ac}")

    def get_ac_from_efficiency_for_charging(self, p_dc) -> float:
        """
        Returns the input p_dc that gives the desired p_ac.
        """

        def func(p_ac):
            return p_ac * self.get_inverter_eff(p_ac) - p_dc

        result = root_scalar(func, bracket=[0, self._rated_kva])
        if result.converged:
            return result.root
        else:
            raise ValueError(f"Could not find p_dc for output {p_dc}")

    def check_ev_in_charging_times(self, time_step):
        if self._ev_inverter_settings.charging_times is None:
            print("The charging mode has to be either set at managed or v2g charging.")
        if sum([1 if interval[0] <= time_step * (self._ev_inverter_settings.step_size / 60) < interval[1] else 0 for interval in self._ev_inverter_settings.charging_times]) == 0:
            return False
        else:
            return True

    def check_ev_in_discharging_times(self, time_step):
        if self._ev_inverter_settings.discharging_times is None:
            print("The discharging mode has to be set at v2g charging.")
        if sum([1 if interval[0] <= time_step * (self._ev_inverter_settings.step_size / 60) < interval[1] else 0 for interval in
                self._ev_inverter_settings.discharging_times]) == 0:
            return False
        else:
            return True
