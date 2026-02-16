from src.external_input_data import ModelInputData, import_txt_file_as_numpy
from src.models.load import Load
from src.models.inverter import Inverter, HybridInverter, EVInverter, InverterSettings, VoltWatt, VoltVar, HybridInverterSettings, TimeOfUseSettings, \
    EVInverterSettings, UnmanagedEVCharging, ManagedEVCharging, V2GEVCharging
from src.models.pv_panel import PVPanels
from src.models.pv_system import PVSystem, HybridPVSystem
from src.models.ev import EVSystem
from src.models.vehicle import Vehicle
from src.models.meter import Meter
from src.models.battery import Battery
from src.results import Results
from src.plots import Plots
from src.circuit_interface import CircuitInterface
from src.compiler import Compiler
from src.utils import remove_sublist, intersection, get_ev_behaviour
from datetime import time
import os
import csv
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

days = ['summer-weekday', 'summer-weekend', 'winter-weekday', 'winter-weekend']
for day in days:
    # First, create the input data for the model using ModelInputData
    load_data_path = os.path.dirname(os.path.dirname(__file__)) + "/Data/Load_Data_Hourly"
    irrad_data_path = os.path.dirname(os.path.dirname(__file__)) + "/Data/PV_Data"
    temp_data_path = os.path.dirname(os.path.dirname(__file__)) + "/Data/PV_Data"
    ev_behaviour_data_path = os.path.dirname(os.path.dirname(__file__)) + f"/Data/EV_Data/evs_behaviour_hourly_{day}.csv"
    circuit_labels = list(range(1, 166))
    demand_power = {circuit_label: None for circuit_label in circuit_labels}
    for label in circuit_labels:
        demand_power[label] = import_txt_file_as_numpy(load_data_path + f'/{day}/Load{label}.txt')
    ev_behaviours = {circuit_label: None for circuit_label in circuit_labels}
    for label in circuit_labels:
        ev_behaviours[label] = get_ev_behaviour(label, ev_behaviour_data_path)
    irradiance = import_txt_file_as_numpy(irrad_data_path + f'/{day}/solar_hourly.txt')
    temperature = import_txt_file_as_numpy(temp_data_path + f'/{day}/temp_hourly.txt')
    step_size = 60
    time_range = [0, 23]
    model_data = ModelInputData(demand_power, irradiance, temperature, step_size, time_range, ev_behaviours)
    # Second, create the CER models and assign the relevant circuit labels using models
    loads_circuit_labels = circuit_labels
    hybrid_pv_time_of_use_circuit_labels = [3, 8, 10, 14, 17, 20, 22, 32, 37, 44, 51, 61, 70, 75, 89, 101, 105, 117, 120, 127, 134, 135, 145, 156, 161]
    v2g_ev_circuit_labels = [1, 2, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 26, 29, 31, 32, 35, 42, 48, 51, 52, 55, 57, 63, 71, 75, 76, 78, 81, 82, 84, 91, 94, 99, 101, 110, 112,
                             115, 117, 118, 121, 122, 129, 132, 134, 137, 139, 141, 147, 150, 151, 153, 157, 158, 162, 163, 165]
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
    batteries = {label: Battery(label, step_size=step_size) for label in hybrid_pv_time_of_use_circuit_labels}
    meters_1 = {label: Meter(label, loads=[loads[label]], inverters=[hybrid_inverters[label]]) for label in hybrid_pv_time_of_use_circuit_labels}
    meters_2 = {label: Meter(label, loads=[loads[label]], inverters=[inverters[label]]) for label in pv_systems_circuit_labels}
    meters = meters_1 | meters_2
    pv_systems = [PVSystem(label, pv_panels[label], inverters[label], meters[label]) for label in pv_systems_circuit_labels]
    hybrid_pv_systems = [HybridPVSystem(label, pv_panels[label], batteries[label], hybrid_inverters[label], meters[label]) for label in hybrid_pv_time_of_use_circuit_labels]
    # EV systems
    ev_inverter_settings = {label: EVInverterSettings() for label in v2g_ev_circuit_labels}
    for label in v2g_ev_circuit_labels:
        ev_inverter_settings[label].enable_volt_var(VoltVar())
        ev_inverter_settings[label].enable_volt_watt(VoltWatt())
        ev_inverter_settings[label].enable_charging_volt_watt_settings(charging_volt_watt)
        ev_inverter_settings[label].enable_v2g_charging(V2GEVCharging(step_size=step_size))
    ev_inverters = {label: EVInverter(circuit_label=label, ev_inverter_settings=ev_inverter_settings[label]) for label in v2g_ev_circuit_labels}
    ev_batteries = {label: Battery(label, capacity=62, soc=0.5, min_soc=0.2, step_size=step_size) for label in v2g_ev_circuit_labels}
    ev_cars = {label: Vehicle(label, model_data.ev_behaviour[label]['driving_distance'], model_data.ev_behaviour[label]['driving_intervals'], battery_range=350,
                              step_size=step_size) for label in v2g_ev_circuit_labels}
    ev_systems = {label: EVSystem(label, ev_cars[label], ev_batteries[label], ev_inverters[label]) for label in v2g_ev_circuit_labels}
    # Update meters to add
    for label in v2g_ev_circuit_labels:
        meters[label].add_ev(ev_systems[label])
    cers = list(loads.values()) + pv_systems + hybrid_pv_systems + list(ev_systems.values())

    # Third, create the opendss circuit interface using CircuitInterface
    with open(os.path.dirname(os.path.dirname(__file__)) + f"/Data/Network_Model/label_bus_dict.csv", 'r') as csvfile:
        reader = csv.reader(csvfile)
        label_bus_dict = {int(row[0]): row[1] for row in reader}
    opendss_path = os.path.dirname(os.path.dirname(__file__)) + f"/Data/Network_Model/model.dss"
    circuit = CircuitInterface(opendss_path, label_bus_dict,
                               {'load': loads_circuit_labels, 'pvsystem': pv_systems_circuit_labels, 'hybridpvsystem': hybrid_pv_time_of_use_circuit_labels,
                                'evsystem': v2g_ev_circuit_labels})
    # Fourth, initialise the Results class with appropriate info from the CircuitInterface instance
    time_settings = [time(0, 0), time(23, 00), 60]
    end_buses = circuit.end_buses
    lines_ratings = circuit.lines_rating
    pv_set = circuit.pv_set
    ev_set = circuit.ev_set
    systems = circuit.models_circuit_labels
    Results.initialise(time_settings, end_buses, lines_ratings, pv_set, meters, ev_set, step_size)
    # Fourth, solve the circuit using Compiler
    solver = Compiler(circuit, cers, model_data)
    # delta_p_q_settings = (0.175, 0.07, 0.12, 0.05, 0.165, 0.065, 0.124, 0.05)
    delta_p_q_settings = (0.16, 0.07, 0.12, 0.05, 0.165, 0.08, 0.1, 0.07)
    solver.change_delta_p_q_settings(delta_p_q_settings)
    for step in range(0, 24):
        solver.cer_convergence_process(step)
        print('time:', step, 'soc:', batteries[3].soc, 'ev soc:', ev_systems[3].battery.soc)
        # print('p_batt', hybrid_inverters[3]._battery_power)

    # print(Results.TOTAL_LOSSES)
    # print(Results.AC_CURTAILMENT_A)
    # Plots.plot_voltages_whisker_plots()
    # Plots.plot_vuf_whisker_plots()
    # Plots.plot_line_currents_whisker_plots()
    # Plots.plot_ac_curtailment_bar_plots()
    # Results.export_energy_flow_results(os.path.dirname(__file__) + "/results/results.xlsx")
    case_name = f'load_pv_battery_time_of_use_v2g_inv_con_hourly_{day}'
    Results.export_summary_results(path=os.path.dirname(__file__) + '/results', file_name=case_name)
    Results.export_energy_flow_results(path=os.path.dirname(__file__) + '/results', file_name=f'load_pv_battery_time_of_use_v2g_inv_con_hourly_energy_flow_{day}')
    case_name = f'load_pv_battery_time_of_use_v2g_inv_con_hourly'
    Results.export_energy_flow_results(path=os.path.dirname(__file__) + '/results', file_name=f'load_pv_battery_time_of_use_v2g_inv_con_hourly_energy_flow_{day}')
    Results.export_metrics(path=os.path.dirname(__file__) + '/results', file_name=f'{case_name}_metrics_{day}')
    Results.export_voltages(path=os.path.dirname(__file__) + '/results', file_name=f'{case_name}_voltages_{day}')
    Results.export_line_currents(path=os.path.dirname(__file__) + '/results', file_name=f'{case_name}_line_currents_{day}')
    Results.export_voltage_unbalance(path=os.path.dirname(__file__) + '/results', file_name=f'{case_name}_voltage_unbalance_{day}')
    Results.export_ac_curtailment(path=os.path.dirname(__file__) + '/results', file_name=f'{case_name}_ac_curtailment_{day}')
    Results.export_dc_curtailment(path=os.path.dirname(__file__) + '/results', file_name=f'{case_name}_dc_curtailment_{day}')
    Results.export_reactive_power_results(path=os.path.dirname(__file__) + '/results', file_name=f'{case_name}_reactive_powers_{day}')
    Plots.plot_and_save_all(os.path.dirname(__file__) + f'/plots/{case_name}/{day}/', extra_disc=f'_{case_name}')
