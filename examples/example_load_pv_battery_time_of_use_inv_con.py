from src.external_input_data import ModelInputData, import_txt_file_as_numpy
from src.models.load import Load
from src.models.inverter import Inverter, HybridInverter, InverterSettings, VoltWatt, VoltVar, HybridInverterSettings, TimeOfUseSettings
from src.models.pv_panel import PVPanels
from src.models.pv_system import PVSystem, HybridPVSystem
from src.models.meter import Meter
from src.models.battery import Battery
from src.results import Results
from src.plots import Plots
from src.circuit_interface import CircuitInterface
from src.compiler import Compiler
from src.utils import remove_sublist
from datetime import time
import os
import csv
import warnings
import time as ctime
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

days = ['summer-weekday', 'summer-weekend', 'winter-weekday', 'winter-weekend']
for day in days:
    # First, create the input data for the model using ModelInputData
    load_data_path = os.path.dirname(os.path.dirname(__file__)) + "/data/load-data"
    irrad_data_path = os.path.dirname(os.path.dirname(__file__)) + "/data/pv-data"
    temp_data_path = os.path.dirname(os.path.dirname(__file__)) + "/data/pv-data"
    ev_behaviour_data_path = os.path.dirname(os.path.dirname(__file__)) + "/data/ev-data"
    circuit_labels = list(range(1, 166))
    demand_power = {circuit_label: None for circuit_label in circuit_labels}
    for label in circuit_labels:
        demand_power[label] = import_txt_file_as_numpy(load_data_path + f'/{day}/Load{label}.txt')
    irradiance = import_txt_file_as_numpy(irrad_data_path + f'/{day}/solar.txt')
    temperature = import_txt_file_as_numpy(temp_data_path + f'/{day}/temp.txt')
    step_size = 30
    time_range = [0, 23.5]
    model_data = ModelInputData(demand_power, irradiance, temperature, step_size, time_range, None)
    # Second, create the CER models and assign the relevant circuit labels using models
    loads_circuit_labels = circuit_labels
    hybrid_pv_time_of_use_circuit_labels = [3, 8, 10, 14, 17, 20, 22, 32, 37, 44, 51, 61, 70, 75, 89, 101, 105, 117, 120, 127, 134, 135, 145, 156, 161]
    pv_systems_circuit_labels = remove_sublist(circuit_labels, hybrid_pv_time_of_use_circuit_labels)
    loads = {label: Load(label) for label in loads_circuit_labels}
    pv_panels = {label: PVPanels(label) for label in circuit_labels}
    inverter_settings = InverterSettings()
    inverter_settings.enable_volt_watt(VoltWatt())
    inverter_settings.enable_volt_var(VoltVar())
    hybrid_inverter_settings = HybridInverterSettings()
    charging_volt_watt = VoltWatt([[0.9, 0.94, 1.1], [0.2, 1, 1]])
    hybrid_inverter_settings.enable_volt_var(VoltVar())
    hybrid_inverter_settings.enable_volt_watt(VoltWatt())
    hybrid_inverter_settings.enable_charging_volt_watt_settings(charging_volt_watt)
    hybrid_inverter_settings.enable_time_of_use_settings(TimeOfUseSettings(step_size=step_size))
    hybrid_inverters = {label: HybridInverter(circuit_label=label, hybrid_inverter_settings=hybrid_inverter_settings) for label in hybrid_pv_time_of_use_circuit_labels}
    inverters = {label: Inverter(circuit_label=label, inverter_settings=inverter_settings) for label in pv_systems_circuit_labels}
    meters_1 = {label: Meter(label, loads=[loads[label]], inverters=[hybrid_inverters[label]]) for label in hybrid_pv_time_of_use_circuit_labels}
    meters_2 = {label: Meter(label, loads=[loads[label]], inverters=[inverters[label]]) for label in pv_systems_circuit_labels}
    meters = meters_1 | meters_2
    batteries = {label: Battery(label, step_size=step_size) for label in hybrid_pv_time_of_use_circuit_labels}
    pv_systems = [PVSystem(label, pv_panels[label], inverters[label], meters[label]) for label in pv_systems_circuit_labels]
    hybrid_pv_systems = [HybridPVSystem(label, pv_panels[label], batteries[label], hybrid_inverters[label], meters[label]) for label in hybrid_pv_time_of_use_circuit_labels]
    cers = list(loads.values()) + pv_systems + hybrid_pv_systems
    # Third, create the opendss circuit interface using CircuitInterface
    with open(os.path.dirname(os.path.dirname(__file__)) + f"/data/network-model/label_bus_dict.csv", 'r') as csvfile:
        reader = csv.reader(csvfile)
        label_bus_dict = {int(row[0]): row[1] for row in reader}
    opendss_path = os.path.dirname(os.path.dirname(__file__)) + f"/data/network-model/model.dss"
    circuit = CircuitInterface(opendss_path, label_bus_dict, {'load': loads_circuit_labels, 'pvsystem': pv_systems_circuit_labels, 'hybridpvsystem': hybrid_pv_time_of_use_circuit_labels})
    # Fourth, initialise the Results class with appropriate info from the CircuitInterface instance
    time_settings = [time(0, 0), time(23, 30), 30]
    end_buses = circuit.end_buses
    lines_ratings = circuit.lines_rating
    pv_set = circuit.pv_set
    Results.initialise(time_settings, end_buses, lines_ratings, pv_set, meters, step_size=step_size)
    # Fourth, solve the circuit using Compiler
    solver = Compiler(circuit, cers, model_data)
    delta_p_q_settings = (0.15, 0.05, 0.1, 0.05, 0.149, 0.05, 0.1, 0.05)
    # delta_p_q_settings = (0.15, 0.05, 0.1, 0.05, 0.15, 0.05, 0.1, 0.05)
    solver.change_delta_p_q_settings(settings=delta_p_q_settings)
    t1 = ctime.time()
    for step in range(0, 48):
        solver.cer_convergence_process(step)
    t2 = ctime.time()
    Results.update_simulation_time(t2 - t1)

    Plots.plot_voltages_whisker_plots()
    Plots.plot_vuf_whisker_plots()
    Plots.plot_line_currents_whisker_plots()
    Plots.plot_ac_curtailment_bar_plots()
    case_name = f'load_pv_battery_time_of_use_inv_con_{day}'
    Results.export_summary_results(path=os.path.dirname(__file__) + '/results', file_name=case_name)
    Results.export_energy_flow_results(path=os.path.dirname(__file__) + '/results', file_name=f'load_pv_battery_time_of_use_inv_con_energy_flow_{day}')
    Results.export_metrics(path=os.path.dirname(__file__) + '/results', file_name=f'load_pv_battery_time_of_use_inv_con_metrics_{day}')
    Results.export_voltages(path=os.path.dirname(__file__) + '/results', file_name=f'load_pv_battery_time_of_use_inv_con_voltages_{day}')
    Results.export_line_currents(path=os.path.dirname(__file__) + '/results', file_name=f'load_pv_battery_time_of_use_inv_con_line_currents_{day}')
    Results.export_voltage_unbalance(path=os.path.dirname(__file__) + '/results', file_name=f'load_pv_battery_time_of_use_inv_con_voltage_unbalance_{day}')
    Results.export_ac_curtailment(path=os.path.dirname(__file__) + '/results', file_name=f'load_pv_battery_time_of_use_inv_con_ac_curtailment_{day}')
    Results.export_dc_curtailment(path=os.path.dirname(__file__) + '/results', file_name=f'load_pv_battery_time_of_use_inv_con_dc_curtailment_{day}')
    Plots.plot_and_save_all(os.path.dirname(__file__) + f'/plots/load_pv_battery_time_of_use_inv_con/{day}/', extra_disc=f'_{case_name}')