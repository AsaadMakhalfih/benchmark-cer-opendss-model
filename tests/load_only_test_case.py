from src.external_input_data import ModelInputData, import_txt_file_as_numpy
from src.models import Load
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
circuit_labels = list(range(1, 166))
demand_power = {circuit_label: None for circuit_label in circuit_labels}
for label in circuit_labels:
    demand_power[label] = import_txt_file_as_numpy(load_data_path + f'/{day}/Load{label}.txt')
step_size = 30
time_range = [0, 23.5]
model_data = ModelInputData(demand_power, None, None, step_size, time_range, None)
# Second, create the CER models and assign the relevant circuit labels using models
loads_circuit_labels = circuit_labels
loads = [Load(label) for label in loads_circuit_labels]
cers = loads
# Third, create the opendss circuit interface using CircuitInterface
with open(os.path.dirname(os.path.dirname(__file__)) + f"/Data/Network_Model/label_bus_dict.csv", 'r') as csvfile:
    reader = csv.reader(csvfile)
    label_bus_dict = {int(row[0]): row[1] for row in reader}
opendss_path = os.path.dirname(os.path.dirname(__file__)) + f"/Data/Network_Model/model.dss"
circuit = CircuitInterface(opendss_path, label_bus_dict, {'load': loads_circuit_labels})
# Fourth, initialise the Results class with appropriate info from the CircuitInterface instance
time_settings = [time(0, 0), time(23, 30), 30]
end_buses = circuit.end_buses
lines_ratings = circuit.lines_rating
Results.initialise(time_settings, end_buses, lines_ratings, None, None)
# Fourth, solve the circuit using Compiler
solver = Compiler(circuit, cers, model_data)
for step in range(0, 48):
    solver.cer_convergence_process(step)

model_voltages_a = Results.VOLTAGE_HISTORY_A
model_voltages_b = Results.VOLTAGE_HISTORY_B
model_voltages_c = Results.VOLTAGE_HISTORY_C
model_voltages = model_voltages_a | model_voltages_b | model_voltages_c
model_currents_a = Results.LINE_CURRENT_A
model_currents_b = Results.LINE_CURRENT_B
model_currents_c = Results.LINE_CURRENT_C

# Run the opendss model
# First, create the opendss circuit interface using CircuitInterface
with open(os.path.dirname(os.path.dirname(__file__)) + f"/Data/Network_Model/label_bus_dict.csv", 'r') as csvfile:
    reader = csv.reader(csvfile)
    label_bus_dict = {int(row[0]): row[1] for row in reader}
opendss_path = os.path.dirname(os.path.dirname(__file__)) + f"/opendss_models_for_tests/load_only/Main.dss"
circuit = CircuitInterface(opendss_path, label_bus_dict)
# Fourth, initialise the Results class with appropriate info from the CircuitInterface instance
time_settings = [time(0, 0), time(23, 30), 30]
end_buses = circuit.end_buses
lines_ratings = circuit.lines_rating
Results.initialise(time_settings, end_buses, lines_ratings, None, None)

for hour in range(48):
    circuit.solve_power_flow_at_hour(hour/2)
    circuit.update_sys_voltage()
    circuit.update_line_flow()
    # After running the final solution update the Results log
    Results.update_lines_results(circuit.get_lines_results())
    Results.update_buses_results(circuit.get_buses_results())


opendss_voltages_a = Results.VOLTAGE_HISTORY_A
opendss_voltages_b = Results.VOLTAGE_HISTORY_B
opendss_voltages_c = Results.VOLTAGE_HISTORY_C
opendss_voltages = opendss_voltages_a | opendss_voltages_b | opendss_voltages_c
opendss_currents_a = Results.LINE_CURRENT_A
opendss_currents_b = Results.LINE_CURRENT_B
opendss_currents_c = Results.LINE_CURRENT_C


results = run_comprehensive_comparison(
    your_model_voltages=model_voltages,
    opendss_voltages=opendss_voltages,
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
