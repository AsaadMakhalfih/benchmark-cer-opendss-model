from src.external_input_data import ModelInputData, import_txt_file_as_numpy
from src.models.load import Load
from src.circuit_interface import CircuitInterface
from src.compiler import Compiler
from src.plots import Plots
from src.results import Results
from datetime import time
import os
import csv
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

days = ['summer-weekday', 'summer-weekend', 'winter-weekday', 'winter-weekend']
for day in days:
    # First, create the input data for the model using ModelInputData
    load_data_path = os.path.dirname(os.path.dirname(__file__)) + "/data/load-data"
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
    with open(os.path.dirname(os.path.dirname(__file__)) + f"/data/network-model/label_bus_dict.csv", 'r') as csvfile:
        reader = csv.reader(csvfile)
        label_bus_dict = {int(row[0]): row[1] for row in reader}
    opendss_path = os.path.dirname(os.path.dirname(__file__)) + f"/simple-data/model.dss"
    circuit = CircuitInterface(opendss_path, label_bus_dict, {'load': loads_circuit_labels})

    time_settings = [time(0, 0), time(23, 30), 30]
    end_buses = circuit.end_buses
    lines_ratings = circuit.lines_rating

    Results.initialise(time_settings, end_buses, lines_ratings, None, None)

    # Fourth, solve the circuit using Compiler
    solver = Compiler(circuit, cers, model_data)
    for step in range(0, 48):
        solver.cer_convergence_process(step)
    # case_name = f'baseline_{day}'
    # Results.export_summary_results(path=os.path.dirname(__file__) + '/results', file_name=case_name)

    Results.export_metrics(path=os.path.dirname(__file__) + '/results', file_name=f'baseline_metrics_{day}')
    Results.export_voltages(path=os.path.dirname(__file__) + '/results', file_name=f'baseline_voltages_{day}')
    Results.export_line_currents(path=os.path.dirname(__file__) + '/results', file_name=f'baseline_line_currents_{day}')
    Results.export_voltage_unbalance(path=os.path.dirname(__file__) + '/results', file_name=f'baseline_voltage_unbalance_{day}')
    Plots.plot_and_save_all(os.path.dirname(__file__) + f'/plots/baseline/{day}/', extra_disc='_baseline_' + day)
