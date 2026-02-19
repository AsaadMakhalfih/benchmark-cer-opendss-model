import numpy as np
import pandas as pd
import cmath
from math import sqrt, pi
from src.opendss_com import dss_object
import os
import csv
from src.models.load import Load
from src.models.pv_system import PVSystem, HybridPVSystem
from src.models.ev import EVSystem
from src.utils import remove_sublist


#  The dataframe columns header should be lower-cased with underscore name convention

class CircuitInterface:
    def __init__(self, opendss_model_path: str = None, label_bus_dict: dict[int: str] = None, models_circuit_labels: dict[str: [int]] = None) -> None:
        self._opendss_model_path = opendss_model_path
        self._dss_object = dss_object()
        self._label_bus_dict = label_bus_dict
        self._models_circuit_labels = models_circuit_labels
        self._evs_circuit_labels = None
        self._hybridpvsystems_circuit_labels = None
        self._pvsystems_circuit_labels = None
        self._loads_circuit_labels = None
        self._buses = None
        self._end_buses = None
        self._lines = None
        self._transformers = None
        self._y_matrix = None
        self._metrics = None

        if self._opendss_model_path is not None:
            self.compile()

        if self._models_circuit_labels is not None:
            for key, value in self._models_circuit_labels.items():
                if key.lower() == 'load':
                    self._loads_circuit_labels = value
                elif key.lower() == 'pvsystem':
                    self._pvsystems_circuit_labels = value
                elif key.lower() == 'hybridpvsystem':
                    self._hybridpvsystems_circuit_labels = value
                elif key.lower() == 'evsystem':
                    self._evs_circuit_labels = value
                else:
                    raise ValueError(f"Invalid input for {key}. Expected a dictionary of type {{str: [int]}}.")

        self.initialise_cers()
        self.initialise_end_buses()
        self.initialise_lines()
        self.initialise_circuit_metrics()
        self.initialise_all_buses()
        self.initialise_transformer()

    @property
    def pvsystems_circuit_labels(self):
        return self._pvsystems_circuit_labels

    @property
    def hybridpvsystems_circuit_labels(self):
        return self._hybridpvsystems_circuit_labels

    def compile(self):
        self._dss_object.Text.Command = 'clear'
        self._dss_object.Text.Command = 'Compile ' + self._opendss_model_path
        self._dss_object.Text.Command = 'Reset'

    def initialise_circuit_metrics(self):
        metrics = [{
            'active_power': 0.0,
            'reactive_power': 0.0,
            'active_losses': 0.0,
            'reactive_losses': 0.0,
        }]
        self._metrics = pd.DataFrame(metrics)

    def initialise_cers(self):
        if self._loads_circuit_labels is not None:
            for label in self._loads_circuit_labels:
                self._dss_object.Text.Command = f'New Load.Load_{label} phases=1 bus1={self._label_bus_dict[label]} kV=0.23 kW=0 PF=1.0 vminpu=0.6 vmaxpu=2'
        if self._pvsystems_circuit_labels is not None:
            for label in self._pvsystems_circuit_labels:
                self._dss_object.Text.Command = f'New Load.PV_{label} phases=1 bus1={self._label_bus_dict[label]} kV=0.23 kW=0 kvar=0 vminpu=0.6 vmaxpu=2'
        if self._hybridpvsystems_circuit_labels is not None:
            for label in self._hybridpvsystems_circuit_labels:
                self._dss_object.Text.Command = f'New Load.HybridPV_{label} phases=1 bus1={self._label_bus_dict[label]} kV=0.23 kW=0 kvar=0 vminpu=0.6 vmaxpu=2'
        if self._evs_circuit_labels is not None:
            for label in self._evs_circuit_labels:
                self._dss_object.Text.Command = f'New Load.EV_{label} phases=1 bus1={self._label_bus_dict[label]} kV=0.23 kW=0 kvar=0 vminpu=0.6 vmaxpu=2'

    def initialise_all_buses(self):
        buses = []
        dss_circuit = self._dss_object.ActiveCircuit
        buses_names = dss_circuit.AllBusNames
        for bus in buses_names:
            for phase in ['1', '2', '3']:
                if phase == '1':
                    angle = 0.0
                elif phase == '2':
                    angle = - 2 * pi / 3
                else:
                    angle = 2 * pi / 3
                dss_circuit.SetActiveBus(bus)
                buses.append({
                    'bus_i': bus,
                    'phase_i': phase,
                    'v_base_ln': 1000 * dss_circuit.ActiveBus.kVBase,
                    'v_pu': 1.0,
                    'angle': angle
                })
        self._buses = pd.DataFrame(buses)

    def initialise_end_buses(self):
        end_buses_names = list(self._label_bus_dict.values())
        buses = []
        dss_circuit = self._dss_object.ActiveCircuit
        for bus in end_buses_names:
            node = bus.split('.')[1]
            main_bus = bus.split('.')[0]
            dss_circuit.SetActiveBus(main_bus)
            buses.append({
                'name': bus,
                'kv_base_ll': dss_circuit.ActiveBus.kVBase,
                'phase': node,
                'distance': dss_circuit.ActiveBus.Distance * 1000,
                'x': dss_circuit.ActiveBus.x,
                'y': dss_circuit.ActiveBus.y,
                'v_pu': 1.0,
                'angle': 0.0
            })
        self._end_buses = pd.DataFrame(buses)
        self._end_buses.set_index('name', inplace=True)

    def initialise_transformer(self):
        dss_circuit = self._dss_object.ActiveCircuit
        transformers_names = dss_circuit.Transformers.AllNames
        transformers = []
        for name in transformers_names:
            dss_circuit.Transformers.Name = name
            transformers.append({
                'name': name,
                'capacity': dss_circuit.Transformers.kva
            })
        self._transformers = pd.DataFrame(transformers)

    def initialise_lines(self):
        dss_circuit = self._dss_object.ActiveCircuit
        lines_names = list(dss_circuit.Lines.AllNames)
        lines = []
        for line in lines_names:
            dss_circuit.Lines.Name = line
            bus1 = dss_circuit.Lines.Bus1  # .split('.')[0]
            bus2 = dss_circuit.Lines.Bus2  # .split('.')[0]
            line_code = dss_circuit.Lines.LineCode
            dss_circuit.LineCodes.Name = line_code
            ampacity = dss_circuit.LineCodes.EmergAmps
            length = dss_circuit.Lines.Length
            dss_circuit.SetActiveBus(bus2)
            distance = dss_circuit.ActiveBus.Distance * 1000
            lines.append({
                'name': line,
                'bus1': bus1,
                'bus2': bus2,
                'length': length,
                'ampacity': ampacity,
                'distance': distance,
                'line_code': line_code,
                'i_a': 0.0,
                'i_b': 0.0,
                'i_c': 0.0,
                's_a': 0.0+0.0j,
                's_b': 0.0+0.0j,
                's_c': 0.0+0.0j,
                'losses_active': 0.0,
                'losses_reactive': 0.0
            })
        self._lines = pd.DataFrame(lines)
        self._lines.set_index('name', inplace=True)

    def update_cer_output_powers(self, cer_powers_dict: {object: [float, float]} = None):
        for cer_obj, [kw, kvar] in cer_powers_dict.items():
            if type(cer_obj) is Load:
                self._dss_object.Text.Command = f'Load.Load_{cer_obj.circuit_label}.kw={kw}'
                self._dss_object.Text.Command = f'Load.Load_{cer_obj.circuit_label}.kvar={kvar}'

            elif type(cer_obj) is PVSystem:
                self._dss_object.Text.Command = f'Load.PV_{cer_obj.circuit_label}.kw={-kw}'
                self._dss_object.Text.Command = f'Load.PV_{cer_obj.circuit_label}.kvar={-kvar}'

            elif type(cer_obj) is HybridPVSystem:
                self._dss_object.Text.Command = f'Load.HybridPV_{cer_obj.circuit_label}.kw={-kw}'
                self._dss_object.Text.Command = f'Load.HybridPV_{cer_obj.circuit_label}.kvar={-kvar}'

            elif type(cer_obj) is EVSystem:
                self._dss_object.Text.Command = f'Load.EV_{cer_obj.circuit_label}.kw={kw}'
                self._dss_object.Text.Command = f'Load.EV_{cer_obj.circuit_label}.kvar={kvar}'  # Check the kvar sign for the ev.

    def solve_power_flow(self) -> None:
        self._dss_object.Text.Command = 'solve'

    def solve_power_flow_at_hour(self, hour) -> None:
        self._dss_object.ActiveCircuit.Solution.dblHour = hour
        self._dss_object.Text.Command = 'Set number=1'
        self._dss_object.Text.Command = 'solve'
        self._dss_object.ActiveCircuit.Solution.Cleanup()

    def update_sys_voltage(self) -> pd.DataFrame:
        buses_names = self._end_buses.index
        dss_circuit = self._dss_object.ActiveCircuit
        for bus in buses_names:
            node = int(bus.split('.')[1])
            main_bus = bus.split('.')[0]
            dss_circuit.SetActiveBus(main_bus)

            self._end_buses.at[bus, 'v_pu'] = dss_circuit.ActiveBus.puVmagAngle[2 * (node - 1)]
            self._end_buses.at[bus, 'angle'] = dss_circuit.ActiveBus.puVmagAngle[2 * node - 1]

        buses_names = self._buses['bus_i'].values
        dss_circuit = self._dss_object.ActiveCircuit
        self._buses.set_index(['bus_i', 'phase_i'], inplace=True)
        for bus in buses_names:
            for phase in ['1', '2', '3']:
                dss_circuit.SetActiveBus(bus)
                self._buses.at[(bus, phase), 'v_pu'] = dss_circuit.ActiveBus.puVmagAngle[2 * (int(phase) - 1)]
                self._buses.at[(bus, phase), 'angle'] = dss_circuit.ActiveBus.puVmagAngle[2 * int(phase) - 1]
        self._buses = self._buses.reset_index()
        return self._end_buses

    def get_cer_voltage(self, cers: [object] = None) -> dict:
        cers_voltages = {cer: 0 for cer in cers}
        for cer in cers:
            cer_bus = self._label_bus_dict[cer.circuit_label]
            cers_voltages[cer] = self._end_buses.loc[cer_bus, 'v_pu']
        return cers_voltages

    def update_line_flow(self) -> pd.DataFrame:
        lines_names = self._lines.index
        dss_circuit = self._dss_object.ActiveCircuit
        for line in lines_names:
            dss_circuit.SetActiveElement(f"Line.{line}")
            self._lines.at[line, 'i_a'] = dss_circuit.ActiveCktElement.CurrentsMagAng[0]
            self._lines.at[line, 'i_b'] = dss_circuit.ActiveCktElement.CurrentsMagAng[2]
            self._lines.at[line, 'i_c'] = dss_circuit.ActiveCktElement.CurrentsMagAng[4]
            self._lines.at[line, 's_a'] = dss_circuit.ActiveCktElement.Powers[0] + 1j * dss_circuit.ActiveCktElement.Powers[1]
            self._lines.at[line, 's_b'] = dss_circuit.ActiveCktElement.Powers[2] + 1j * dss_circuit.ActiveCktElement.Powers[3]
            self._lines.at[line, 's_c'] = dss_circuit.ActiveCktElement.Powers[4] + 1j * dss_circuit.ActiveCktElement.Powers[5]
            self._lines.at[line, 'losses_active'] = dss_circuit.ActiveCktElement.Losses[0] / 1000
            self._lines.at[line, 'losses_reactive'] = dss_circuit.ActiveCktElement.Losses[1] / 1000
        return self._lines

    def update_circuit_metrics(self) -> pd.DataFrame:
        dss_circuit = self._dss_object.ActiveCircuit
        metrics = [{
            'active_power': dss_circuit.TotalPower[0],
            'reactive_power': dss_circuit.TotalPower[1],
            'active_losses': dss_circuit.Losses[0] / 1000,
            'reactive_losses': dss_circuit.Losses[1] / 1000,
        }]
        self._metrics = pd.DataFrame(metrics)
        return self._metrics

    def get_buses_results(self):
        return self._end_buses, self._buses

    def get_lines_results(self):
        return self._lines

    @property
    def init_volt_matrix(self):
        return self._buses

    @property
    def y_matrix_raw(self) -> np.ndarray:
        return self._y_matrix

    @property
    def metrics(self):
        return self._metrics

    @property
    def buses_set_raw(self) -> np.ndarray:
        return np.array(self._dss_object.ActiveCircuit.AllBusNames)

    @property
    def nodes_set_raw(self) -> np.ndarray:
        return np.array(self._dss_object.ActiveCircuit.AllNodeNames)

    @property
    def phases_set_raw(self) -> np.ndarray:
        return np.array(['1', '2', '3'])

    @property
    def lines_set_raw(self) -> np.ndarray:
        return np.array(self._dss_object.ActiveCircuit.Lines.AllNames)

    @property
    def transformers(self):
        return self._transformers

    @property
    def loads_set_raw(self) -> np.ndarray:
        names_of_all_loads = self._dss_object.ActiveCircuit.Loads.AllNames
        loads_set = []
        for element in names_of_all_loads:
            if 'load_' in element.lower():
                self._dss_object.ActiveCircuit.Loads.Name = element
                loads_set.append(element)
        return np.array(loads_set)

    @property
    def lines_matrix_raw(self) -> pd.DataFrame:
        lines_matrix = []
        lines_names = self._dss_object.ActiveCircuit.Lines.AllNames
        for line in lines_names:
            lines_matrix.append({
                'line': line,
                'sending_buses': self._lines.loc[line, 'bus1'],
                'receiving_buses': self._lines.loc[line, 'bus2'],
                'line_code': self._lines.loc[line, 'line_code'],
                'ampacity': self._lines.loc[line, 'ampacity']
            })
        return pd.DataFrame(lines_matrix)

    @property
    def loads_matrix_raw(self) -> pd.DataFrame:
        names_of_all_loads = self._dss_object.ActiveCircuit.Loads.AllNames
        loads_matrix = []
        for element in names_of_all_loads:
            if 'load_' in element.lower():
                self._dss_object.ActiveCircuit.Loads.Name = element
                loads_matrix.append({
                    'load': element,
                    'load_buses': self._dss_object.ActiveCircuit.ActiveCktElement.BusNames[0].split('.')[0],
                    'load_phases': self._dss_object.ActiveCircuit.ActiveCktElement.BusNames[0].split('.')[1],
                    'load_v_nom': float(self._dss_object.ActiveCircuit.Loads.kV) * 1000
                })
        return pd.DataFrame(loads_matrix)

    @property
    def pv_set_raw(self) -> np.ndarray:
        names_of_all_loads = self._dss_object.ActiveCircuit.Loads.AllNames
        pv_set = []
        for element in names_of_all_loads:
            if 'pv_' in element.lower():
                self._dss_object.ActiveCircuit.Loads.Name = element
                pv_set.append(element)
        return np.array(pv_set)

    @property
    def pvs_matrix_raw(self) -> pd.DataFrame:
        names_of_all_loads = self._dss_object.ActiveCircuit.Loads.AllNames
        pvs_matrix = []
        for element in names_of_all_loads:
            if 'pv_' in element.lower():
                self._dss_object.ActiveCircuit.Loads.Name = element
                pvs_matrix.append({
                    'pv': element,
                    'pv_buses': self._dss_object.ActiveCircuit.ActiveCktElement.BusNames[0].split('.')[0],
                    'pv_phases': self._dss_object.ActiveCircuit.ActiveCktElement.BusNames[0].split('.')[1],
                    'pv_v_nom': float(self._dss_object.ActiveCircuit.Loads.kV) * 1000,
                })
        return pd.DataFrame(pvs_matrix)

    @property
    def loads_circuit_labels_dict(self) -> dict:
        loads_labels = {}
        bus_label_dict = {v: k for k, v in self._label_bus_dict.items()}
        for ld in self.loads_set_raw:
            self._dss_object.ActiveCircuit.Loads.Name = ld
            bus = self._dss_object.ActiveCircuit.ActiveCktElement.BusNames[0]
            label = bus_label_dict[bus]
            loads_labels[ld] = label
        return loads_labels

    @property
    def end_buses(self) -> list:
        """
        :return: the sorted end buses according to distance
        """
        sorted_df = self._end_buses.sort_values(by='distance').copy()
        buses = list(sorted_df.reset_index()['name'].values)
        return buses

    @property
    def lines_rating(self) -> dict:
        """
        :return: the lines ratings dictionary {line: ampacity}
        """
        sorted_df = self._lines.sort_values(by='distance').copy()
        sorted_df = sorted_df.reset_index()
        lines_ratings = dict(zip(sorted_df['name'].values, sorted_df['ampacity'].values))
        return lines_ratings

    @property
    def pv_set(self) -> dict:
        """
        :return: the names of the pv systems ordered in accordance with their distance from the source. {pv_name: bus}
        """
        buses = self.end_buses
        names_of_all_loads = self._dss_object.ActiveCircuit.Loads.AllNames
        pv_set = {}
        for element in names_of_all_loads:
            if 'pv_' in element.lower():
                self._dss_object.ActiveCircuit.Loads.Name = element
                pv_set[element] = self._dss_object.ActiveCircuit.ActiveCktElement.BusNames[0]

        # Sort the PV systems based on the order of their buses in the `buses` list
        sorted_pv_set = {k: v for k, v in sorted(pv_set.items(), key=lambda item: buses.index(item[1]) if item[1] in buses else len(buses))}
        return sorted_pv_set

    @property
    def ev_set(self) -> dict:
        """
        :return: the names of the pv systems ordered in accordance with their distance from the source. {pv_name: bus}
        """
        buses = self.end_buses
        names_of_all_loads = self._dss_object.ActiveCircuit.Loads.AllNames
        ev_set = {}
        for element in names_of_all_loads:
            if 'ev_' in element.lower():
                self._dss_object.ActiveCircuit.Loads.Name = element
                ev_set[element] = self._dss_object.ActiveCircuit.ActiveCktElement.BusNames[0]

        # Sort the EV systems based on the order of their buses in the `buses` list
        sorted_ev_set = {k: v for k, v in sorted(ev_set.items(), key=lambda item: buses.index(item[1]) if item[1] in buses else len(buses))}
        return sorted_ev_set

    @property
    def models_circuit_labels(self):
        return self._models_circuit_labels

    @property
    def loads_only_circuit_labels(self):
        labels = []
        if self._pvsystems_circuit_labels is not None and self._hybridpvsystems_circuit_labels is not None and self._evs_circuit_labels is not None:
            labels = remove_sublist(remove_sublist(remove_sublist(self._loads_circuit_labels, self._pvsystems_circuit_labels),
                                                   self._hybridpvsystems_circuit_labels), self._evs_circuit_labels)
        elif self._pvsystems_circuit_labels is not None and self._hybridpvsystems_circuit_labels is not None:
            labels = remove_sublist(remove_sublist(self._loads_circuit_labels, self._pvsystems_circuit_labels),
                                    self._hybridpvsystems_circuit_labels)
        elif self._pvsystems_circuit_labels is not None:
            labels = remove_sublist(self._loads_circuit_labels, self._pvsystems_circuit_labels)

        return labels


if __name__ == '__main__':
    with open(os.path.dirname(os.path.dirname(__file__)) + f"/Data/Network_Model/label_bus_dict.csv", 'r') as csvfile:
        reader = csv.reader(csvfile)
        label_bus_dict = {int(row[0]): row[1] for row in reader}

    loads_circuit_labels = list(range(1, 166))
    opendss_path = os.path.dirname(os.path.dirname(__file__)) + f"/Data/Network_Model/model.dss"
    circuit = CircuitInterface(opendss_path, label_bus_dict, {'load': loads_circuit_labels})
    circuit.initialise_end_buses()
    circuit.initialise_lines()
    circuit.update_line_flow()
    circuit.solve_power_flow()
    print(circuit.update_sys_voltage())
