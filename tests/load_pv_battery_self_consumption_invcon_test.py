from src.external_input_data import ModelInputData, import_txt_file_as_numpy
from src.models.load import Load
from src.models.inverter import Inverter, HybridInverter, InverterSettings, VoltWatt, VoltVar, HybridInverterSettings, MaximiseSelfConsumptionSettings
from src.models.pv_panel import PVPanels
from src.models.pv_system import PVSystem, HybridPVSystem
from src.models.meter import Meter
from src.models.battery import Battery
from src.results import Results
from src.plots import Plots
from src.circuit_interface import CircuitInterface
from src.solver import Compiler
from src.tests import run_comprehensive_comparison
from src.utils import remove_sublist
from datetime import time
import os
import csv

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
model_data = ModelInputData(demand_power, irradiance, temperature, 30, None)
print(model_data.irradiance)
# Second, create the CER models and assign the relevant circuit labels using models
loads_circuit_labels = circuit_labels
hybrid_pv_self_consumption_circuit_labels = [3, 8, 10, 14, 17, 20, 22, 32, 37, 44, 51, 61, 70, 75, 89, 101, 105, 117, 120, 127, 134, 135, 145, 156, 161]
pv_systems_circuit_labels = remove_sublist(circuit_labels, hybrid_pv_self_consumption_circuit_labels)
loads = {label: Load(label) for label in loads_circuit_labels}
pv_panels = PVPanels()
inverter_settings = InverterSettings()
inverter_settings.enable_volt_watt(VoltWatt())
inverter_settings.enable_volt_var(VoltVar())
hybrid_inverter_settings = HybridInverterSettings()
charging_volt_watt = VoltWatt([[0.9, 0.94, 1.1], [0.2, 1, 1]])
hybrid_inverter_settings.enable_volt_var(VoltVar())
hybrid_inverter_settings.enable_volt_watt(VoltWatt())
hybrid_inverter_settings.enable_charging_volt_watt_settings(charging_volt_watt)
hybrid_inverter_settings.enable_maximise_self_consumption_settings(MaximiseSelfConsumptionSettings())
hybrid_inverters = {label: HybridInverter(circuit_label=label, hybrid_inverter_settings=hybrid_inverter_settings) for label in hybrid_pv_self_consumption_circuit_labels}
meters = {label: Meter(label, loads=[loads[label]], inverters=[hybrid_inverters[label]]) for label in hybrid_pv_self_consumption_circuit_labels}
inverter = Inverter(inverter_settings=inverter_settings)
batteries = {label: Battery(label) for label in hybrid_pv_self_consumption_circuit_labels}
pv_systems = [PVSystem(label, pv_panels, inverter) for label in pv_systems_circuit_labels]
hybrid_pv_systems = [HybridPVSystem(label, pv_panels, batteries[label], hybrid_inverters[label], meters[label]) for label in hybrid_pv_self_consumption_circuit_labels]
cers = list(loads.values()) + pv_systems + hybrid_pv_systems
# Third, create the opendss circuit interface using CircuitInterface
with open(os.path.dirname(os.path.dirname(__file__)) + f"/Data/Network_Model/label_bus_dict.csv", 'r') as csvfile:
    reader = csv.reader(csvfile)
    label_bus_dict = {int(row[0]): row[1] for row in reader}
opendss_path = os.path.dirname(os.path.dirname(__file__)) + f"/Data/Network_Model/model.dss"
circuit = CircuitInterface(opendss_path, label_bus_dict, {'load': loads_circuit_labels, 'pvsystem': pv_systems_circuit_labels, 'hybridpvsystem': hybrid_pv_self_consumption_circuit_labels})
# Fourth, initialise the Results class with appropriate info from the CircuitInterface instance
time_settings = [time(0, 0), time(23, 30), 30]
end_buses = circuit.end_buses
lines_ratings = circuit.lines_rating
Results.initialise(time_settings, end_buses, lines_ratings,,
# Fourth, solve the circuit using Compiler
solver = Solver(circuit, cers, model_data)
for step in range(0, 48):
    solver.cer_convergence_process(step)
    print('soc:', batteries[161].soc)
    # print('p_batt', hybrid_inverters[3]._battery_power)

model_voltages_a = Results.VOLTAGE_HISTORY_A
model_voltages_b = Results.VOLTAGE_HISTORY_B
model_voltages_c = Results.VOLTAGE_HISTORY_C

model_currents_a = Results.LINE_CURRENT_A
model_currents_b = Results.LINE_CURRENT_B
model_currents_c = Results.LINE_CURRENT_C

# Run the opendss model
# First, create the opendss circuit interface using CircuitInterface
with open(os.path.dirname(os.path.dirname(__file__)) + f"/Data/Network_Model/label_bus_dict.csv", 'r') as csvfile:
    reader = csv.reader(csvfile)
    label_bus_dict = {int(row[0]): row[1] for row in reader}
opendss_path = os.path.dirname(os.path.dirname(__file__)) + f"/opendss_models_for_tests/load_pv_battery_self_consumption_invcon/Main.dss"
circuit = CircuitInterface(opendss_path, label_bus_dict)
# Fourth, initialise the Results class with appropriate info from the CircuitInterface instance
time_settings = [time(0, 0), time(23, 30), 30]
end_buses = circuit.end_buses
lines_ratings = circuit.lines_rating
Results.initialise(time_settings, end_buses, lines_ratings,,

for hour in range(48):
    circuit.solve_power_flow_at_hour(hour / 2)
    circuit.update_sys_voltage()
    circuit.update_line_flow()
    # After running the final solution update the Results log
    Results.update_lines_results(circuit.get_lines_results())
    Results.update_buses_results(circuit.get_buses_results())

opendss_voltages_a = Results.VOLTAGE_HISTORY_A
opendss_voltages_b = Results.VOLTAGE_HISTORY_B
opendss_voltages_c = Results.VOLTAGE_HISTORY_C

opendss_currents_a = Results.LINE_CURRENT_A
opendss_currents_b = Results.LINE_CURRENT_B
opendss_currents_c = Results.LINE_CURRENT_C

print(model_currents_a['line29.1'])
print(opendss_currents_a['line29.1'])

results = run_comprehensive_comparison(
    your_model_voltages=model_voltages_a,
    opendss_voltages=opendss_voltages_a,
    your_model_currents=model_currents_a,
    opendss_currents=opendss_currents_a,
    save_plots_dir='comparison_plots'
)

# Print summary metrics
print("Voltage Metrics:")
print(f"RMSE: {results['voltage_metrics']['rmse']:.4f}")
print(f"Mean Absolute Error: {results['voltage_metrics']['mean_abs']:.4f}")
print(f"Mean Relative Error: {results['voltage_metrics']['mean_rel']:.2f}%")

print("\nCurrent Metrics:")
print(f"RMSE: {results['current_metrics']['rmse']:.4f}")
print(f"Mean Absolute Error: {results['current_metrics']['mean_abs']:.4f}")
print(f"Mean Relative Error: {results['current_metrics']['mean_rel']:.2f}%")