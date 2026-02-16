from src.external_input_data import ModelInputData, import_txt_file_as_numpy
from src.models import Load, PVSystem, PVPanels, Inverter, InverterSettings, VoltWatt
from src.circuit_interface import CircuitInterface
from src.compiler import Compiler
import os
import csv

# First, create the input data for the model using ModelInputData
load_data_path = os.path.dirname(os.path.dirname(__file__)) + "/simple-data/loads"
irrad_data_path = os.path.dirname(os.path.dirname(__file__)) + "/simple-data"
temp_data_path = os.path.dirname(os.path.dirname(__file__)) + "/simple-data"
ev_behaviour_data_path = os.path.dirname(os.path.dirname(__file__)) + "/simple-data"
circuit_labels = list(range(1, 166))
demand_power = {circuit_label: None for circuit_label in circuit_labels}
for label in circuit_labels:
    demand_power[label] = import_txt_file_as_numpy(load_data_path + f'/Load{label}.txt')
irradiance = import_txt_file_as_numpy(irrad_data_path + f'/solar.txt')
temperature = import_txt_file_as_numpy(temp_data_path + f'/temp.txt')
model_data = ModelInputData(demand_power, irradiance, temperature)
# Second, create the CER models and assign the relevant circuit labels using models
loads_circuit_labels = circuit_labels
pv_systems_circuit_labels = [165]
loads = [Load(label) for label in loads_circuit_labels]
pv_panels = PVPanels()
inverter_settings = InverterSettings()
inverter_settings.enable_volt_watt(VoltWatt())
inverter = Inverter(inverter_settings=inverter_settings)
pv_system = PVSystem(pv_systems_circuit_labels[0], pv_panels, inverter)
cers = loads + [pv_system]
# Third, create the opendss circuit interface using CircuitInterface
with open(os.path.dirname(os.path.dirname(__file__)) + f"/data/network-model/label_bus_dict.csv", 'r') as csvfile:
    reader = csv.reader(csvfile)
    label_bus_dict = {int(row[0]): row[1] for row in reader}
opendss_path = os.path.dirname(os.path.dirname(__file__)) + f"/simple-data/model.dss"
circuit = CircuitInterface(opendss_path, label_bus_dict, {'load': loads_circuit_labels, 'pvsystem': pv_systems_circuit_labels})
# Fourth, solve the circuit using Compiler
solver = Compiler(circuit, cers, model_data)
for step in range(0, 48):
    solver.cer_convergence_process(step)
