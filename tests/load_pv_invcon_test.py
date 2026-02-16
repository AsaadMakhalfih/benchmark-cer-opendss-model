import numpy as np

from src.external_input_data import ModelInputData, import_txt_file_as_numpy
from src.models.load import Load
from src.models.pv_panel import PVPanels
from src.models.pv_system import PVSystem
from src.models.inverter import Inverter, InverterSettings, VoltWatt, VoltVar
from src.models.meter import Meter
from src.results import Results
from src.circuit_interface import CircuitInterface
from src.tests import run_comprehensive_comparison
from src.compiler import Compiler
from datetime import time
import os
import csv
import warnings
warnings.filterwarnings("ignore")

day = 'Summer_Weekday'
# First, create the input data for the model using ModelInputData
load_data_path = os.path.dirname(os.path.dirname(__file__)) + "/Data/Load_Data"
irrad_data_path = os.path.dirname(os.path.dirname(__file__)) + "/Data/PV_Data"
temp_data_path = os.path.dirname(os.path.dirname(__file__)) + "/Data/PV_Data"
ev_behaviour_data_path = os.path.dirname(os.path.dirname(__file__)) + "/Data/EV_Data"
circuit_labels = list(range(1, 166))
demand_power = {circuit_label: None for circuit_label in circuit_labels}
for label in circuit_labels:
    demand_power[label] = import_txt_file_as_numpy(load_data_path + f'/{day}/Load{label}.txt')
irradiance = import_txt_file_as_numpy(irrad_data_path + f'/{day}/Solar.txt')
temperature = import_txt_file_as_numpy(temp_data_path + f'/{day}/Temp.txt')
step_size = 30
time_range = [0, 23.5]
model_data = ModelInputData(demand_power, irradiance, temperature, step_size, time_range, None)
# Second, create the CER models and assign the relevant circuit labels using models
loads_circuit_labels = circuit_labels
pv_systems_circuit_labels = circuit_labels
loads = {label: Load(label) for label in loads_circuit_labels}
pv_panels = {label: PVPanels(label) for label in pv_systems_circuit_labels}
inverter_settings = InverterSettings()
inverter_settings.enable_volt_watt(VoltWatt())
inverter_settings.enable_volt_var(VoltVar())
inverters = {label: Inverter(circuit_label=label, inverter_settings=inverter_settings) for label in pv_systems_circuit_labels}
meters = {label: Meter(label, loads=[loads[label]], inverters=[inverters[label]]) for label in pv_systems_circuit_labels}
pv_systems = [PVSystem(label, pv_panels[label], inverters[label], meters[label]) for label in pv_systems_circuit_labels]
cers = list(loads.values()) + pv_systems
# Third, create the opendss circuit interface using CircuitInterface
with open(os.path.dirname(os.path.dirname(__file__)) + f"/Data/Network_Model/label_bus_dict.csv", 'r') as csvfile:
    reader = csv.reader(csvfile)
    label_bus_dict = {int(row[0]): row[1] for row in reader}
opendss_path = os.path.dirname(os.path.dirname(__file__)) + f"/Data/Network_Model/model.dss"
circuit = CircuitInterface(opendss_path, label_bus_dict, {'load': loads_circuit_labels, 'pvsystem': pv_systems_circuit_labels})
# Fourth, initialise the Results class with appropriate info from the CircuitInterface instance
time_settings = [time(0, 0), time(23, 30), 30]
end_buses = circuit.end_buses
lines_ratings = circuit.lines_rating
pv_set = circuit.pv_set

Results.initialise(time_settings, end_buses, lines_ratings, pv_set, meters)
# Fourth, solve the circuit using Compiler
solver = Compiler(circuit, cers, model_data)
delta_p_q_settings = (0.15, 0.05, 0.1, 0.05, 0.15, 0.05, 0.1, 0.05)
solver.change_delta_p_q_settings(settings=delta_p_q_settings)
for step in range(0, 48):
    solver.cer_convergence_process(step)
    print('time:', step / 2.0)

model_voltages_a = Results.VOLTAGE_HISTORY_A
model_voltages_b = Results.VOLTAGE_HISTORY_B
model_voltages_c = Results.VOLTAGE_HISTORY_C
model_voltages = model_voltages_a | model_voltages_b | model_voltages_c
model_currents_a = Results.LINE_CURRENT_A
model_currents_b = Results.LINE_CURRENT_B
model_currents_c = Results.LINE_CURRENT_C

model_pv_active_power = Results.PV_INVERTER_ACTIVE_POWER
model_pv_reactive_power = Results.PV_INVERTER_REACTIVE_POWER
# Run the opendss model
# First, create the opendss circuit interface using CircuitInterface
with open(os.path.dirname(os.path.dirname(__file__)) + f"/Data/Network_Model/label_bus_dict.csv", 'r') as csvfile:
    reader = csv.reader(csvfile)
    label_bus_dict = {int(row[0]): row[1] for row in reader}
opendss_path = os.path.dirname(os.path.dirname(__file__)) + f"/opendss_models_for_tests/load_pv_invcon/Main.dss"
circuit = CircuitInterface(opendss_path, label_bus_dict)
# Fourth, initialise the Results class with appropriate info from the CircuitInterface instance
time_settings = [time(0, 0), time(23, 30), 30]
end_buses = circuit.end_buses
lines_ratings = circuit.lines_rating
Results.initialise(time_settings, end_buses, lines_ratings, pv_set, meters)

active_power = {key: 0.0 for key in pv_set}
reactive_power = {key: 0.0 for key in pv_set}
for hour in range(48):
    circuit.solve_power_flow_at_hour(hour/2)
    circuit.update_sys_voltage()
    circuit.update_line_flow()
    # After running the final solution update the Results log
    Results.update_lines_results(circuit.get_lines_results())
    Results.update_buses_results(circuit.get_buses_results())
    for pv in pv_set:
        circuit._dss_object.ActiveCircuit.PVSystems.Name = pv
        active_power[pv] = abs(circuit._dss_object.ActiveCircuit.ActiveCktElement.Powers[0])
        reactive_power[pv] = - (circuit._dss_object.ActiveCircuit.ActiveCktElement.Powers[1])
    Results._update_pv_active_power_results(active_power)
    Results._update_pv_reactive_power_results(reactive_power)

opendss_voltages_a = Results.VOLTAGE_HISTORY_A
opendss_voltages_b = Results.VOLTAGE_HISTORY_B
opendss_voltages_c = Results.VOLTAGE_HISTORY_C
opendss_voltages = opendss_voltages_a | opendss_voltages_b | opendss_voltages_c
opendss_currents_a = Results.LINE_CURRENT_A
opendss_currents_b = Results.LINE_CURRENT_B
opendss_currents_c = Results.LINE_CURRENT_C

opendss_pv_active_power = Results.PV_INVERTER_ACTIVE_POWER
opendss_pv_reactive_power = Results.PV_INVERTER_REACTIVE_POWER

print(model_pv_active_power['pv_158'])
print(opendss_pv_active_power['pv_158'])
print('\n')
print(model_pv_reactive_power['pv_158'])
print(opendss_pv_reactive_power['pv_158'])

active_power = np.array((model_pv_active_power['pv_158']))
reactive_power = np.array((model_pv_reactive_power['pv_158']))
apparent_power = np.sqrt(np.power(active_power, 2) + np.power(reactive_power, 2))
print(apparent_power)

active_power = np.array((opendss_pv_active_power['pv_158']))
reactive_power = np.array((opendss_pv_reactive_power['pv_158']))
apparent_power = np.sqrt(np.power(active_power, 2) + np.power(reactive_power, 2))
print(apparent_power)
results = run_comprehensive_comparison(your_model_voltages=model_voltages, opendss_voltages=opendss_voltages, your_model_currents=model_currents_a,
                                       opendss_currents=opendss_currents_a, your_model_active_pv_power=model_pv_active_power, opendss_active_pv_power=opendss_pv_active_power,
                                       your_model_reactive_pv_power=model_pv_reactive_power, opendss_reactive_pv_power=opendss_pv_reactive_power, save_plots_dir='comparison_plots')

# Print summary metrics
print("Voltage Metrics:")
print(f"RMSE: {results['voltage_metrics']['rmse']:.4f}")
print(f"Mean Absolute Error: {results['voltage_metrics']['mean_abs']:.4f}")
print(f"Mean Relative Error: {results['voltage_metrics']['mean_rel']:.2f}%")

print("\nCurrent Metrics:")
print(f"RMSE: {results['current_metrics']['rmse'] / 100:.4f}")
print(f"Mean Absolute Error: {results['current_metrics']['mean_abs'] / 100:.4f}")
print(f"Mean Relative Error: {results['current_metrics']['mean_rel'] / 100:.2f}%")

print("\nPV Active Power Metrics:")
print(f"RMSE: {results['pv_active_power_metrics']['rmse'] / 100:.4f}")
print(f"Mean Absolute Error: {results['pv_active_power_metrics']['mean_abs'] / 100:.4f}")
print(f"Mean Relative Error: {results['pv_active_power_metrics']['mean_rel'] / 100:.2f}%")

print("\nPV Reactive Power Metrics:")
print(f"RMSE: {results['pv_reactive_power_metrics']['rmse'] / 100:.4f}")
print(f"Mean Absolute Error: {results['pv_reactive_power_metrics']['mean_abs'] / 100:.4f}")
print(f"Mean Relative Error: {results['pv_reactive_power_metrics']['mean_rel'] / 100:.2f}%")