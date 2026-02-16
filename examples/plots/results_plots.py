from src.plots import Plots
import os

# Scenarios = ['baseline', 'load_pv', 'load_pv_export_limit', 'load_pv_inv_con', 'load_pv_battery_time_of_use_inv_con', 'load_pv_battery_time_of_use_v2g_inv_con']  # ,
Scenarios = ['baseline_hourly', 'load_pv_only_hourly', 'load_pv_export_limit_hourly', 'load_pv_inv_con_hourly', 'load_pv_battery_time_of_use_inv_con_hourly',
             'load_pv_battery_time_of_use_v2g_inv_con_hourly']  # ,

# 'load_pv_battery_time_of_use_v2g_export_limit']  # , 'load_pv_battery_time_of_use_v2g_inv_con_export_limit']
# Scenarios = ['load_pv_export_limit']
Plots.plot_voltage_scenario_envelopes(os.path.dirname(os.path.dirname(__file__)), Scenarios, save_path=os.path.dirname(__file__))
Plots.plot_line_current_envelopes(os.path.dirname(os.path.dirname(__file__)), Scenarios, save_path=os.path.dirname(__file__))
Plots.plot_voltage_unbalance_scenario_envelopes(os.path.dirname(os.path.dirname(__file__)), Scenarios, save_path=os.path.dirname(__file__))
Plots.plot_ac_curtailment_total(os.path.dirname(os.path.dirname(__file__)), Scenarios, save_path=os.path.dirname(__file__))
Plots.plot_dc_curtailment_total(os.path.dirname(os.path.dirname(__file__)), Scenarios, save_path=os.path.dirname(__file__))
csv_files = os.listdir(os.path.dirname(os.path.dirname(__file__)) + f'/results')
print(csv_files)
for scenario in Scenarios:
    # paths = [os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_voltages_Summer_Weekday.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_voltages_Summer_Weekend.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_voltages_Winter_Weekday.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_voltages_Winter_Weekend.csv']

    paths = [os.path.dirname(os.path.dirname(__file__)) + f'/results/{file}' for file in csv_files if
             scenario.replace('_hourly', "") in file and 'hourly' in file and 'voltages' in file][:4]
    print(paths)
    Plots.plot_voltages_from_csv(paths, save_path=os.path.dirname(__file__) + f'/{scenario}')

    # paths = [os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_line_currents_Summer_Weekday.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_line_currents_Summer_Weekend.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_line_currents_Winter_Weekday.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_line_currents_Winter_Weekend.csv']
    paths = [os.path.dirname(os.path.dirname(__file__)) + f'/results/{file}' for file in csv_files if
             scenario.replace('_hourly', "") in file and 'hourly' in file and 'line_currents' in file][:4]
    print(paths)
    Plots.plot_currents_from_csv(paths, save_path=os.path.dirname(__file__) + f'/{scenario}')

    # paths = [os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_voltage_unbalance_Summer_Weekday.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_voltage_unbalance_Summer_Weekend.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_voltage_unbalance_Winter_Weekday.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_voltage_unbalance_Winter_Weekend.csv']
    paths = [os.path.dirname(os.path.dirname(__file__)) + f'/results/{file}' for file in csv_files if
             scenario.replace('_hourly', "") in file and 'hourly' in file and 'voltage_unbalance' in file][:4]
    print(paths)
    Plots.plot_voltage_unbalance_from_csv(paths, save_path=os.path.dirname(__file__) + f'/{scenario}')
    if 'baseline' in scenario:
        continue
    # paths = [os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_ac_curtailment_Summer_Weekday.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_ac_curtailment_Summer_Weekend.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_ac_curtailment_Winter_Weekday.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_ac_curtailment_Winter_Weekend.csv']
    paths = [os.path.dirname(os.path.dirname(__file__)) + f'/results/{file}' for file in csv_files if
             scenario.replace('_hourly', "") in file and 'hourly' in file and 'ac_curtailment' in file][:4]
    print(paths)
    print(len(paths))
    Plots.plot_ac_curtailment_from_csv(paths, save_path=os.path.dirname(__file__) + f'/{scenario}')

    # paths = [os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_dc_curtailment_Summer_Weekday.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_dc_curtailment_Summer_Weekend.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_dc_curtailment_Winter_Weekday.csv',
    #          os.path.dirname(os.path.dirname(__file__)) + f'/results/{scenario}_dc_curtailment_Winter_Weekend.csv']
    paths = [os.path.dirname(os.path.dirname(__file__)) + f'/results/{file}' for file in csv_files if
             scenario.replace('_hourly', "") in file and 'hourly' in file and 'dc_curtailment' in file][:4]
    Plots.plot_dc_curtailment_from_csv(paths, save_path=os.path.dirname(__file__) + f'/{scenario}')

# # Scenario 16
# paths = [os.path.dirname(os.path.dirname(__file__)) + '/results/load_pv_battery_time_of_use_v2g_inv_con_voltages_Summer_Weekday.csv',
#          os.path.dirname(os.path.dirname(__file__)) + '/results/load_pv_battery_time_of_use_v2g_inv_con_voltages_Summer_Weekend.csv',
#          os.path.dirname(os.path.dirname(__file__)) + '/results/load_pv_battery_time_of_use_v2g_inv_con_voltages_Winter_Weekday.csv',
#          os.path.dirname(os.path.dirname(__file__)) + '/results/load_pv_battery_time_of_use_v2g_inv_con_voltages_Winter_Weekend.csv']
# Plots.plot_voltages_from_csv(paths, save_path=os.path.dirname(__file__) + '/load_pv_battery_time_of_use_v2g_inv_con')
#
# paths = [os.path.dirname(os.path.dirname(__file__)) + '/results/load_pv_battery_time_of_use_v2g_inv_con_line_currents_Summer_Weekday.csv',
#          os.path.dirname(os.path.dirname(__file__)) + '/results/load_pv_battery_time_of_use_v2g_inv_con_line_currents_Summer_Weekend.csv',
#          os.path.dirname(os.path.dirname(__file__)) + '/results/load_pv_battery_time_of_use_v2g_inv_con_line_currents_Winter_Weekday.csv',
#          os.path.dirname(os.path.dirname(__file__)) + '/results/load_pv_battery_time_of_use_v2g_inv_con_line_currents_Winter_Weekend.csv']
# Plots.plot_currents_from_csv(paths, save_path=os.path.dirname(__file__) + '/load_pv_battery_time_of_use_v2g_inv_con')
#
# paths = [os.path.dirname(os.path.dirname(__file__)) + '/results/load_pv_battery_time_of_use_v2g_inv_con_voltage_unbalance_Summer_Weekday.csv',
#          os.path.dirname(os.path.dirname(__file__)) + '/results/load_pv_battery_time_of_use_v2g_inv_con_voltage_unbalance_Summer_Weekend.csv',
#          os.path.dirname(os.path.dirname(__file__)) + '/results/load_pv_battery_time_of_use_v2g_inv_con_voltage_unbalance_Winter_Weekday.csv',
#          os.path.dirname(os.path.dirname(__file__)) + '/results/load_pv_battery_time_of_use_v2g_inv_con_voltage_unbalance_Winter_Weekend.csv']
# Plots.plot_voltage_unbalance_from_csv(paths, save_path=os.path.dirname(__file__) + '/load_pv_battery_time_of_use_v2g_inv_con')

# # # # Weather Plots
# Plots.plot_irradiance_from_csv(os.path.dirname(os.path.dirname(__file__)) + '/results/', os.path.dirname(__file__))
# Plots.plot_temperature_from_csv(os.path.dirname(os.path.dirname(__file__)) + '/results/', os.path.dirname(__file__))
