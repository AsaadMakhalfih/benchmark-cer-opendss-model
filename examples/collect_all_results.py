import pandas as pd
import os

# import example_load

# import example_load_pv
# import example_load_pv_inv_con
# import example_load_pv_export_limit
#
# import example_load_pv_battery_self_consumption_export_limit
# import example_load_pv_battery_self_consumption_inv_con
#
# import example_load_pv_battery_time_of_use_inv_con
# import example_load_pv_battery_time_of_use_export_limit
#
# import example_load_pv_battery_self_consumption_managed_export_limit
# import example_load_pv_battery_self_consumption_managed_inv_con
# import example_load_pv_battery_time_of_use_managed_export_limit
# import example_load_pv_battery_time_of_use_managed_inv_con

# import example_load_pv_battery_self_consumption_unmanaged_export_limit
# import example_load_pv_battery_self_consumption_unmanaged_inv_con
# import example_load_pv_battery_time_of_use_unmanaged_export_limit
# import example_load_pv_battery_time_of_use_unmanaged_inv_con

# import example_load_pv_battery_self_consumption_v2g_export_limit
# import example_load_pv_battery_self_consumption_v2g_inv_con
# import example_load_pv_battery_time_of_use_v2g_export_limit
# import example_load_pv_battery_time_of_use_v2g_inv_con


import example_load_hourly

import example_load_pv_hourly
import example_load_pv_inv_con_hourly
import example_load_pv_export_limit_hourly

import example_load_pv_battery_self_consumption_export_limit_hourly
import example_load_pv_battery_self_consumption_inv_con_hourly

import example_load_pv_battery_time_of_use_inv_con_hourly
import example_load_pv_battery_time_of_use_export_limit_hourly

import example_load_pv_battery_self_consumption_managed_export_limit_hourly
import example_load_pv_battery_self_consumption_managed_inv_con_hourly
import example_load_pv_battery_time_of_use_managed_export_limit_hourly
import example_load_pv_battery_time_of_use_managed_inv_con_hourly

# import example_load_pv_battery_self_consumption_unmanaged_export_limit
# import example_load_pv_battery_self_consumption_unmanaged_inv_con
# import example_load_pv_battery_time_of_use_unmanaged_export_limit
# import example_load_pv_battery_time_of_use_unmanaged_inv_con

import example_load_pv_battery_self_consumption_v2g_export_limit_hourly
import example_load_pv_battery_self_consumption_v2g_inv_con_hourly
import example_load_pv_battery_time_of_use_v2g_export_limit_hourly
import example_load_pv_battery_time_of_use_v2g_inv_con_hourly

# folders = ['Case_Load_PV', 'Case_Load_PV_Static_Export_Limit', 'Case_Load_PV_Inv_Control', 'Case_Load_PV_Static_Export_Limit_Battery_Time_Of_Use',
# 'Case_Load_PV_Inv_Control_Battery_Time_Of_Use', 'Case_Load_PV_Static_Export_Limit_Battery_Max_Self_Consumption', 'Case_Load_PV_Inv_Control_Battery_Max_Self_Consumption',
# 'Case_Load_PV_Static_Export_Limit_Battery_Time_Of_Use_EV_Unmanaged_Charging', 'Case_Load_PV_Inv_Control_Battery_Time_Of_Use_EV_Unmanaged_Charging',
# 'Case_Load_PV_Static_Export_Limit_Battery_Max_Self_Consumption_EV_Unmanaged_Charging', 'Case_Load_PV_Inv_Control_Battery_Max_Self_Consumption_EV_Unmanaged_Charging',
# 'Case_Load_PV_Static_Export_Limit_Battery_Time_Of_Use_EV_Managed_Charging', 'Case_Load_PV_Inv_Control_Battery_Time_Of_Use_EV_Managed_Charging',
# 'Case_Load_PV_Static_Export_Limit_Battery_Max_Self_Consumption_EV_Managed_Charging', 'Case_Load_PV_Inv_Control_Battery_Max_Self_Consumption_EV_Managed_Charging',
# 'Case_Load_PV_Static_Export_Limit_Battery_Time_Of_Use_EV_V2G_Charging', 'Case_Load_PV_Inv_Control_Battery_Time_Of_Use_EV_V2G_Charging',
# 'Case_Load_PV_Static_Export_Limit_Battery_Max_Self_Consumption_EV_V2G_Charging', 'Case_Load_PV_Inv_Control_Battery_Max_Self_Consumption_EV_V2G_Charging']
# cases = ['baseline', 'load_pv', 'load_pv_export_limit', 'load_pv_battery_self_consumption_export_limit', 'load_pv_battery_time_of_use_export_limit',
#          'load_pv_battery_self_consumption_managed_export_limit', 'load_pv_battery_self_consumption_v2g_export_limit', 'load_pv_battery_time_of_use_managed_export_limit',
#          'load_pv_battery_time_of_use_v2g_export_limit', 'load_pv_inv_con', 'load_pv_battery_self_consumption_inv_con', 'load_pv_battery_time_of_use_inv_con',
#          'load_pv_battery_self_consumption_managed_inv_con', 'load_pv_battery_self_consumption_v2g_inv_con', 'load_pv_battery_time_of_use_managed_inv_con',
#          'load_pv_battery_time_of_use_v2g_inv_con']

cases = ['baseline_hourly', 'load_pv_only_hourly', 'load_pv_export_limit_hourly', 'load_pv_battery_self_consumption_export_limit_hourly', 'load_pv_battery_time_of_use_export_limit_hourly',
         'load_pv_battery_self_consumption_managed_export_limit_hourly', 'load_pv_battery_self_consumption_v2g_export_limit_hourly', 'load_pv_battery_time_of_use_managed_export_limit_hourly',
         'load_pv_battery_time_of_use_v2g_export_limit_hourly', 'load_pv_inv_con_hourly', 'load_pv_battery_self_consumption_inv_con_hourly', 'load_pv_battery_time_of_use_inv_con_hourly',
         'load_pv_battery_self_consumption_managed_inv_con_hourly', 'load_pv_battery_self_consumption_v2g_inv_con_hourly', 'load_pv_battery_time_of_use_managed_inv_con_hourly',
         'load_pv_battery_time_of_use_v2g_inv_con_hourly']
#
# , 'load_pv_battery_self_consumption_unmanaged_inv_con',
#       'load_pv_battery_time_of_use_unmanaged_inv_con',
#
#       'load_pv_battery_self_consumption_unmanaged_export_limit',
#       'load_pv_battery_time_of_use_unmanaged_export_limit'
#      ]

days_scenario = ['Summer_Weekday', 'Summer_Weekend', 'Winter_Weekday', 'Winter_Weekend']
output_path = os.path.join(os.path.dirname(__file__), "ALL_RESULTS_HOURLY.xlsx")

# Open the Excel writer once, so that all sheets are saved in the same workbook.
with pd.ExcelWriter(output_path, mode='w', engine='openpyxl') as writer:
    for day in days_scenario:
        results = {
            "Case": [],
            "PV dc-generation (kWh)": [],
            "Battery stored energy (kWh)": [],
            "EV stored energy (kWh)": [],
            "Potential inverter ac output (kWh)": [],
            "Actual inverter ac output (kWh)": [],
            "Total pv to battery (kWh)": [],
            "Total inverter to load (kWh)": [],
            "Total inverter to ev (kWh)": [],
            "Total inverter to grid (kWh)": [],
            "Total ev to load (kWh)": [],
            "Total ev to grid (kWh)": [],
            "Total grid to load (kWh)": [],
            "Total grid to ev (kWh)": [],
            "Total dc curtailment (kWh)": [],
            "Total ac curtailment (kWh)": [],
            "Total curtailment (kWh)": [],
            "Total dc curtailment (%)": [],
            "Total ac curtailment (%)": [],
            "Total curtailment (%)": [],
            "Active System Losses (kWh)": [],
            "Reactive System Losses (kVArh)": [],
            'Fairness Index (%)': [],
            'Simulation Time (Sec)': []
        }
        # Loop through each case folder, creating a new folder name for this day scenario.
        for folder in cases:
            if 'baseline' in folder:
                continue
            folder_name = f"{folder}_{day}"
            # Read the CSV for the given folder name.
            file_path = os.path.join(os.path.dirname(__file__), f"results/{folder_name}.csv")
            sub_results = pd.read_csv(file_path)
            results["Case"].append(folder_name)
            results["PV dc-generation (kWh)"].append(sub_results["PV dc-generation (kWh)"].values[0])
            results["Battery stored energy (kWh)"].append(sub_results["Battery stored energy (kWh)"].values[0])
            results["EV stored energy (kWh)"].append(sub_results["EV stored energy (kWh)"].values[0])
            results["Potential inverter ac output (kWh)"].append(sub_results["Potential inverter ac output (kWh)"].values[0])
            results["Actual inverter ac output (kWh)"].append(sub_results["Actual inverter ac output (kWh)"].values[0])
            results["Total pv to battery (kWh)"].append(sub_results["Total pv to battery (kWh)"].values[0])
            results["Total inverter to load (kWh)"].append(sub_results["Total inverter to load (kWh)"].values[0])
            results["Total inverter to ev (kWh)"].append(sub_results["Total inverter to ev (kWh)"].values[0])
            results["Total inverter to grid (kWh)"].append(sub_results["Total inverter to grid (kWh)"].values[0])
            results["Total ev to load (kWh)"].append(sub_results["Total ev to load (kWh)"].values[0])
            results["Total ev to grid (kWh)"].append(sub_results["Total ev to grid (kWh)"].values[0])
            results["Total grid to load (kWh)"].append(sub_results["Total grid to load (kWh)"].values[0])
            results["Total grid to ev (kWh)"].append(sub_results["Total grid to ev (kWh)"].values[0])
            results["Total dc curtailment (kWh)"].append(sub_results["Total dc curtailment (kWh)"].values[0])
            results["Total ac curtailment (kWh)"].append(sub_results["Total ac curtailment (kWh)"].values[0])
            results["Total curtailment (kWh)"].append(sub_results["Total curtailment (kWh)"].values[0])
            results["Total dc curtailment (%)"].append(sub_results["Total dc curtailment (%)"].values[0])
            results["Total ac curtailment (%)"].append(sub_results["Total ac curtailment (%)"].values[0])
            results["Total curtailment (%)"].append(sub_results["Total curtailment (%)"].values[0])
            results["Active System Losses (kWh)"].append(sub_results["Active System Losses (kWh)"].values[0])
            results["Reactive System Losses (kVArh)"].append(sub_results["Reactive System Losses (kVArh)"].values[0])
            results["Fairness Index (%)"].append(sub_results["Fairness Index (%)"].values[0])
            results["Simulation Time (Sec)"].append(sub_results["Simulation Time (Sec)"].values[0])

        summary_df = pd.DataFrame(results)
        # Write this DataFrame to a sheet named after the day scenario.
        summary_df.to_excel(writer, sheet_name=day, index=False)

output_path = os.path.join(os.path.dirname(__file__), "ALL_METRICS_HOURLY.xlsx")

# Open the Excel writer once, so that all sheets are saved in the same workbook.
with pd.ExcelWriter(output_path, mode='w', engine='openpyxl') as writer:
    for day in days_scenario:
        results = {
            "Case": [],
            "Metric 1.a": [],
            "Metric 1.b": [],
            # "Metric 2": [],
            # "Metric 3": [],
            # "Metric 4": [],
            "Metric 5.a": [],
            "Metric 5.b": []
        }
        # Loop through each case folder, creating a new folder name for this day scenario.
        for folder in cases:
            folder_name = f"{folder.replace('_hourly', '')}_metrics_{day}"
            if 'hourly' in folder:
                files = os.listdir(os.path.dirname(__file__) + "/results")
                print(files)
                file_path = [os.path.dirname(__file__) + f"/results/{file}" for file in files if folder.replace("_hourly", "") in file and "metrics" in file and "hourly" in file and day in file][0]
                print(file_path)
            # Read the CSV for the given folder name.
            # file_path = os.path.join(os.path.dirname(__file__), f"results/{folder_name}.csv")
            sub_results = pd.read_csv(file_path)
            results["Case"].append(folder_name)
            results["Metric 1.a"].append(sub_results["Metric 1.a"].values[0])
            results["Metric 1.b"].append(sub_results["Metric 1.b"].values[0])
            # results["Metric 2"].append(sub_results["Metric 2"].values[0])
            # results["Metric 3"].append(sub_results["Metric 3"].values[0])
            # results["Metric 4"].append(sub_results["Metric 4"].values[0])
            results["Metric 5.a"].append(sub_results["Metric 5.a"].values[0])
            results["Metric 5.b"].append(sub_results["Metric 5.b"].values[0])

        summary_df = pd.DataFrame(results)
        # Write this DataFrame to a sheet named after the day scenario.
        summary_df.to_excel(writer, sheet_name=day, index=False)
