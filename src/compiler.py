import pandas as pd
from src.circuit_interface import CircuitInterface
from src.external_input_data import ModelInputData
import os
from copy import deepcopy
from src.models.load import Load
from src.models.pv_system import PVSystem, HybridPVSystem
from src.models.ev import EVSystem
from src.results import Results


class Compiler:
    """
    This is mainly inspired by OpenDER developed by EPRI, please see citation in the repo description.
    """

    # Converge criteria of V,P,Q
    V_TOLERANCE = 0.00001
    Q_TOLERANCE = 0.0006
    P_TOLERANCE = 0.0006

    def __init__(self, circuit: CircuitInterface = None, cers: [object] = None, model_data: ModelInputData = None):
        self._circuit = circuit
        self._cers = cers
        self._model_data = model_data
        self._cers_temp = None

        # P and Q steps for each convergence iteration
        self._delta_q = [0.5 for cer in self._cers]
        self._delta_p = [0.5 for cer in self._cers]
        self._converged = False
        self._v_converged = [False for cer in self._cers]
        self._q_converged = [False for cer in self._cers]
        self._p_converged = [False for cer in self._cers]

        self._p_out = [0 for cer in self._cers]
        self._q_out = [0 for cer in self._cers]

        self._p_inv = [0 for cer in self._cers]
        self._q_inv = [0 for cer in self._cers]

        self._p_previous = [0 for cer in self._cers]
        self._q_previous = [0 for cer in self._cers]

        self._current_v = [0 for cer in self._cers]
        self._previous_v = [0 for cer in self._cers]
        self._old_delta_v = [0 for cer in self._cers]

        self._p_check = [False for cer in self._cers]
        self._q_check = [False for cer in self._cers]

        # --- Parameterized update coefficients for delta-Q ---
        # When voltage change is high (relative to previous change)
        self._delta_q_decr_high = 0.1  # subtract when delta_v > 0.8 * old_delta_v
        self._delta_q_decr_low = 0.05  # subtract when delta_v > 0.6 * old_delta_v
        # When voltage change is low
        self._delta_q_incr_low = 0.10  # add when delta_v < 0.2 * old_delta_v
        self._delta_q_incr_high = 0.05  # add when delta_v < 0.4 * old_delta_v

        # --- Parameterized update coefficients for delta-P ---
        self._delta_p_decr_high = 0.1  # subtract when delta_v > 0.8 * old_delta_v
        self._delta_p_decr_low = 0.05  # subtract when delta_v > 0.6 * old_delta_v
        self._delta_p_incr_low = 0.10  # add when delta_v < 0.2 * old_delta_v
        self._delta_p_incr_high = 0.05  # add when delta_v < 0.4 * old_delta_v

    def run_cers(self, cers, time_step):
        # Read CER terminal voltages
        cer_voltages = self._circuit.get_cer_voltage(cers)
        for cer, volt in cer_voltages.items():
            # Update the voltages to CER objects, and Compute CER output power
            if isinstance(cer, Load):
                cer.update(self._model_data.demand_power[cer.circuit_label][time_step], volt)
            elif isinstance(cer, PVSystem):
                cer.update(self._model_data.irradiance[time_step], self._model_data.temperature[time_step], volt)
            elif isinstance(cer, HybridPVSystem):
                cer.update(self._model_data.irradiance[time_step], self._model_data.temperature[time_step], volt)
            elif isinstance(cer, EVSystem):
                cer.update(volt)
            if isinstance(cer, HybridPVSystem) or isinstance(cer, EVSystem):
                cer.step(time_step)
            else:
                cer.step()

    def _check_q(self):
        for i, cer in enumerate(self._cers):
            if isinstance(cer, PVSystem):
                if cer.inverter.vv_enabled:
                    self._q_check[i] = True
            elif isinstance(cer, HybridPVSystem):
                if cer.inverter.vv_enabled:
                    self._q_check[i] = True
            elif isinstance(cer, EVSystem):
                if cer.inverter.vv_enabled:
                    self._q_check[i] = True

    def _check_p(self):
        for i, cer in enumerate(self._cers):
            if isinstance(cer, PVSystem):
                if cer.inverter.vw_enabled:
                    self._p_check[i] = True
            elif isinstance(cer, HybridPVSystem):
                if cer.inverter.vw_enabled:
                    self._p_check[i] = True
            elif isinstance(cer, EVSystem):
                if cer.inverter.vw_enabled:
                    self._p_check[i] = True

    def _initialize_convergence(self):
        """
        Initialize the convergence process.
        """
        self._cl_first_iteration = True
        self._reset_converged()

        self._p_check = [False for der_obj in self._cers]
        self._q_check = [False for der_obj in self._cers]
        self._check_p()
        self._check_q()
        self._delta_p = [0.5 if p_check is True else None for p_check in self._p_check]
        self._delta_q = [0.5 if q_check is True else None for q_check in self._q_check]

    def _convergence_iteration(self):
        """
        Iteration for convergence process. Repeat the interation until the active power, reactive power, and terminal
        voltage of all the CERs in the circuit keep the same values. Convergence is reached at this point.
        """
        self._reset_converged()

        self._p_inv = [cer.p_out if isinstance(cer, PVSystem) or isinstance(cer, HybridPVSystem) else cer.p_in for cer in self._cers_temp]
        self._q_inv = [cer.q_out if isinstance(cer, PVSystem) or isinstance(cer, HybridPVSystem) else cer.q_in for cer in self._cers_temp]  # Where is the EVSystem
        self._current_v = [cer.volt for cer in self._cers_temp]
        self._change_delta_p_factor()
        self._change_delta_q_factor()
        if not self._cl_first_iteration:
            self._calculate_p_out()
            self._calculate_q_out()
            self._check_converged()
            self._previous_v = self._current_v
            self._p_previous = self._p_out
            self._q_previous = self._q_out
        else:
            self._cl_first_iteration = False
            self._previous_v = self._current_v
            self._p_previous = self._p_inv
            self._q_previous = self._q_inv

            self._p_out = self._p_inv
            self._q_out = self._q_inv

    def _reset_converged(self):
        """
        Reset convergence checkers.
        """
        self._converged = False
        self._v_converged = [False for cer_obj in self._cers]
        self._q_converged = [False for cer_obj in self._cers]
        self._p_converged = [False for cer_obj in self._cers]

    def _check_v_criteria(self):
        """
        Check if the CER terminal voltages keep the same values between convergence iterations.
        """
        for i in range(len(self._cers)):
            if abs(self._current_v[i] - self._previous_v[i]) <= self.__class__.V_TOLERANCE:
                self._v_converged[i] = True

    def _check_q_criteria(self):
        """
        Check if the CER output reactive powers are below set tolerance.
        """
        for i in range(len(self._cers)):
            if abs(self._q_out[i] - self._q_inv[i]) <= self.__class__.Q_TOLERANCE:
                self._q_converged[i] = True

    def _check_p_criteria(self):
        """
        Check if the CER output active powers are below set tolerance.
        """
        for i in range(len(self._cers)):
            if abs(self._p_out[i] - self._p_inv[i]) <= self.__class__.P_TOLERANCE:
                self._p_converged[i] = True

    def _check_converged(self):
        self._check_v_criteria()
        self._check_p_criteria()
        self._check_q_criteria()
        if all(self._v_converged) and all(self._q_converged) and all(self._p_converged):
            self._converged = True

    def _calculate_q_out(self):
        """
        For each iteration of convergence process, change only a certain percentage of CER output reactive power.
        """
        new_q_out = []
        for q_check, q_inv, delta_q, q_previous in zip(self._q_check, self._q_inv, self._delta_q, self._q_previous):
            if q_check:
                new_q = (q_inv - q_previous) * delta_q + q_previous
            else:
                new_q = q_inv
            new_q_out.append(new_q)
        self._q_out = new_q_out

    def _calculate_p_out(self):
        """
        For each iteration of convergence process, change only a certain percentage of CER output active power.
        """
        new_p_out = []
        for p_check, p_inv, delta_p, p_previous in zip(self._p_check, self._p_inv, self._delta_p, self._p_previous):
            if p_check:
                new_p = (p_inv - p_previous) * delta_p + p_previous
            else:
                new_p = p_inv
            new_p_out.append(new_p)
        self._p_out = new_p_out

    def cer_convergence_process(self, time_step):
        """
        Convergence process. This is done by repetitively running power flow solutions and updating CER outputs,
        until the convergence criteria for P, Q, V are met.
        """
        i = 0
        self._initialize_convergence()

        while not self._converged and i < 300:
            # Copy temporary CER objects so any calculation does not impact their soc variables if any.
            self._cers_temp = deepcopy(self._cers)
            # Run the temporary CER objects and update the outputs to circuit simulation
            self.run_cers(self._cers_temp, time_step)
            self._convergence_iteration()
            self._circuit.update_cer_output_powers({cer: [p_out, q_out] for cer, p_out, q_out in zip(self._cers_temp, self._p_out, self._q_out)})
            self._circuit.solve_power_flow()
            self._circuit.update_sys_voltage()
            i = i + 1
        # After iteration, the simulation should be converged. Run the actual CER objects and solve power flow.
        self.run_cers(self._cers, time_step)
        self._circuit.update_cer_output_powers({cer: [p_out, q_out] for cer, p_out, q_out in zip(self._cers, self._p_out, self._q_out)})
        self._circuit.solve_power_flow()
        self._circuit.update_sys_voltage()
        self._circuit.update_line_flow()
        self._circuit.update_circuit_metrics()
        self._collect_results(time_step)

        if self._converged:
            return self._p_out, self._q_out
        else:
            print('convergence error!')

    def _change_delta_q_factor(self):
        for i, delta_q in enumerate(self._delta_q):
            if delta_q is not None:
                delta_v = abs(self._current_v[i] - self._previous_v[i])
                if self._old_delta_v[i] >= 0.0:
                    if abs(delta_v) > 0.8 * self._old_delta_v[i] and delta_q > 0.2:
                        self._delta_q[i] -= self._delta_q_decr_high
                    elif abs(delta_v) > 0.6 * self._old_delta_v[i] and delta_q > 0.2:
                        self._delta_q[i] -= self._delta_q_decr_low
                    elif abs(delta_v) < 0.2 * self._old_delta_v[i] and delta_q < 0.9:
                        self._delta_q[i] += self._delta_q_incr_low
                    elif abs(delta_v) < 0.4 * self._old_delta_v[i] and delta_q < 0.9:
                        self._delta_q[i] += self._delta_q_incr_high
                self._old_delta_v[i] = abs(delta_v)

    def _change_delta_p_factor(self):
        for i, delta_p in enumerate(self._delta_p):
            if delta_p is not None:
                delta_v = abs(self._current_v[i] - self._previous_v[i])
                if self._old_delta_v[i] >= 0.0:
                    if abs(delta_v) > 0.8 * self._old_delta_v[i] and delta_p > 0.2:
                        self._delta_p[i] -= self._delta_p_decr_high
                    elif abs(delta_v) > 0.6 * self._old_delta_v[i] and delta_p > 0.2:
                        self._delta_p[i] -= self._delta_p_decr_low
                    elif abs(delta_v) < 0.2 * self._old_delta_v[i] and delta_p < 0.9:
                        self._delta_p[i] += self._delta_p_incr_low
                    elif abs(delta_v) < 0.4 * self._old_delta_v[i] and delta_p < 0.9:
                        self._delta_p[i] += self._delta_p_incr_high
                if self._delta_q[i] is None:
                    self._old_delta_v[i] = abs(delta_v)  # Be careful with cases where only volt watt is enabled!

    def change_delta_p_q_settings(self, settings):
        # --- Parameterized update coefficients for delta-Q ---
        # When voltage change is high (relative to previous change)
        delta_q_decr_high, delta_q_decr_low, delta_q_incr_low, delta_q_incr_high, \
            delta_p_decr_high, delta_p_decr_low, delta_p_incr_low, delta_p_incr_high = settings
        self._delta_q_decr_high = delta_q_decr_high  # subtract when delta_v > 0.8 * old_delta_v
        self._delta_q_decr_low = delta_q_decr_low  # subtract when delta_v > 0.6 * old_delta_v
        # When voltage change is low
        self._delta_q_incr_low = delta_q_incr_low  # add when delta_v < 0.2 * old_delta_v
        self._delta_q_incr_high = delta_q_incr_high  # add when delta_v < 0.4 * old_delta_v

        # --- Parameterized update coefficients for delta-P ---
        self._delta_p_decr_high = delta_p_decr_high  # subtract when delta_v > 0.8 * old_delta_v
        self._delta_p_decr_low = delta_p_decr_low  # subtract when delta_v > 0.6 * old_delta_v
        self._delta_p_incr_low = delta_p_incr_low  # add when delta_v < 0.2 * old_delta_v
        self._delta_p_incr_high = delta_p_incr_high  # add when delta_v < 0.4 * old_delta_v

    def _collect_results(self, time_step):
        Results.update_lines_results(self._circuit.get_lines_results())
        Results.update_buses_results(self._circuit.get_buses_results()[0])
        pv_set = list(self._circuit.pv_set.keys())
        ev_set = list(self._circuit.ev_set.keys())
        ac_curtailment = {key: 0.0 for key in pv_set}
        dc_curtailment = {key: 0.0 for key in pv_set}
        dc_generation = {key: 0.0 for key in pv_set}
        ac_potential_output = {key: 0.0 for key in pv_set}
        battery_stored_energy = {key: 0.0 for key in pv_set if "hybridpv_" in key}
        ev_battery_stored_energy = {key: 0.0 for key in ev_set}
        pv_reactive_power = {key: 0.0 for key in pv_set}
        pv_active_power = {key: 0.0 for key in pv_set}
        ev_reactive_power = {key: 0.0 for key in ev_set}
        ev_active_power = {key: 0.0 for key in ev_set}
        energy_flow = {}
        for cer in self._cers:
            if type(cer) == Load and cer.circuit_label in self._circuit.loads_only_circuit_labels:
                if cer.meter is not None:
                    energy_flow[cer.circuit_label] = cer.meter.get_energy_flow_results()

            elif type(cer) == HybridPVSystem:
                ac_curtailment[f'hybridpv_{cer.circuit_label}'] = cer.ac_curtailment
                dc_curtailment[f'hybridpv_{cer.circuit_label}'] = cer.dc_curtailment
                dc_generation[f'hybridpv_{cer.circuit_label}'] = cer.dc_generation
                ac_potential_output[f'hybridpv_{cer.circuit_label}'] = cer.ac_potential_output
                pv_reactive_power[f'hybridpv_{cer.circuit_label}'] = cer.q_out
                pv_active_power[f'hybridpv_{cer.circuit_label}'] = cer.p_out
                battery_stored_energy[f'hybridpv_{cer.circuit_label}'] = cer.battery.stored_energy
                if cer.meter is not None:
                    energy_flow[cer.circuit_label] = cer.meter.get_energy_flow_results()

            elif type(cer) == PVSystem:
                ac_curtailment[f'pv_{cer.circuit_label}'] = cer.ac_curtailment
                dc_curtailment[f'pv_{cer.circuit_label}'] = cer.dc_curtailment
                dc_generation[f'pv_{cer.circuit_label}'] = cer.dc_generation
                ac_potential_output[f'pv_{cer.circuit_label}'] = cer.ac_potential_output
                pv_reactive_power[f'pv_{cer.circuit_label}'] = cer.q_out
                pv_active_power[f'pv_{cer.circuit_label}'] = cer.p_out
                if cer.meter is not None:
                    energy_flow[cer.circuit_label] = cer.meter.get_energy_flow_results()
            elif type(cer) == EVSystem:
                ev_battery_stored_energy[f'ev_{cer.circuit_label}'] = cer.battery.stored_energy
                ev_reactive_power[f'ev_{cer.circuit_label}'] = cer.q_in
                ev_active_power[f'ev_{cer.circuit_label}'] = cer.p_in

        Results.update_inverter_register_results(ac_curtailment, dc_curtailment, dc_generation, ac_potential_output)
        Results.update_energy_flow_results(energy_flow)
        Results.update_battery_state_results(battery_stored_energy, ev_battery_stored_energy)
        Results.update_total_powers(self._circuit.metrics.loc[0, 'active_power'], self._circuit.metrics.loc[0, 'reactive_power'],
                                    self._circuit.metrics.loc[0, 'active_losses'], self._circuit.metrics.loc[0, 'reactive_losses'])

        Results._update_pv_reactive_power_results(pv_reactive_power)
        Results._update_pv_active_power_results(pv_active_power)
        Results._update_ev_reactive_power_results(ev_reactive_power)
        Results._update_ev_active_power_results(ev_active_power)

        Results.update_initial_voltages_results(self._circuit.get_buses_results()[1], time_stamp=time_step)


