import os.path
from datetime import time, datetime, timedelta
import pandas as pd
import numpy as np
from src.utils import intersection, remove_sublist
from src.models.meter import Meter
from typing import Dict
from math import radians
import csv


def symmetrical_components(magnitudes, angles):
    # Convert to rectangular form (complex numbers)
    V_A = magnitudes[0] * np.exp(1j * np.radians(angles[0]))
    V_B = magnitudes[1] * np.exp(1j * np.radians(angles[1]))
    V_C = magnitudes[2] * np.exp(1j * np.radians(angles[2]))

    # Rotation operator
    a = np.exp(1j * 2 * np.pi / 3)  # e^(j120°)
    a2 = a ** 2  # e^(j240°)

    # Compute symmetrical components
    V_0 = (V_A + V_B + V_C) / 3
    V_1 = (V_A + a * V_B + a2 * V_C) / 3
    V_2 = (V_A + a2 * V_B + a * V_C) / 3

    return abs(V_0), abs(V_1), abs(V_2)


def create_time_series(start_time, end_time, step):
    series = []
    while not start_time == end_time:
        series.append(start_time.strftime("%H: %M"))
        start_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=step)).time()
    series.append(end_time.strftime("%H: %M"))
    return series


class classproperty:
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, cls):
        # ignore 'obj', always call with the class
        return self.f(cls)


class Results:
    VOLTAGE_UNBALANCE_HISTORY, TOTAL_LOSSES, TOTAL_POWER = None, None, None
    VOLTAGE_HISTORY_A, VOLTAGE_HISTORY_B, VOLTAGE_HISTORY_C = None, None, None
    INITIAL_VOLTAGES = None
    POWER_HISTORY_A, POWER_HISTORY_B, POWER_HISTORY_C = None, None, None
    RE_POWER_HISTORY_A, RE_POWER_HISTORY_B, RE_POWER_HISTORY_C = None, None, None
    LINE_CURRENT_A, LINE_CURRENT_B, LINE_CURRENT_C, LINE_RATINGS_A, LINE_RATINGS_B, LINE_RATINGS_C = None, None, None, None, None, None
    AC_CURTAILMENT_A, AC_CURTAILMENT_B, AC_CURTAILMENT_C, DC_CURTAILMENT_A, DC_CURTAILMENT_B, DC_CURTAILMENT_C = None, None, None, None, None, None
    ENERGY_FLOWS = None
    PV_DC_GENERATION, PV_INVERTER_POTENTIAL_OUTPUT, BATTERY_STORED_ENERGY, EV_STORED_ENERGY = None, None, None, None
    PV_INVERTER_REACTIVE_POWER, PV_INVERTER_ACTIVE_POWER = None, None
    EV_INVERTER_REACTIVE_POWER, EV_INVERTER_ACTIVE_POWER = None, None
    METRICS = None
    SIMULATION_TIME = None
    STEP_SIZE = None

    @classmethod
    def initialise(cls, time_interval: [time, time, int], end_buses, lines_rating, pv_set, meters: {Meter}, ev_set=None, step_size=None):
        if ev_set is None:
            ev_set = {}
        if pv_set is None:
            pv_set = {}
        if meters is None:
            meters = {}
        """Initialize class-level attributes based on `load_buses` and `lines_rating`."""
        # Time Series
        cls.TIME_SERIES = create_time_series(time_interval[0], time_interval[1], time_interval[2])
        cls.SIMULATION_TIME = []
        # Voltage histories
        cls.VOLTAGE_HISTORY_A = {key: [] for key in end_buses if '.1' in key}
        cls.VOLTAGE_HISTORY_B = {key: [] for key in end_buses if '.2' in key}
        cls.VOLTAGE_HISTORY_C = {key: [] for key in end_buses if '.3' in key}
        # Voltage unbalance history
        cls.VOLTAGE_UNBALANCE_HISTORY = {bus.split('.')[0]: [] for bus in cls.VOLTAGE_HISTORY_A.keys()}
        # Line currents
        cls.LINE_RATINGS_A = {f"{line}.1": rating for line, rating in lines_rating.items()}
        cls.LINE_RATINGS_B = {f"{line}.2": rating for line, rating in lines_rating.items()}
        cls.LINE_RATINGS_C = {f"{line}.3": rating for line, rating in lines_rating.items()}
        cls.LINE_CURRENT_A = {f"{line}.1": [] for line, rating in lines_rating.items()}
        cls.LINE_CURRENT_B = {f"{line}.2": [] for line, rating in lines_rating.items()}
        cls.LINE_CURRENT_C = {f"{line}.3": [] for line, rating in lines_rating.items()}
        # Total powers
        cls.TOTAL_POWER = {'Active': [], 'Reactive': []}
        cls.TOTAL_LOSSES = {'Active': [], 'Reactive': []}
        # AC and DC Curtailment in kWh
        cls.AC_CURTAILMENT_A = {key: [] for key, bus in pv_set.items() if '.' in bus and bus.split('.', 1)[1] == '1'}
        cls.AC_CURTAILMENT_B = {key: [] for key, bus in pv_set.items() if '.' in bus and bus.split('.', 1)[1] == '2'}
        cls.AC_CURTAILMENT_C = {key: [] for key, bus in pv_set.items() if '.' in bus and bus.split('.', 1)[1] == '3'}
        cls.DC_CURTAILMENT_A = {key: [] for key, bus in pv_set.items() if '.' in bus and bus.split('.', 1)[1] == '1'}
        cls.DC_CURTAILMENT_B = {key: [] for key, bus in pv_set.items() if '.' in bus and bus.split('.', 1)[1] == '2'}
        cls.DC_CURTAILMENT_C = {key: [] for key, bus in pv_set.items() if '.' in bus and bus.split('.', 1)[1] == '3'}
        # Energy flows
        cls.ENERGY_FLOWS = {label: meters[label].initialise_energy_flow_results() for label in meters.keys()}
        # AC and DC Curtailment in kWh
        cls.PV_DC_GENERATION = {key: [] for key in pv_set.keys()}
        cls.PV_INVERTER_POTENTIAL_OUTPUT = {key: [] for key in pv_set.keys()}
        cls.PV_INVERTER_REACTIVE_POWER = {key: [] for key in pv_set.keys()}
        cls.PV_INVERTER_ACTIVE_POWER = {key: [] for key in pv_set.keys()}
        cls.BATTERY_STORED_ENERGY = {key: [] for key in pv_set.keys() if "hybridpv_" in key}
        cls.EV_INVERTER_REACTIVE_POWER = {key: [] for key in ev_set.keys()}
        cls.EV_INVERTER_ACTIVE_POWER = {key: [] for key in ev_set.keys()}
        cls.EV_STORED_ENERGY = {key: [] for key in ev_set.keys()}
        # Metrics
        cls.METRICS = {'Metric 1.a': [0], 'Metric 1.b': [0], 'Metric 2': [0], 'Metric 3': [0], 'Metric 4': [0], 'Metric 5.a': [0], 'Metric 5.b': [0]}

        # Initial voltages for OPF
        cls.INITIAL_VOLTAGES = {'bus_i': [], 'phase_i': [], 'time': [], 'v_nom': [], 'v_pu': [], 'v_angle': []}

        cls.STEP_SIZE = step_size

    @classmethod
    def update_buses_results(cls, bus_results: pd.DataFrame) -> None:
        cls._update_bus_voltage_results(bus_results)
        cls._update_voltage_unbalance_results(bus_results)

    @classmethod
    def update_initial_voltages_results(cls, bus_results: pd.DataFrame, time_stamp: float) -> None:
        cls._update_initial_voltages_results(bus_results, time_stamp)

    @classmethod
    def update_lines_results(cls, line_results: pd.DataFrame) -> None:
        cls._update_line_current_results(line_results)
        # cls._update_losses_results(line_results)

    @classmethod
    def update_inverter_register_results(cls, ac_curtailment: dict, dc_curtailment: dict, dc_generation: dict, ac_potential_output: dict) -> None:
        cls._update_ac_curtailment_results(ac_curtailment)
        cls._update_dc_curtailment_results(dc_curtailment)
        cls._update_dc_generation_results(dc_generation)
        cls._update_ac_potential_output_results(ac_potential_output)

    @classmethod
    def update_battery_state_results(cls, battery_states: dict, ev_battery_state: dict):
        cls._update_battery_state_results(battery_states)
        cls._update_ev_battery_state_results(ev_battery_state)

    @classmethod
    def update_energy_flow_results(cls, energy_flow):
        cls._update_energy_flow_results(energy_flow)

    @classmethod
    def _update_initial_voltages_results(cls, bus_results: pd.DataFrame, time_stamp: float) -> None:
        """Add voltage result to the appropriate history."""
        bus_results_copy = bus_results.copy()
        bus_results_copy = bus_results_copy.reset_index()
        for bus_i, phase_i, v_nom, v_pu, v_angle in bus_results_copy[['bus_i', 'phase_i', 'v_base_ln', 'v_pu', 'angle']].values:
            cls.INITIAL_VOLTAGES['bus_i'].append(bus_i)
            cls.INITIAL_VOLTAGES['phase_i'].append(phase_i)
            cls.INITIAL_VOLTAGES['v_nom'].append(v_nom)
            cls.INITIAL_VOLTAGES['time'].append(time_stamp * cls.STEP_SIZE / 60)
            cls.INITIAL_VOLTAGES['v_pu'].append(v_pu)
            cls.INITIAL_VOLTAGES['v_angle'].append(radians(v_angle))

    @classproperty
    def initial_voltages(cls):
        return pd.DataFrame(cls.INITIAL_VOLTAGES)

    @classmethod
    def update_simulation_time(cls, time_spent):
        cls.SIMULATION_TIME.append(time_spent)

    @classmethod
    def _update_bus_voltage_results(cls, bus_results: pd.DataFrame) -> None:
        """Add voltage result to the appropriate history."""
        bus_results_copy = bus_results.copy()
        bus_results_copy = bus_results_copy.reset_index()
        bus_results_copy = bus_results_copy.set_index('name')
        for bus in cls.VOLTAGE_HISTORY_A.keys():
            cls.VOLTAGE_HISTORY_A[bus].append(bus_results_copy.loc[bus, 'v_pu'])
        for bus in cls.VOLTAGE_HISTORY_B.keys():
            cls.VOLTAGE_HISTORY_B[bus].append(bus_results_copy.loc[bus, 'v_pu'])
        for bus in cls.VOLTAGE_HISTORY_C.keys():
            cls.VOLTAGE_HISTORY_C[bus].append(bus_results_copy.loc[bus, 'v_pu'])

    @classmethod
    def _update_voltage_unbalance_results(cls, bus_results: pd.DataFrame) -> None:
        """Add voltage result to the appropriate history."""
        bus_results_copy = bus_results.copy()
        bus_results_copy = bus_results_copy.reset_index()
        # bus_results_copy = bus_results_copy.set_index('name')
        for bus in cls.VOLTAGE_UNBALANCE_HISTORY.keys():
            voltages = list((bus_results_copy[bus_results_copy['name'].str.split('.').str[0] == bus])['v_pu'].values)
            angles = list((bus_results_copy[bus_results_copy['name'].str.split('.').str[0] == bus])['angle'].values)
            _, V_1, V_2 = symmetrical_components(voltages, angles)
            cls.VOLTAGE_UNBALANCE_HISTORY[bus].append(100 * (V_2 / V_1))

    @classmethod
    def add_power_results(cls, bus, power):
        """Add power result to the appropriate history."""
        if bus in cls.POWER_HISTORY_A:
            cls.POWER_HISTORY_A[bus].append(power)
        elif bus in cls.POWER_HISTORY_B:
            cls.POWER_HISTORY_B[bus].append(power)
        elif bus in cls.POWER_HISTORY_C:
            cls.POWER_HISTORY_C[bus].append(power)

    @classmethod
    def add_reactive_power_results(cls, bus, reactive_power):
        """Add reactive power result to the appropriate history."""
        if bus in cls.RE_POWER_HISTORY_A:
            cls.RE_POWER_HISTORY_A[bus].append(reactive_power)
        elif bus in cls.RE_POWER_HISTORY_B:
            cls.RE_POWER_HISTORY_B[bus].append(reactive_power)
        elif bus in cls.RE_POWER_HISTORY_C:
            cls.RE_POWER_HISTORY_C[bus].append(reactive_power)

    @classmethod
    def _update_line_current_results(cls, line_results: pd.DataFrame) -> None:
        """Add line current result to the appropriate history."""
        line_results_copy = line_results.copy()
        line_results_copy = line_results_copy.reset_index()
        lines = list(line_results_copy['name'].values)
        line_results_copy = line_results_copy.set_index('name')
        for line in lines:
            cls.LINE_CURRENT_A[f"{line}.1"].append(100 * line_results_copy.loc[line, 'i_a'] / cls.LINE_RATINGS_A[f"{line}.1"])
            cls.LINE_CURRENT_B[f"{line}.2"].append(100 * line_results_copy.loc[line, 'i_b'] / cls.LINE_RATINGS_B[f"{line}.2"])
            cls.LINE_CURRENT_C[f"{line}.3"].append(100 * line_results_copy.loc[line, 'i_c'] / cls.LINE_RATINGS_C[f"{line}.3"])

    # @classmethod
    # def _update_losses_results(cls, line_results: pd.DataFrame) -> None:
    #     """Add line current result to the appropriate history."""
    #     line_results_copy = line_results.copy()
    #     line_results_copy = line_results_copy.reset_index()
    #     line_results_copy = line_results_copy.set_index('name')
    #     cls.TOTAL_LOSSES['Active'] += line_results_copy['losses_active'].sum() * cls.STEP_SIZE / 60
    #     cls.TOTAL_LOSSES['Reactive'] += line_results_copy['losses_reactive'].sum() * cls.STEP_SIZE / 60

    @classmethod
    def _update_ac_curtailment_results(cls, ac_curtailment: dict) -> None:
        """Add voltage result to the appropriate history."""
        for pv in cls.AC_CURTAILMENT_A.keys():
            cls.AC_CURTAILMENT_A[pv].append(ac_curtailment[pv])
        for pv in cls.AC_CURTAILMENT_B.keys():
            cls.AC_CURTAILMENT_B[pv].append(ac_curtailment[pv])
        for pv in cls.AC_CURTAILMENT_C.keys():
            cls.AC_CURTAILMENT_C[pv].append(ac_curtailment[pv])

    @classmethod
    def _update_dc_curtailment_results(cls, dc_curtailment: dict) -> None:
        """Add voltage result to the appropriate history."""
        for pv in cls.DC_CURTAILMENT_A.keys():
            cls.DC_CURTAILMENT_A[pv].append(dc_curtailment[pv])
        for pv in cls.DC_CURTAILMENT_B.keys():
            cls.DC_CURTAILMENT_B[pv].append(dc_curtailment[pv])
        for pv in cls.DC_CURTAILMENT_C.keys():
            cls.DC_CURTAILMENT_C[pv].append(dc_curtailment[pv])

    @classmethod
    def _update_dc_generation_results(cls, dc_generation: dict) -> None:
        """Add dc generation result to the appropriate history."""
        for pv in cls.PV_DC_GENERATION.keys():
            cls.PV_DC_GENERATION[pv].append(dc_generation[pv])

    @classmethod
    def _update_ac_potential_output_results(cls, ac_potential_output):
        """Add dc generation result to the appropriate history."""
        for pv in cls.PV_INVERTER_POTENTIAL_OUTPUT.keys():
            cls.PV_INVERTER_POTENTIAL_OUTPUT[pv].append(ac_potential_output[pv])

    @classmethod
    def _update_battery_state_results(cls, battery_states: dict) -> None:
        """Add battery energy result to the appropriate history."""
        for pv in cls.BATTERY_STORED_ENERGY.keys():
            cls.BATTERY_STORED_ENERGY[pv].append(battery_states[pv])

    @classmethod
    def _update_ev_battery_state_results(cls, ev_battery_states: dict) -> None:
        """Add ev battery energy result to the appropriate history."""
        for ev in cls.EV_STORED_ENERGY.keys():
            cls.EV_STORED_ENERGY[ev].append(ev_battery_states[ev])

    @classmethod
    def _update_energy_flow_results(cls, energy_flow: dict) -> None:
        """Add energy flow result to the appropriate history."""
        for label in energy_flow.keys():
            for category in energy_flow[label]:
                cls.ENERGY_FLOWS[label][category].append(energy_flow[label][category])

    @classmethod
    def export_energy_flow_results(cls, path: str = os.path.dirname(__file__), file_name: str = "energy_flows") -> None:
        """
        Export energy flow results to an Excel file, with each label in a separate sheet.

        Args:
            filename (str): Name of the output Excel file.
        """
        with pd.ExcelWriter(path + f'/{file_name}.xlsx', engine='openpyxl') as writer:
            for label, data_dict in cls.ENERGY_FLOWS.items():
                # Convert the dictionary of lists to a DataFrame
                df = pd.DataFrame(data_dict)
                # Convert label to a string and truncate to 31 characters (Excel limit)
                sheet_name = str(label)[:31]

                # Write the DataFrame to a sheet named after the label
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    @classmethod
    def export_summary_results(cls, path: str = os.path.dirname(__file__), file_name: str = 'summary') -> None:
        DC_CURTAILMENT = cls.DC_CURTAILMENT_A | cls.DC_CURTAILMENT_B | cls.DC_CURTAILMENT_C
        AC_CURTAILMENT = cls.AC_CURTAILMENT_A | cls.AC_CURTAILMENT_B | cls.AC_CURTAILMENT_C
        summary = {'PV dc-generation (kWh)': sum([sum(cls.PV_DC_GENERATION[key]) for key in cls.PV_DC_GENERATION.keys()]) * cls.STEP_SIZE / 60,
                   'Battery stored energy (kWh)': sum([cls.BATTERY_STORED_ENERGY[key][-1] for key in cls.BATTERY_STORED_ENERGY.keys()]),
                   'EV stored energy (kWh)': sum([cls.EV_STORED_ENERGY[key][-1] for key in cls.EV_STORED_ENERGY.keys()]),
                   'Potential inverter ac output (kWh)': sum([sum(cls.PV_INVERTER_POTENTIAL_OUTPUT[key]) for key in cls.PV_INVERTER_POTENTIAL_OUTPUT.keys()]) * cls.STEP_SIZE / 60,
                   'Actual inverter ac output (kWh)': sum([sum(cls.ENERGY_FLOWS[key].get('Inverter Power (kW)', [])) for key in cls.ENERGY_FLOWS.keys()]) * cls.STEP_SIZE / 60,
                   'Total pv to battery (kWh)': sum([sum(cls.ENERGY_FLOWS[key].get('Inverter to Battery (kW)', [])) for key in cls.ENERGY_FLOWS.keys()]) * cls.STEP_SIZE / 60,
                   'Total inverter to load (kWh)': sum([sum(cls.ENERGY_FLOWS[key].get('Inverter to Load (kW)', [])) for key in cls.ENERGY_FLOWS.keys()]) * cls.STEP_SIZE / 60,
                   'Total inverter to ev (kWh)': sum([sum(cls.ENERGY_FLOWS[key].get('Inverter to EV (kW)', [])) for key in cls.ENERGY_FLOWS.keys()]) * cls.STEP_SIZE / 60,
                   'Total inverter to grid (kWh)': sum([sum(cls.ENERGY_FLOWS[key].get('Inverter to Grid (kW)', [])) for key in cls.ENERGY_FLOWS.keys()]) * cls.STEP_SIZE / 60,
                   'Total ev to load (kWh)': sum([sum(cls.ENERGY_FLOWS[key].get('EV to Load (kW)', [])) for key in cls.ENERGY_FLOWS.keys()]) * cls.STEP_SIZE / 60,
                   'Total ev to grid (kWh)': sum([sum(cls.ENERGY_FLOWS[key].get('EV to Grid (kW)', [])) for key in cls.ENERGY_FLOWS.keys()]) * cls.STEP_SIZE / 60,
                   'Total grid to load (kWh)': sum([sum(cls.ENERGY_FLOWS[key].get('Grid to Load (kW)', [])) for key in cls.ENERGY_FLOWS.keys()]) * cls.STEP_SIZE / 60,
                   'Total grid to ev (kWh)': sum([sum(cls.ENERGY_FLOWS[key].get('Grid to EV (kW)', [])) for key in cls.ENERGY_FLOWS.keys()]) * cls.STEP_SIZE / 60,
                   'Total dc curtailment (kWh)': sum([sum(DC_CURTAILMENT[key]) for key in DC_CURTAILMENT.keys()]) * cls.STEP_SIZE / 60,
                   'Total ac curtailment (kWh)': sum([sum(AC_CURTAILMENT[key]) for key in AC_CURTAILMENT.keys()]) * cls.STEP_SIZE / 60,
                   'Total curtailment (kWh)': 0,
                   'Total dc curtailment (%)': 0,
                   'Total ac curtailment (%)': 0,
                   'Total curtailment (%)': 0,
                   'Fairness Index (%)': cls.system_fairness_index() * 100,
                   'Active System Losses (kWh)': sum(cls.TOTAL_LOSSES['Active']) * cls.STEP_SIZE / 60,
                   'Reactive System Losses (kVArh)': sum(cls.TOTAL_LOSSES['Reactive']) * cls.STEP_SIZE / 60,
                   'Simulation Time (Sec)': sum(cls.SIMULATION_TIME) / len(cls.SIMULATION_TIME)}
        summary['Total curtailment (kWh)'] = summary['Total ac curtailment (kWh)'] + summary['Total dc curtailment (kWh)']
        summary['Total dc curtailment (%)'] = 100 * summary['Total dc curtailment (kWh)'] / summary['PV dc-generation (kWh)']
        summary['Total ac curtailment (%)'] = 100 * summary['Total ac curtailment (kWh)'] / summary['Potential inverter ac output (kWh)']
        summary['Total curtailment (%)'] = 100 * summary['Total curtailment (kWh)'] / summary['PV dc-generation (kWh)']
        with open(path + f'/{file_name}.csv', mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(summary.keys())  # Write the header row
            writer.writerow(summary.values())

    @classmethod
    def system_fairness_index(cls):
        ratios = []
        for key, potential in cls.PV_INVERTER_POTENTIAL_OUTPUT.items():
            idx = int(key.split('_')[1])
            flows = cls.ENERGY_FLOWS[idx].get("Inverter Power (kW)", [])
            total = sum(flows)
            ratio = total / sum(potential) if sum(potential) != 0 else np.nan
            ratios.append(ratio)
        return 1 - np.std(ratios) / 0.5

    @classmethod
    def _update_pv_reactive_power_results(cls, reactive_power: dict) -> None:
        """Add dc generation result to the appropriate history."""
        for pv in cls.PV_INVERTER_REACTIVE_POWER.keys():
            cls.PV_INVERTER_REACTIVE_POWER[pv].append(reactive_power[pv])

    @classmethod
    def _update_pv_active_power_results(cls, active_power: dict) -> None:
        """Add dc generation result to the appropriate history."""
        for pv in cls.PV_INVERTER_ACTIVE_POWER.keys():
            cls.PV_INVERTER_ACTIVE_POWER[pv].append(active_power[pv])

    @classmethod
    def _update_ev_reactive_power_results(cls, reactive_power: dict) -> None:
        """Add dc generation result to the appropriate history."""
        for ev in cls.EV_INVERTER_REACTIVE_POWER.keys():
            cls.EV_INVERTER_REACTIVE_POWER[ev].append(reactive_power[ev])

    @classmethod
    def _update_ev_active_power_results(cls, active_power: dict) -> None:
        """Add dc generation result to the appropriate history."""
        for ev in cls.EV_INVERTER_ACTIVE_POWER.keys():
            cls.EV_INVERTER_ACTIVE_POWER[ev].append(active_power[ev])

    @classmethod
    def export_reactive_power_results(cls, path: str = os.path.dirname(__file__), file_name: str = "reactive_power") -> None:
        """
        Export energy flow results to an Excel file, with each label in a separate sheet.

        Args:
            filename (str): Name of the output Excel file.
        """
        data = cls.PV_INVERTER_REACTIVE_POWER | cls.EV_INVERTER_REACTIVE_POWER

        with open(path + f"/{file_name}.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data.keys())
            for row in zip(*data.values()):
                writer.writerow(row)

    @classmethod
    def export_metrics(cls, path: str = os.path.dirname(__file__), file_name: str = "metrics") -> None:
        """
        Export energy flow results to an Excel file, with each label in a separate sheet.

        Args:
            filename (str): Name of the output Excel file.
        """
        # cls._update_metrics()
        data = cls.METRICS
        cls._update_metrics()
        print(data)
        header = list(data.keys())
        rows = list(zip(*data.values()))

        with open(path + f"/{file_name}.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(rows)

    @classmethod
    def _update_metrics(cls):
        Steps_No = 24 / (cls.STEP_SIZE / 60)
        DC_CURTAILMENT = cls.DC_CURTAILMENT_A | cls.DC_CURTAILMENT_B | cls.DC_CURTAILMENT_C
        AC_CURTAILMENT = cls.AC_CURTAILMENT_A | cls.AC_CURTAILMENT_B | cls.AC_CURTAILMENT_C
        VOLTAGES = cls.VOLTAGE_HISTORY_A | cls.VOLTAGE_HISTORY_B | cls.VOLTAGE_HISTORY_C
        Nodes_No = len(list(VOLTAGES.keys()))
        CURRENTS = cls.LINE_CURRENT_A | cls.LINE_CURRENT_B | cls.LINE_CURRENT_C
        Lines_No = len(list(CURRENTS.keys()))
        Buses_No = len(list(cls.VOLTAGE_UNBALANCE_HISTORY.keys()))
        try:
            cls.METRICS['Metric 1.a'] = [
                100 * sum([sum(DC_CURTAILMENT[key]) for key in DC_CURTAILMENT.keys()]) / sum([sum(cls.PV_DC_GENERATION[key]) for key in cls.PV_DC_GENERATION.keys()])]
            cls.METRICS['Metric 1.b'] = [100 * sum([sum(AC_CURTAILMENT[key]) for key in AC_CURTAILMENT.keys()]) / sum(
                [sum(cls.PV_INVERTER_POTENTIAL_OUTPUT[key]) for key in cls.PV_INVERTER_POTENTIAL_OUTPUT.keys()])]
        except:
            cls.METRICS['Metric 1.a'] = [0]
            cls.METRICS['Metric 1.b'] = [0]
        cls.METRICS['Metric 2'] = [100 * sum(sum(1 for v in VOLTAGES[key] if v > 1.1 or v < 0.9) for key in VOLTAGES.keys()) / (Steps_No * Nodes_No)]
        cls.METRICS['Metric 3'] = [100 * sum(sum(1 for i in CURRENTS[key] if i > 100) for key in CURRENTS.keys()) / (Steps_No * Lines_No)]
        cls.METRICS['Metric 4'] = [
            100 * sum(sum(1 for vuf in cls.VOLTAGE_UNBALANCE_HISTORY[key] if vuf > 2) for key in cls.VOLTAGE_UNBALANCE_HISTORY.keys()) / (Steps_No * Buses_No)]
        cls.METRICS['Metric 5.a'] = [100 * sum(cls.TOTAL_LOSSES['Active']) / sum(np.abs(np.array(cls.TOTAL_POWER['Active'])))]
        cls.METRICS['Metric 5.b'] = [100 * sum(cls.TOTAL_LOSSES['Reactive']) / sum(np.abs(np.array(cls.TOTAL_POWER['Reactive'])))]

    @classmethod
    def export_voltages(cls, path: str = os.path.dirname(__file__), file_name: str = "voltages") -> None:
        """Export voltage histories for all phases and buses to CSV"""
        combined_voltages = cls.VOLTAGE_HISTORY_A | cls.VOLTAGE_HISTORY_B | cls.VOLTAGE_HISTORY_C
        df = pd.DataFrame(combined_voltages)
        df.insert(0, "Time", cls.TIME_SERIES)
        df.to_csv(os.path.join(path, f"{file_name}.csv"), index=False)

    @classmethod
    def export_line_currents(cls, path: str = os.path.dirname(__file__), file_name: str = "line_currents") -> None:
        """Export line current histories for all phases to CSV"""
        combined_currents = cls.LINE_CURRENT_A | cls.LINE_CURRENT_B | cls.LINE_CURRENT_C
        df = pd.DataFrame(combined_currents)
        df.insert(0, "Time", cls.TIME_SERIES)
        df.to_csv(os.path.join(path, f"{file_name}.csv"), index=False)

    @classmethod
    def export_voltage_unbalance(cls, path: str = os.path.dirname(__file__), file_name: str = "voltage_unbalance") -> None:
        """Export voltage unbalance history to CSV"""
        df = pd.DataFrame(cls.VOLTAGE_UNBALANCE_HISTORY)
        df.insert(0, "Time", cls.TIME_SERIES)
        df.to_csv(os.path.join(path, f"{file_name}.csv"), index=False)

    @classmethod
    def export_ac_curtailment(cls, path: str = os.path.dirname(__file__), file_name: str = "ac_curtailment") -> None:
        """Export line current histories for all phases to CSV"""
        ac_curtailment_a = {k + '.1': v for k, v in cls.AC_CURTAILMENT_A.items()}
        ac_curtailment_b = {k + '.2': v for k, v in cls.AC_CURTAILMENT_B.items()}
        ac_curtailment_c = {k + '.3': v for k, v in cls.AC_CURTAILMENT_C.items()}
        combined_curtailment = ac_curtailment_a | ac_curtailment_b | ac_curtailment_c
        df = pd.DataFrame(combined_curtailment)
        df.insert(0, "Time", cls.TIME_SERIES)
        df.to_csv(os.path.join(path, f"{file_name}.csv"), index=False)

    @classmethod
    def export_dc_curtailment(cls, path: str = os.path.dirname(__file__), file_name: str = "dc_curtailment") -> None:
        """Export line current histories for all phases to CSV"""
        dc_curtailment_a = {k + '.1': v for k, v in cls.DC_CURTAILMENT_A.items()}
        dc_curtailment_b = {k + '.2': v for k, v in cls.DC_CURTAILMENT_B.items()}
        dc_curtailment_c = {k + '.3': v for k, v in cls.DC_CURTAILMENT_C.items()}
        combined_curtailment = dc_curtailment_a | dc_curtailment_b | dc_curtailment_c
        df = pd.DataFrame(combined_curtailment)
        df.insert(0, "Time", cls.TIME_SERIES)
        df.to_csv(os.path.join(path, f"{file_name}.csv"), index=False)

    @classmethod
    def update_total_powers(cls, active_power, reactive_power, active_losses, reactive_losses):
        cls.TOTAL_POWER['Active'].append(active_power)
        cls.TOTAL_POWER['Reactive'].append(reactive_power)
        cls.TOTAL_LOSSES['Active'].append(active_losses)
        cls.TOTAL_LOSSES['Reactive'].append(reactive_losses)
