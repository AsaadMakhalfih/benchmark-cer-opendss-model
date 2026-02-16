from src.results import Results
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import pandas as pd
import numpy as np
import os
from pathlib import Path


class Plots:
    width_cm = 15.9
    height_cm = 5
    width_in = width_cm / 2.54
    height_in = height_cm / 2.54

    @classmethod
    def plot_voltages_whisker_plots(cls, save_dir=None, extra_disc=''):
        if save_dir is not None:
            os.makedirs(save_dir, exist_ok=True)
            phase_a_path = os.path.join(save_dir, f'voltage_phase_a{extra_disc}.svg')
            phase_b_path = os.path.join(save_dir, f'voltage_phase_b{extra_disc}.svg')
            phase_c_path = os.path.join(save_dir, f'voltage_phase_c{extra_disc}.svg')
            cls._plot_voltages_whisker_plots_phase_a(save_path=phase_a_path)
            cls._plot_voltages_whisker_plots_phase_b(save_path=phase_b_path)
            cls._plot_voltages_whisker_plots_phase_c(save_path=phase_c_path)
        else:
            cls._plot_voltages_whisker_plots_phase_a()
            cls._plot_voltages_whisker_plots_phase_b()
            cls._plot_voltages_whisker_plots_phase_c()

    @classmethod
    def plot_line_currents_whisker_plots(cls, save_dir=None, extra_disc=''):
        if save_dir is not None:
            os.makedirs(save_dir, exist_ok=True)
            phase_a_path = os.path.join(save_dir, f'currents_phase_a{extra_disc}.svg')
            phase_b_path = os.path.join(save_dir, f'currents_phase_b{extra_disc}.svg')
            phase_c_path = os.path.join(save_dir, f'currents_phase_c{extra_disc}.svg')
            cls._plot_line_currents_whisker_plot_phase_a(save_path=phase_a_path)
            cls._plot_line_currents_whisker_plot_phase_b(save_path=phase_b_path)
            cls._plot_line_currents_whisker_plot_phase_c(save_path=phase_c_path)
        else:
            cls._plot_line_currents_whisker_plot_phase_a()
            cls._plot_line_currents_whisker_plot_phase_b()
            cls._plot_line_currents_whisker_plot_phase_c()

    @classmethod
    def plot_vuf_whisker_plots(cls, save_path=None):
        voltages = Results.VOLTAGE_UNBALANCE_HISTORY
        columns = list(voltages.keys())
        data = list(voltages.values())
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.boxplot(data, labels=columns, patch_artist=True, showfliers=False)
        ax.axhline(2, color='red')
        ax.set_title(' ')
        ax.set_xlabel('Buses', fontsize=10)
        ax.tick_params(axis='x', labelrotation=-90)
        ax.set_ylabel("VUF(%)")
        ax.set_ylim(bottom=0)
        fig.tight_layout()
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    @classmethod
    def _plot_line_currents_whisker_plot_phase_a(cls, save_path=None):
        currents = Results.LINE_CURRENT_A
        columns = list(currents.keys())
        data = list((currents.values()))
        fig9, ax9 = plt.subplots(figsize=(10, 2))
        ax9.boxplot(data, labels=columns, patch_artist=True, showfliers=False)
        ax9.set_title('Phase A')
        ax9.set_xlabel('Lines', fontsize=10)
        ax9.tick_params(axis='x', labelrotation=-90, labelsize=6)
        ax9.set_ylabel("Current (%)")
        ax9.axhline(100, color='red')
        ax9.axhline(0, color='red')
        fig9.tight_layout()
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    @classmethod
    def _plot_line_currents_whisker_plot_phase_b(cls, save_path=None):
        currents = Results.LINE_CURRENT_B
        columns = list(currents.keys())
        data = list((currents.values()))
        fig9, ax9 = plt.subplots(figsize=(10, 2))
        ax9.boxplot(data, labels=columns, patch_artist=True, showfliers=False)
        ax9.set_title('Phase B')
        ax9.set_xlabel('Lines', fontsize=10)
        ax9.tick_params(axis='x', labelrotation=-90, labelsize=6)
        ax9.set_ylabel("Current (%)")
        ax9.axhline(100, color='red')
        ax9.axhline(0, color='red')
        fig9.tight_layout()
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    @classmethod
    def _plot_line_currents_whisker_plot_phase_c(cls, save_path=None):
        currents = Results.LINE_CURRENT_C
        columns = list(currents.keys())
        data = list((currents.values()))
        fig9, ax9 = plt.subplots(figsize=(10, 2))
        ax9.boxplot(data, labels=columns, patch_artist=True, showfliers=False)
        ax9.set_title('Phase C')
        ax9.set_xlabel('Lines', fontsize=10)
        ax9.tick_params(axis='x', labelrotation=-90, labelsize=6)
        ax9.set_ylabel("Current (%)")
        ax9.axhline(100, color='red')
        ax9.axhline(0, color='red')
        fig9.tight_layout()
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    @classmethod
    def plot_ac_curtailment_bar_plots(cls, save_path=None):
        pv_a = list(Results.AC_CURTAILMENT_A.keys())
        pv_b = list(Results.AC_CURTAILMENT_B.keys())
        pv_c = list(Results.AC_CURTAILMENT_C.keys())

        data_a = [sum(Results.AC_CURTAILMENT_A[pv]) * 0.5 for pv in pv_a]
        data_b = [sum(Results.AC_CURTAILMENT_B[pv]) * 0.5 for pv in pv_b]
        data_c = [sum(Results.AC_CURTAILMENT_C[pv]) * 0.5 for pv in pv_c]

        fig6, axes = plt.subplots(1, 3, figsize=(12, 6))
        axes[0].barh(range(len(data_a)), data_a, color='skyblue', edgecolor='black')
        axes[0].set_title('Phase A')
        axes[0].set_xlabel('Curtailment (kWh)')
        axes[0].set_yticks(range(len(pv_a)))
        axes[0].set_yticklabels(pv_a, fontsize=7)
        axes[1].barh(range(len(data_b)), data_b, color='salmon', edgecolor='black')
        axes[1].set_title('Phase B')
        axes[1].set_yticks(range(len(pv_b)))
        axes[1].set_yticklabels(pv_b, fontsize=7)
        axes[2].barh(range(len(data_c)), data_c, color='lightgreen', edgecolor='black')
        axes[2].set_title('Phase C')
        axes[2].set_yticks(range(len(pv_c)))
        axes[2].set_yticklabels(pv_c, fontsize=7)
        fig6.tight_layout()
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    @classmethod
    def plot_dc_curtailment_bar_plots(cls, save_path=None):
        pv_a = list(Results.DC_CURTAILMENT_A.keys())
        pv_b = list(Results.DC_CURTAILMENT_B.keys())
        pv_c = list(Results.DC_CURTAILMENT_C.keys())

        data_a = [sum(Results.DC_CURTAILMENT_A[pv]) * 0.5 for pv in pv_a]
        data_b = [sum(Results.DC_CURTAILMENT_B[pv]) * 0.5 for pv in pv_b]
        data_c = [sum(Results.DC_CURTAILMENT_C[pv]) * 0.5 for pv in pv_c]

        fig6, axes = plt.subplots(1, 3, figsize=(12, 6))
        axes[0].barh(range(len(data_a)), data_a, color='skyblue', edgecolor='black')
        axes[0].set_title('Phase A')
        axes[0].set_yticks(range(len(pv_a)))
        axes[0].set_yticklabels(pv_a, fontsize=7)
        axes[1].barh(range(len(data_b)), data_b, color='salmon', edgecolor='black')
        axes[1].set_title('Phase B')
        axes[1].set_yticks(range(len(pv_b)))
        axes[1].set_yticklabels(pv_b, fontsize=7)
        axes[2].barh(range(len(data_c)), data_c, color='lightgreen', edgecolor='black')
        axes[2].set_title('Phase C')
        axes[2].set_yticks(range(len(pv_c)))
        axes[2].set_yticklabels(pv_c, fontsize=7)
        fig6.tight_layout()
        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()

    @classmethod
    def _plot_voltages_whisker_plots_phase_a(cls, save_path=None):
        voltages = Results.VOLTAGE_HISTORY_A
        columns = list(voltages.keys())
        data = list(voltages.values())
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.boxplot(data, labels=columns, patch_artist=True, showfliers=False)
        ax.set_title('Phase A')
        ax.set_xlabel('Buses', fontsize=10)
        ax.tick_params(axis='x', labelrotation=-90)
        ax.set_ylabel("Voltage (p.u)")
        ax.axhline(1.1, color='red')
        ax.axhline(0.90, color='red')
        fig.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    @classmethod
    def _plot_voltages_whisker_plots_phase_b(cls, save_path=None):
        voltages = Results.VOLTAGE_HISTORY_B
        columns = list(voltages.keys())
        data = list(voltages.values())
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.boxplot(data, labels=columns, patch_artist=True, showfliers=False)
        ax.set_title('Phase B')
        ax.set_xlabel('Buses', fontsize=10)
        ax.tick_params(axis='x', labelrotation=-90)
        ax.set_ylabel("Voltage (p.u)")
        ax.axhline(1.1, color='red')
        ax.axhline(0.90, color='red')
        fig.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    @classmethod
    def _plot_voltages_whisker_plots_phase_c(cls, save_path=None):
        voltages = Results.VOLTAGE_HISTORY_C
        columns = list(voltages.keys())
        data = list(voltages.values())
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.boxplot(data, labels=columns, patch_artist=True, showfliers=False)
        ax.set_title('Phase C')
        ax.set_xlabel('Buses', fontsize=10)
        ax.tick_params(axis='x', labelrotation=-90)
        ax.set_ylabel("Voltage (p.u)")
        ax.axhline(1.1, color='red')
        ax.axhline(0.90, color='red')
        fig.tight_layout()
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    @classmethod
    def plot_and_save_all(cls, path, extra_disc=''):
        os.makedirs(path, exist_ok=True)
        # Save voltage phases
        cls.plot_voltages_whisker_plots(save_dir=path, extra_disc=extra_disc)
        # Save VUF
        cls.plot_vuf_whisker_plots(save_path=os.path.join(path, f'vuf_whisker{extra_disc}.svg'))
        # Save line currents Phase A
        cls.plot_line_currents_whisker_plots(save_dir=path, extra_disc=extra_disc)
        # Save AC curtailment
        cls.plot_ac_curtailment_bar_plots(save_path=os.path.join(path, f'ac_curtailment{extra_disc}.svg'))
        # Save DC curtailment
        cls.plot_dc_curtailment_bar_plots(save_path=os.path.join(path, f'dc_curtailment{extra_disc}.svg'))

    # @classmethod
    # def plot_from_csv(cls, csv_path, plot_type='voltage', save_path=None):
    #     """Generic plotting method for CSV data with temporal dimensions"""
    #
    #     # Load data and parse timestamps
    #     df = pd.read_csv(csv_path)
    #     df['Datetime'] = pd.to_datetime(df['Time'], format='%H: %M')  # Adapt format as needed
    #     df['Day'] = (df.index // (1440 / Results.STEP_SIZE)).astype(int) + 1  # Calculate day number
    #
    #     fig, axs = plt.subplots(3, 1, figsize=(14, 10)) if plot_type != 'unbalance' else plt.subplots(1, 1, figsize=(14, 4))
    #     phases = ['A', 'B', 'C'] if plot_type != 'unbalance' else ['']
    #
    #     for phase_idx, phase in enumerate(phases):
    #         ax = axs[phase_idx] if plot_type != 'unbalance' else axs
    #         phase_data = df.filter(regex=f'.{phase_idx + 1}$' if plot_type != 'unbalance' else '')
    #
    #         # Prepare data structure for boxplots
    #         plot_data = []
    #         positions = []
    #         day_labels = []
    #         colors = plt.cm.viridis(np.linspace(0, 1, df['Day'].nunique()))
    #
    #         # Organize data by bus/line and day
    #         for col_idx, col in enumerate(phase_data.columns):
    #             if col == 'Time': continue
    #             base_name = col.split('.')[0]
    #             for day in sorted(df['Day'].unique()):
    #                 day_data = phase_data[col][df['Day'] == day].values
    #                 plot_data.append(day_data)
    #                 positions.append(col_idx + (day - 1) * 0.2)
    #                 day_labels.append(f'Day {day}')
    #
    #         # Create boxplots
    #         bp = ax.boxplot(plot_data, positions=positions, widths=0.15, patch_artist=True, showfliers=False)
    #
    #         # Color coding for days
    #         for patch, pos in zip(bp['boxes'], positions):
    #             patch.set_facecolor(colors[int((pos % 1) * 5)])
    #
    #         # Plot formatting
    #         if plot_type == 'voltage':
    #             ax.axhline(1.1, color='r', linestyle='--', alpha=0.7)
    #             ax.axhline(0.9, color='r', linestyle='--', alpha=0.7)
    #             ax.set_ylim(0.85, 1.15)
    #
    #         # X-axis configuration
    #         tick_positions = np.arange(len(phase_data.columns)) + 0.3
    #         ax.set_xticks(tick_positions)
    #         ax.set_xticklabels([col.split('.')[0] for col in phase_data.columns], rotation=90)
    #
    #         if plot_type != 'unbalance':
    #             ax.set_title(f'Phase {phase}', fontsize=10)
    #             ax.set_ylabel('Voltage (p.u)' if plot_type == 'voltage' else 'Current (%)')
    #
    #     # Create unified legend
    #     legend_elements = [Patch(facecolor=colors[i], label=f'Day {i + 1}')
    #                        for i in range(df['Day'].nunique())]
    #     fig.legend(handles=legend_elements, loc='upper right', title='Days')
    #
    #     plt.tight_layout()
    #     if save_path:
    #         plt.savefig(save_path, bbox_inches='tight')
    #         plt.close()
    #     else:
    #         plt.show()

    @classmethod
    def plot_voltage_scenario_envelopes(cls, base_dir, scenarios, days=['Summer_Weekday', 'Summer_Weekend', 'Winter_Weekday', 'Winter_Weekend'], save_path=None):
        """
        For each scenario in `scenarios`, read the 4 daily CSV files and plot the voltage envelopes (max/min across buses).
        """
        fig, axs = plt.subplots(2, 3, figsize=(12, 6))  # 2 rows x 3 columns
        plt.subplots_adjust(
            top=0.9,  # leave space at top
            bottom=0.1,  # space at bottom
            left=0.07,  # margins
            right=0.97,
            hspace=0.4,  # vertical spacing between subplots
            wspace=0.3  # horizontal spacing
        )
        axs = axs.flatten()

        if len(scenarios) == 1:  # If only one scenario, axs is not iterable
            axs = [axs]
        scenarios_titles = ['BAU (Sc.1)', 'Max. Allowable PV (Sc.2)', '100% PV with Export Limit (Sc.3)', '100% PV with Voltage Response (Sc.10)',
                            '100% PV and 15% Battery \n with TOU and Voltage Response (Sc.12)', '100% PV, 15% Battery and 30% EV \n with TOU, V2G and Voltage Response (Sc.16)']
        for idx, scenario in enumerate(scenarios):
            # Find CSV files for the scenario
            csv_files = [base_dir + f'/results/{scenario}_voltages_{day}.csv' for day in days]
            if 'hourly' in scenario:
                files = os.listdir(base_dir + "/results")
                print(files)
                csv_files = [base_dir + f"/results/{file}" for file in files if scenario.replace("_hourly", "") in file and "voltages" in file and "hourly" in file]
                print(csv_files)
            # Read and combine data
            day_data = [pd.read_csv(f).set_index('Time') for f in csv_files]
            nodes = list(pd.read_csv(csv_files[0]).columns)[1:56]
            all_data = pd.concat(day_data, keys=days, names=['Day', 'Time'])
            # Compute envelope per time step (across all buses)
            voltages_only = all_data.drop(columns=['Day'], errors='ignore') if 'Day' in all_data.columns else all_data
            bus_names = [node.split('.')[0] for node in nodes]
            voltages_only.columns = bus_names * 3  # rename columns by bus

            # Now group columns by bus and compute min/max
            v_max_per_bus = voltages_only.groupby(axis=1, level=0).max()  # max across phases
            v_min_per_bus = voltages_only.groupby(axis=1, level=0).min()
            v_max_per_bus = v_max_per_bus[bus_names]
            v_min_per_bus = v_min_per_bus[bus_names]
            v_max = v_max_per_bus.groupby(level='Time').max().max(axis=0)
            v_min = v_min_per_bus.groupby(level='Time').min().min(axis=0)

            # Plot envelopes
            ax = axs[idx]
            ax.fill_between(v_max.index, v_min.values, v_max.values, alpha=0.3)
            ax.plot(v_max.index, v_max.values, color='magenta', lw=0.8, label='Max Values')
            ax.plot(v_min.index, v_min.values, color='orange', lw=0.8, label='Min Values')

            # Horizontal limits
            ax.axhline(1.1, color='r', linestyle='--', lw=0.8, label='Max limit')
            ax.axhline(0.9, color='b', linestyle='--', lw=0.8, label='Min limit')

            # ax.set_title(scenario.replace('_', ' ').title(), fontsize=10)
            ax.set_title(scenarios_titles[idx], fontsize=9, weight='bold')
            if idx == 0 or idx == 3:
                ax.set_ylabel('Voltage (p.u)')
            ax.set_xlabel(r'Bus $\rightarrow$ Distance from Source')
            ax.set_xticks([])
            # ax.tick_params(axis='x', labelsize=4)
            ax.grid(True, alpha=0.3)

        fig.subplots_adjust(bottom=0.05, top=0.90)
        # Unified legend
        handles, labels = axs[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.01), ncol=4, frameon=False, fontsize=10)

        # plt.tight_layout(rect=[0, 0.05, 1, 1])

        if save_path:
            plt.savefig(save_path + r'\all_voltages.pdf', bbox_inches='tight')
        else:
            plt.show()

    @classmethod
    def plot_voltage_unbalance_scenario_envelopes(cls, base_dir, scenarios, days=['Summer_Weekday', 'Summer_Weekend', 'Winter_Weekday', 'Winter_Weekend'], save_path=None):
        """
        For each scenario in `scenarios`, read the 4 daily CSV files and plot the voltage envelopes (max/min across buses).
        """
        fig, axs = plt.subplots(2, 3, figsize=(12, 6))  # 2 rows x 3 columns
        plt.subplots_adjust(
            top=0.9,  # leave space at top
            bottom=0.1,  # space at bottom
            left=0.07,  # margins
            right=0.97,
            hspace=0.4,  # vertical spacing between subplots
            wspace=0.3  # horizontal spacing
        )
        axs = axs.flatten()

        if len(scenarios) == 1:  # If only one scenario, axs is not iterable
            axs = [axs]
        scenarios_titles = ['BAU (Sc.1)', 'Max. Allowable PV (Sc.2)', '100% PV with Export Limit (Sc.3)', '100% PV with Voltage Response (Sc.10)',
                            '100% PV and 15% Battery \n with TOU and Voltage Response (Sc.12)', '100% PV, 15% Battery and 30% EV \n with TOU, V2G and Voltage Response (Sc.16)']
        for idx, scenario in enumerate(scenarios):
            # Find CSV files for the scenario
            csv_files = [base_dir + f'/results/{scenario}_voltage_unbalance_{day}.csv' for day in days]
            if 'hourly' in scenario:
                files = os.listdir(base_dir + "/results")
                csv_files = [base_dir + f"/results/{file}" for file in files if scenario.replace("_hourly", "") in file and "voltage_unbalance" in file and "hourly" in file]

            # Read and combine data
            day_data = [pd.read_csv(f).set_index('Time') for f in csv_files]
            nodes = list(pd.read_csv(csv_files[0]).columns)
            all_data = pd.concat(day_data, keys=days, names=['Day', 'Time'])
            # Compute envelope per time step (across all buses)
            voltages_only = all_data.drop(columns=['Day'], errors='ignore') if 'Day' in all_data.columns else all_data
            bus_names = [node.split('.')[0] for node in nodes][1:]
            voltages_only.columns = bus_names  # rename columns by bus

            # Now group columns by bus and compute min/max
            v_max_per_bus = voltages_only.groupby(axis=1, level=0).max()  # max across phases
            v_min_per_bus = voltages_only.groupby(axis=1, level=0).min()
            v_max_per_bus = v_max_per_bus[bus_names]
            v_min_per_bus = v_min_per_bus[bus_names]
            v_max = v_max_per_bus.groupby(level='Time').max().max(axis=1)
            v_min = v_min_per_bus.groupby(level='Time').min().min(axis=1)

            # Plot envelopes
            ax = axs[idx]
            ax.fill_between(v_max.index, v_min.values, v_max.values, alpha=0.3)
            ax.plot(v_max.index, v_max.values, color='magenta', lw=0.8, label='Max Values')
            ax.plot(v_min.index, v_min.values, color='orange', lw=0.8, label='Min Values')

            # Horizontal limits
            ax.axhline(2, color='r', linestyle='--', lw=0.8, label='Max limit')

            # ax.set_title(scenario.replace('_', ' ').title(), fontsize=10)
            ax.set_title(scenarios_titles[idx], fontsize=9, weight='bold')
            if idx == 0 or idx == 3:
                ax.set_ylabel('VUF (%)')
            ax.set_xlabel(r'Day Time $\rightarrow$')
            ax.set_xticks([])
            # ax.tick_params(axis='x', labelsize=4)
            ax.grid(True, alpha=0.3)

        fig.subplots_adjust(bottom=0.05, top=0.90)
        # Unified legend
        handles, labels = axs[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.01), ncol=4, frameon=False, fontsize=10)

        # plt.tight_layout(rect=[0, 0.05, 1, 1])

        if save_path:
            plt.savefig(save_path + r'\all_voltage_unbalance.pdf', bbox_inches='tight')
        else:
            plt.show()

    @classmethod
    def plot_line_current_envelopes(cls, base_dir, scenarios, days=['Summer_Weekday', 'Summer_Weekend', 'Winter_Weekday', 'Winter_Weekend'], save_path=None):
        """
        Plot line current envelopes (max/min across lines) for multiple scenarios.
        """
        fig, axs = plt.subplots(2, 3, figsize=(12, 6))  # 2 rows x 3 columns
        plt.subplots_adjust(
            top=0.9,  # leave space at top
            bottom=0.1,  # space at bottom
            left=0.07,  # margins
            right=0.97,
            hspace=0.4,  # vertical spacing between subplots
            wspace=0.3  # horizontal spacing
        )
        axs = axs.flatten()

        if len(scenarios) == 1:
            axs = [axs]

        scenarios_titles = ['BAU (Sc.1)', 'Max. Allowable PV (Sc.2)', '100% PV with Export Limit (Sc.3)', '100% PV with Voltage Response (Sc.10)',
                            '100% PV and 15% Battery \n with TOU and Voltage Response (Sc.12)', '100% PV, 15% Battery and 30% EV \n with TOU, V2G and Voltage Response (Sc.16)']
        for idx, scenario in enumerate(scenarios):
            # Read CSV files for this scenario
            csv_files = [base_dir + f'/results/{scenario}_line_currents_{day}.csv' for day in days]
            if 'hourly' in scenario:
                files = os.listdir(base_dir + "/results")
                csv_files = [base_dir + f"/results/{file}" for file in files if scenario.replace("_hourly", "") in file and "line_currents" in file and "hourly" in file]

            day_data = [pd.read_csv(f).set_index('Time') for f in csv_files]
            line_names = [col.split('.')[0] for col in pd.read_csv(csv_files[0]).columns[1:]][:116]  # skip Time
            all_data = pd.concat(day_data, keys=days, names=['Day', 'Time'])

            # Group by line and compute max/min across phases
            currents_only = all_data.drop(columns=['Day'], errors='ignore') if 'Day' in all_data.columns else all_data
            currents_only.columns = line_names * 3  # rename columns by line

            i_max_per_line = currents_only.groupby(axis=1, level=0).max()  # max across phases
            i_min_per_line = currents_only.groupby(axis=1, level=0).min()
            i_max_per_line = i_max_per_line[line_names]
            i_min_per_line = i_min_per_line[line_names]
            i_max = i_max_per_line.groupby(level='Time').max().max(axis=0)
            i_min = i_min_per_line.groupby(level='Time').min().min(axis=0)
            # Plot envelopes
            ax = axs[idx]
            ax.fill_between(range(len(line_names)), i_min.values, i_max.values, alpha=0.3)
            ax.plot(range(len(line_names)), i_max.values, color='magenta', lw=0.8, label='Max Currents')
            ax.plot(range(len(line_names)), i_min.values, color='orange', lw=0.8, label='Min Currents')

            # Horizontal reference line (e.g., 100% loading)
            ax.axhline(100, color='r', linestyle='--', lw=0.8, label='Max limit')

            ax.set_title(scenarios_titles[idx], fontsize=9, weight='bold')
            if idx == 0 or idx == 3:
                ax.set_ylabel('Line Loading (%)')
            ax.set_xlabel(r'Lines $\rightarrow$ Distance from Source')
            ax.set_xticks([])
            ax.grid(True, alpha=0.3)

        fig.subplots_adjust(bottom=0.05, top=0.90)

        # Unified legend
        handles, labels = axs[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.01), ncol=4, frameon=False, fontsize=10)

        if save_path:
            plt.savefig(save_path + r'\all_currents.pdf', bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    @classmethod
    def plot_ac_curtailment_total(cls, base_dir, scenarios, days=['Summer_Weekday', 'Summer_Weekend', 'Winter_Weekday', 'Winter_Weekend'], save_path=None):
        """
        Plot total AC curtailment per PV system for multiple scenarios, summing over time and phases.
        """
        fig, axs = plt.subplots(2, 3, figsize=(12, 6))  # 2 rows x 3 columns
        plt.subplots_adjust(
            top=0.9,  # leave space at top
            bottom=0.1,  # space at bottom
            left=0.07,  # margins
            right=0.97,
            hspace=0.4,  # vertical spacing between subplots
            wspace=0.3  # horizontal spacing
        )
        axs = axs.flatten()

        if len(scenarios) == 1:
            axs = [axs]

        scenarios_titles = ['BAU (Sc.1)', 'Max. Allowable PV (Sc.2)', '100% PV with Export Limit (Sc.3)', '100% PV with Voltage Response (Sc.10)',
                            '100% PV and 15% Battery \n with TOU and Voltage Response (Sc.12)', '100% PV, 15% Battery and 30% EV \n with TOU, V2G and Voltage Response (Sc.16)']
        for idx, scenario in enumerate(scenarios):
            if idx == 0:
                csv_files = [base_dir + f'/results/{scenarios[1]}_ac_curtailment_{day}.csv' for day in days]
                if 'hourly' in scenario:
                    files = os.listdir(base_dir + "/results")
                    csv_files = [base_dir + f"/results/{file}" for file in files if scenarios[1].replace("_hourly", "") in file and "ac_curtailment" in file and "hourly" in file]

            # Read CSV files for this scenario
            else:
                csv_files = [base_dir + f'/results/{scenario}_ac_curtailment_{day}.csv' for day in days]
                if 'hourly' in scenario:
                    files = os.listdir(base_dir + "/results")
                    csv_files = [base_dir + f"/results/{file}" for file in files if scenario.replace("_hourly", "") in file and "ac_curtailment" in file and "hourly" in file]

            day_data = [pd.read_csv(f).set_index('Time') for f in csv_files]

            # Get PV system names

            pv_systems = [col.split('.')[0] for col in day_data[0].columns]
            # Concatenate all days
            all_data = pd.concat(day_data, keys=days, names=['Day', 'Time'])

            # Remove 'Day' column if present
            data_only = all_data.drop(columns=['Day'], errors='ignore') if 'Day' in all_data.columns else all_data

            data_only.columns = pv_systems

            # Sum over time and phases and multiply by 0.5 to represent half-hour
            if 'hourly' in scenario:
                factor = 1
            else:
                factor = 0.5
            total_curtailment = data_only.groupby(level="Day").sum() * factor

            # Group by PV system (sum across phases)
            total_per_pv = total_curtailment.groupby(total_curtailment.index).max()
            # print(total_per_pv.loc["Summer_Weekday"])
            total_values = [total_per_pv.loc['Summer_Weekday'][pv] for pv in pv_systems][:55]

            # Plot
            ax = axs[idx]
            ax.bar(range(len(pv_systems[:55])), total_values, color='lightblue', edgecolor='k')
            ax.set_title(scenarios_titles[idx], fontsize=9, weight='bold')
            if idx == 0 or idx == 3:
                ax.set_ylabel('Total Curtailment (kWh)')
            ax.set_xlabel(r'PV Systems $\rightarrow$ Distance from Source')
            ax.set_xticks([])
            ax.grid(True, axis='y', alpha=0.3)

        fig.subplots_adjust(bottom=0.05, top=0.90)

        # Unified legend (single color bar)
        from matplotlib.patches import Patch
        handles = [Patch(facecolor='lightblue', edgecolor='k', label='Total AC Curtailment')]
        fig.legend(handles, [h.get_label() for h in handles], loc='upper center', bbox_to_anchor=(0.5, 1.01), ncol=1, frameon=False, fontsize=10)

        if save_path:
            plt.savefig(save_path + r'\all_ac_curtailment.pdf', bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    @classmethod
    def plot_dc_curtailment_total(cls, base_dir, scenarios, days=['Summer_Weekday', 'Summer_Weekend', 'Winter_Weekday', 'Winter_Weekend'], save_path=None):
        """
        Plot total DC curtailment per PV system for multiple scenarios, summing over time and phases.
        """
        fig, axs = plt.subplots(2, 3, figsize=(12, 6))  # 2 rows x 3 columns
        plt.subplots_adjust(
            top=0.9,  # leave space at top
            bottom=0.1,  # space at bottom
            left=0.07,  # margins
            right=0.97,
            hspace=0.4,  # vertical spacing between subplots
            wspace=0.3  # horizontal spacing
        )
        axs = axs.flatten()

        if len(scenarios) == 1:
            axs = [axs]

        scenarios_titles = ['BAU (Sc.1)', 'Max. Allowable PV (Sc.2)', '100% PV with Export Limit (Sc.3)', '100% PV with Voltage Response (Sc.10)',
                            '100% PV and 15% Battery \n with TOU and Voltage Response (Sc.12)', '100% PV, 15% Battery and 30% EV \n with TOU, V2G and Voltage Response (Sc.16)']
        for idx, scenario in enumerate(scenarios):
            if idx == 0:
                csv_files = [base_dir + f'/results/{scenarios[1]}_dc_curtailment_{day}.csv' for day in days]
                if 'hourly' in scenario:
                    files = os.listdir(base_dir + "/results")
                    csv_files = [base_dir + f"/results/{file}" for file in files if scenarios[1].replace("_hourly", "") in file and "dc_curtailment" in file and "hourly" in file]

                day_data = [pd.read_csv(f).set_index('Time') for f in csv_files]

                # Get PV system names

                pv_systems = [col.split('.')[0] for col in day_data[0].columns]
                # Concatenate all days
                all_data = pd.concat(day_data, keys=days, names=['Day', 'Time'])

                # Remove 'Day' column if present
                data_only = all_data.drop(columns=['Day'], errors='ignore') if 'Day' in all_data.columns else all_data

                # Repeat columns per phase
                data_only.columns = pv_systems

                # Sum over time and phases and multiply by 0.5 to represent half-hour
                total_curtailment = data_only.sum(axis=0) * 0
                total_curtailment = data_only.groupby(level="Day").sum() * 0
            # Read CSV files for this scenario
            else:
                csv_files = [base_dir + f'/results/{scenario}_dc_curtailment_{day}.csv' for day in days]
                if 'hourly' in scenario:
                    files = os.listdir(base_dir + "/results")
                    csv_files = [base_dir + f"/results/{file}" for file in files if scenario.replace("_hourly", "") in file and "dc_curtailment" in file and "hourly" in file]
                day_data = [pd.read_csv(f).set_index('Time') for f in csv_files]

                # Get PV system names

                pv_systems = [col.split('.')[0] for col in day_data[0].columns]
                # pv_systems = pv_systems[:len(pv_systems) // 3]
                # Concatenate all days
                all_data = pd.concat(day_data, keys=days, names=['Day', 'Time'])

                # Remove 'Day' column if present
                data_only = all_data.drop(columns=['Day'], errors='ignore') if 'Day' in all_data.columns else all_data

                # Repeat columns per phase
                data_only.columns = pv_systems
                if 'hourly' in scenario:
                    factor = 1
                else:
                    factor = 0.5
                # Sum over time and phases and multiply by 0.5 to represent half-hour
                total_curtailment = data_only.groupby(level="Day").sum() * factor
            # Group by PV system (sum across phases)
            total_per_pv = total_curtailment.groupby(total_curtailment.index).max()
            # print(total_per_pv.loc["Summer_Weekday"])
            total_values = [total_per_pv.loc['Summer_Weekday'][pv] for pv in pv_systems][:55]
            # Plot
            ax = axs[idx]
            ax.bar(range(len(pv_systems[:55])), total_values, color='lightblue', edgecolor='k')
            ax.set_title(scenarios_titles[idx], fontsize=9, weight='bold')
            if idx == 0 or idx == 3:
                ax.set_ylabel('Total Curtailment (kWh)')
            ax.set_xlabel(r'PV Systems $\rightarrow$ Distance from Source')
            ax.set_xticks([])
            ax.grid(True, axis='y', alpha=0.3)

        fig.subplots_adjust(bottom=0.05, top=0.90)

        # Unified legend (single color bar)
        from matplotlib.patches import Patch
        handles = [Patch(facecolor='lightblue', edgecolor='k', label='Total DC Curtailment')]
        fig.legend(handles, [h.get_label() for h in handles], loc='upper center', bbox_to_anchor=(0.5, 1.01), ncol=1, frameon=False, fontsize=10)

        if save_path:
            plt.savefig(save_path + r'\all_dc_curtailment.pdf', bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    # @classmethod
    # def plot_ac_curtailment_envelopes(cls, base_dir, scenarios, days=['Summer_Weekday', 'Summer_Weekend', 'Winter_Weekday', 'Winter_Weekend'], save_path=None):
    #     """
    #     Plot AC curtailment envelopes per PV system for multiple scenarios, mimicking voltage/current envelopes.
    #     """
    #     fig, axs = plt.subplots(2, 3, figsize=(12, 5))
    #     axs = axs.flatten()
    #
    #     if len(scenarios) == 1:
    #         axs = [axs]
    #
    #     scenarios_titles = ['BAU', 'Max. Allowable PV', '100% PV with Export Limit', '100% PV with Voltage Response',
    #                         '100% PV and 15% Battery \n with TOU and Voltage Response', '100% PV, 15% Battery and 30% EV \n with TOU, V2G and Voltage Response']
    #
    #     for idx, scenario in enumerate(scenarios):
    #         if idx == 0:
    #             continue
    #         # Read CSV files for this scenario
    #         csv_files = [base_dir + f'/results/{scenario}_ac_curtailment_{day}.csv' for day in days]
    #         day_data = [pd.read_csv(f).set_index('Time') for f in csv_files]
    #
    #         # Get PV system names
    #         pv_systems = [col.split('.')[0] for col in day_data[0].columns]
    #         print(pv_systems)
    #         # Concatenate all days
    #         all_data = pd.concat(day_data, keys=days, names=['Day', 'Time'])
    #
    #         # Remove 'Day' column if present
    #         data_only = all_data.drop(columns=['Day'], errors='ignore') if 'Day' in all_data.columns else all_data
    #
    #         # Compute max/min envelopes per PV system
    #         data_only.columns = pv_systems
    #         i_sum_per_pv = data_only.groupby(axis=1, level=0).sum()
    #         print(i_sum_per_pv)
    #         # i_min_per_pv = data_only.groupby(axis=1, level=0).min()
    #         i_sum_per_pv = i_sum_per_pv[pv_systems]
    #         # i_min_per_pv = i_min_per_pv[pv_systems]
    #
    #         # Envelope across time
    #         i_max = i_sum_per_pv.max(axis=0)
    #         i_min = i_sum_per_pv.min(axis=0)
    #
    #         # Plot envelopes
    #         ax = axs[idx]
    #         ax.fill_between(range(len(pv_systems)), i_min.values, i_max.values, alpha=0.3)
    #         ax.plot(range(len(pv_systems)), i_max.values, color='magenta', lw=0.8, label='Max Curtailment')
    #         ax.plot(range(len(pv_systems)), i_min.values, color='orange', lw=0.8, label='Min Curtailment')
    #
    #         ax.set_title(scenarios_titles[idx], fontsize=9)
    #         if idx == 0 or idx == 3:
    #             ax.set_ylabel('Curtailment (kWh)')
    #         if idx in [3, 4, 5]:
    #             ax.set_xlabel('PV Systems')
    #         ax.set_xticks([])
    #         ax.grid(True, alpha=0.3)
    #
    #     fig.subplots_adjust(bottom=0.05, top=0.90)
    #
    #     # Unified legend
    #     handles, labels = axs[0].get_legend_handles_labels()
    #     fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.01), ncol=4, frameon=False, fontsize=10)
    #
    #     if save_path:
    #         plt.savefig(save_path + r'\all_ac_curtailment.pdf', bbox_inches='tight')
    #         plt.close()
    #     else:
    #         plt.show()

    @classmethod
    def plot_voltages_from_csv(cls, csv_paths, save_path=None, DAYS=['Summer_Weekday', 'Summer_Weekend', 'Winter_Weekday', 'Winter_Weekend']):
        """Plot combined voltage analysis from multiple daily CSV files"""
        # Combine data from all days
        formatting = 'pdf'
        all_days = pd.concat(
            [pd.read_csv(f).assign(Day=day_idx + 1)
             for day_idx, f in enumerate(csv_paths)],
            ignore_index=True
        )

        # Create plot structure
        fig, axs = plt.subplots(3, 1, figsize=(14, 10))
        phases = {'1': 0, '2': 1, '3': 2}
        colors = plt.cm.tab10.colors  # Distinct colors for days

        for phase, ax_idx in phases.items():
            ax = axs[ax_idx]
            phase_data = all_days.filter(regex=f'\.{phase[-1]}$|Time')

            # Group data by bus and day
            plot_data = []
            positions = []
            for col_idx, col in enumerate(phase_data.columns[1:]):  # Skip Time column
                bus_data = []
                for day in sorted(all_days.Day.unique()):
                    bus_data.append(
                        phase_data[col][all_days.Day == day].values
                    )
                plot_data.extend(bus_data)
                positions.extend([col_idx + (day - 1) * 0.2 for day in sorted(all_days.Day.unique())])

            # Create boxplots with color coding
            bp = ax.boxplot(plot_data, positions=positions, widths=0.15,
                            patch_artist=True, showfliers=True)

            # Set colors for each day's boxes

            for patch, day in zip(bp['boxes'], list(range(len(csv_paths))) * len(phase_data.columns[1:])):
                patch.set_facecolor(colors[day])

            phase_label = {'1': 'A', '2': 'B', '3': 'C'}
            # Configure plot
            ax.set_title(f'Phase {phase_label[phase]}', fontsize=10)
            ax.set_xticks(np.arange(len(phase_data.columns[1:])) + 0.3)
            ax.axhline(1.1, color='r', linestyle='--')
            ax.axhline(0.9, color='r', linestyle='--')
            ax.set_ylabel('Voltage (p.u)')
            if phase == '3':
                ax.set_xticklabels([col.split('.')[0] for col in phase_data.columns[1:]], rotation=90)
                ax.set_xlabel('Buses')
            else:
                ax.set_xticklabels([])
                ax.set_xlabel('')
            ax.grid(True, alpha=0.3)

        # Create unified legend
        legend_patches = [plt.Rectangle((0, 0), 1, 1, color=colors[i], label=f"{DAYS[i].split('_')[0]} {DAYS[i].split('_')[1]}")
                          for i in range(len(csv_paths))]
        min_max_line = Line2D([0], [0], color='r', linestyle='--', label='Min-Max Limits')
        legend_patches.append(min_max_line)
        # fig.legend(handles=legend_patches, loc='upper left', bbox_to_anchor=(0.1, 0.98), ncol=2)
        fig.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, 1.01), ncol=5, frameon=False)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path + f'_All_Voltages.{formatting}', bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    @classmethod
    def plot_currents_from_csv(cls, csv_paths, save_path=None, DAYS=['Summer_Weekday', 'Summer_Weekend', 'Winter_Weekday', 'Winter_Weekend']):
        """Plot combined voltage analysis from multiple daily CSV files"""
        # Combine data from all days
        formatting = 'pdf'
        all_days = pd.concat(
            [pd.read_csv(f).assign(Day=day_idx + 1)
             for day_idx, f in enumerate(csv_paths)],
            ignore_index=True
        )

        # Create plot structure
        fig, axs = plt.subplots(3, 1, figsize=(20, 12))
        phases = {'1': 0, '2': 1, '3': 2}
        colors = plt.cm.tab10.colors  # Distinct colors for days

        for phase, ax_idx in phases.items():
            ax = axs[ax_idx]
            phase_data = all_days.filter(regex=f'\.{phase[-1]}$|Time')

            # Group data by bus and day
            plot_data = []
            positions = []
            for col_idx, col in enumerate(phase_data.columns[1:]):  # Skip Time column
                bus_data = []
                for day in sorted(all_days.Day.unique()):
                    bus_data.append(
                        phase_data[col][all_days.Day == day].values
                    )
                plot_data.extend(bus_data)
                positions.extend([col_idx + (day - 1) * 0.2 for day in sorted(all_days.Day.unique())])

            # Create boxplots with color coding
            bp = ax.boxplot(plot_data, positions=positions, widths=0.15,
                            patch_artist=True, showfliers=True)

            # Set colors for each day's boxes

            for patch, day in zip(bp['boxes'], list(range(len(csv_paths))) * len(phase_data.columns[1:])):
                patch.set_facecolor(colors[day])

            phase_label = {'1': 'A', '2': 'B', '3': 'C'}
            # Configure plot
            ax.set_title(f'Phase {phase_label[phase]}', fontsize=10)
            ax.set_xticks(np.arange(len(phase_data.columns[1:])) + 0.3)
            ax.axhline(100, color='r', linestyle='--')
            ax.set_ylabel('Loading (%)')
            if phase == '3':
                ax.set_xticklabels([col.split('.')[0] for col in phase_data.columns[1:]], rotation=90)
                ax.set_xlabel('Lines')
            else:
                ax.set_xticklabels([])
                ax.set_xlabel('')
            ax.grid(True, alpha=0.3)

        # Create unified legend
        legend_patches = [plt.Rectangle((0, 0), 1, 1, color=colors[i], label=f"{DAYS[i].split('_')[0]} {DAYS[i].split('_')[1]}")
                          for i in range(len(csv_paths))]
        max_line = Line2D([0], [0], color='r', linestyle='--', label='Max Limit')
        legend_patches.append(max_line)
        # fig.legend(handles=legend_patches, loc='upper left', bbox_to_anchor=(0.1, 0.98), ncol=2)
        fig.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, 1.01), ncol=5, frameon=False)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path + f'_All_Currents.{formatting}', bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    @classmethod
    def plot_voltage_unbalance_from_csv(cls, csv_paths, save_path=None, DAYS=['Summer_Weekday', 'Summer_Weekend', 'Winter_Weekday', 'Winter_Weekend']):
        """Plot voltage unbalance analysis from multiple daily CSV files"""
        formatting = 'pdf'
        all_days = pd.concat(
            [pd.read_csv(f).assign(Day=day_idx + 1)
             for day_idx, f in enumerate(csv_paths)],
            ignore_index=True
        )

        fig, ax = plt.subplots(figsize=(14, 6))
        colors = plt.cm.tab10.colors

        plot_data = []
        positions = []
        for col_idx, col in enumerate(all_days.columns[1:-1]):  # Skip Time and Day
            for day in sorted(all_days.Day.unique()):
                plot_data.append(all_days[col][all_days.Day == day].values)
                positions.append(col_idx + (day - 1) * 0.2)

        bp = ax.boxplot(plot_data, positions=positions, widths=0.15,
                        patch_artist=True, showfliers=True)

        for patch, day in zip(bp['boxes'], list(range(len(csv_paths))) * len(all_days.columns[1:-1])):
            patch.set_facecolor(colors[day])

        ax.set_xticks(np.arange(len(all_days.columns[1:-1])) + 0.3)
        ax.set_xticklabels(all_days.columns[1:-1], rotation=90)
        ax.axhline(2, color='r', linestyle='--')  # Unbalance threshold
        ax.set_ylabel('Voltage Unbalance (%)')
        ax.set_xlabel('Bus')
        ax.set_title(' ')
        ax.grid(True, alpha=0.3)

        legend_patches = [plt.Rectangle((0, 0), 1, 1, color=colors[i], label=f"{DAYS[i].split('_')[0]} {DAYS[i].split('_')[1]}")
                          for i in range(len(csv_paths))]
        max_line = Line2D([0], [0], color='r', linestyle='--', label='Max Limit')
        legend_patches.append(max_line)
        # fig.legend(handles=legend_patches, loc='upper left', bbox_to_anchor=(0.1, 0.90), ncol=2)
        fig.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, 1.01), ncol=5, frameon=False)

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path + f'_All_VUF.{formatting}', bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    @classmethod
    def plot_ac_curtailment_from_csv(cls, csv_paths, save_path=None, DAYS=['Summer_Weekday', 'Summer_Weekend', 'Winter_Weekday', 'Winter_Weekend']):
        """Plot DC curtailment with flipped axes, adjusted layout, and internal legend"""
        # Load and process data (unchanged)
        formatting = 'pdf'
        scenario_data = {}
        for idx, csv_file in enumerate(csv_paths):
            df = pd.read_csv(csv_file)
            df = df.drop(columns=['Time'])
            step_size = 30
            if 'hourly' in csv_file:
                step_size = 60
            scenario_totals = df.sum(axis=0) * step_size / 60
            scenario_data[DAYS[idx]] = scenario_totals.to_dict()

        # Organize data by phase and PV (unchanged)
        phase_groups = {'A': {}, 'B': {}, 'C': {}}
        for day in DAYS:
            for pv_key, value in scenario_data[day].items():
                if '.1' in pv_key:
                    phase = 'A'
                    pv_name = pv_key.split('.')[0]
                elif '.2' in pv_key:
                    phase = 'B'
                    pv_name = pv_key.split('.')[0]
                elif '.3' in pv_key:
                    phase = 'C'
                    pv_name = pv_key.split('.')[0]
                else:
                    continue

                if pv_name not in phase_groups[phase]:
                    phase_groups[phase][pv_name] = []
                phase_groups[phase][pv_name].append(value)

        # Create plot with adjusted dimensions
        fig, axes = plt.subplots(3, 1, figsize=(18, 10))

        colors = [
            '#4E79A7',  # Blue
            '#F28E2B',  # Orange
            '#59A14F',  # Green
            '#E15759'  # Red
        ]
        markers = ['o', '+', '*', 'x']

        for phase, ax in zip(['A', 'B', 'C'], axes):
            if not phase_groups[phase]:
                ax.axis('off')
                continue

            pv_names = list(phase_groups[phase].keys())
            x_pos = np.arange(len(pv_names))
            # Remove LaTeX formatting for 'H'
            pv_systems_no = [
                pv_name.split('_')[1] + ' (H)'  # Plain text with (H)
                if pv_name.split('_')[0] != 'pv'
                else pv_name.split('_')[1]
                for pv_name in pv_names
            ]

            # Plot symbols with flipped axes (unchanged)
            for pv_idx, pv in enumerate(pv_names):
                scenarios = phase_groups[phase][pv]
                for scenario_idx, value in enumerate(scenarios):
                    ax.scatter(
                        pv_idx,  # x-axis: PV index
                        value,  # y-axis: DC curtailment
                        color=colors[scenario_idx],
                        marker=markers[scenario_idx],
                        s=100,
                        edgecolors='k',
                        zorder=2
                    )

            # Configure axes
            ax.set_title(f'Phase {phase}', fontsize=12)
            ax.set_ylabel('Curtailment (kWh)', fontsize=10)
            if phase == 'C':
                ax.set_xlabel('System No.', fontsize=10)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(pv_systems_no, rotation=90, ha='right', fontsize=9)

            # Manually color 'H' in x-ticks red
            for label in ax.get_xticklabels():
                if '(H)' in label.get_text():
                    label.set_color('red')

            ax.grid(axis='y', alpha=0.3, zorder=1)
            ax.set_ylim(bottom=0)
            ax.set_xlim(-0.5, len(pv_names) - 0.5)

        # Add unified legend with red 'H' explanation
        from matplotlib.lines import Line2D
        handles = [
            Line2D([0], [0], marker=markers[i], color=colors[i], linestyle='',
                   markersize=10, label=DAYS[i]) for i in range(len(DAYS))
        ]

        n = 4
        labels = DAYS.copy()
        if sum([0 if pv_name.split('_')[0] == 'pv' else 1 for pv_name in pv_names]) > 0:
            # Add custom text-only item
            text_only_handle = Line2D([], [], color='none', label=r"H: Hybrid PV Battery System")
            handles.append(text_only_handle)

            # Labels (match the order of handles)
            labels = DAYS + [r"H: Hybrid PV Battery System"]
            n = 5

        if any('(H)' in pv_name for pv_name in pv_names):
            # Add red 'H' legend entry using a proxy artist
            h_legend = Line2D([], [], color='red', marker='s', linestyle='None',
                              markersize=10, label='H: Hybrid PV Battery System')
            handles.append(h_legend)
            labels.append('H: Hybrid PV Battery System')

        # # Add to legend
        # fig.legend(
        #     handles, labels,
        #     loc='upper center',
        #     ncol=n,
        #     bbox_to_anchor=(0.3, 0.80),
        #     frameon=True,
        #     fontsize=8
        # )

        fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, 0.90), ncol=n, frameon=False, fontsize=8)
        plt.tight_layout(pad=3.0)
        plt.subplots_adjust(top=0.85)

        if save_path:
            plt.savefig(save_path + f'_All_AC_CURTAILMENT.{formatting}', bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    # @classmethod
    # def plot_ac_curtailment_from_csv(cls, csv_paths, save_path=None, DAYS=['Summer_Weekday', 'Summer_Weekend', 'Winter_Weekday', 'Winter_Weekend']):
    #     """Plot DC curtailment with flipped axes, adjusted layout, and internal legend"""
    #     # Load and process data (unchanged)
    #     scenario_data = {}
    #     for idx, csv_file in enumerate(csv_paths):
    #         df = pd.read_csv(csv_file)
    #         df = df.drop(columns=['Time'])
    #         scenario_totals = df.sum(axis=0) * Results.STEP_SIZE / 60
    #         scenario_data[DAYS[idx]] = scenario_totals.to_dict()
    #
    #     # Organize data by phase and PV (unchanged)
    #     phase_groups = {'A': {}, 'B': {}, 'C': {}}
    #     for day in DAYS:
    #         for pv_key, value in scenario_data[day].items():
    #             if '.1' in pv_key:
    #                 phase = 'A'
    #                 pv_name = pv_key.split('.')[0]
    #             elif '.2' in pv_key:
    #                 phase = 'B'
    #                 pv_name = pv_key.split('.')[0]
    #             elif '.3' in pv_key:
    #                 phase = 'C'
    #                 pv_name = pv_key.split('.')[0]
    #             else:
    #                 continue
    #
    #             if pv_name not in phase_groups[phase]:
    #                 phase_groups[phase][pv_name] = []
    #             phase_groups[phase][pv_name].append(value)
    #
    #     # Create plot with adjusted dimensions
    #     fig, axes = plt.subplots(3, 1, figsize=(18, 10))  # Wider (18) and shorter (10)
    #
    #     colors = [
    #         '#4E79A7',  # Blue
    #         '#F28E2B',  # Orange
    #         '#59A14F',  # Green
    #         '#E15759'  # Red
    #     ]
    #     markers = ['o', '+', '*', 'x']
    #
    #     for phase, ax in zip(['A', 'B', 'C'], axes):
    #         if not phase_groups[phase]:
    #             ax.axis('off')
    #             continue
    #
    #         pv_names = list(phase_groups[phase].keys())
    #         x_pos = np.arange(len(pv_names))
    #         pv_systems_no = [pv_name.split('_')[1] if pv_name.split('_')[0] == 'pv' else pv_name.split('_')[1] + '$(H)$' for pv_name in pv_names]
    #         # Plot symbols with flipped axes
    #         for pv_idx, pv in enumerate(pv_names):
    #             scenarios = phase_groups[phase][pv]
    #             for scenario_idx, value in enumerate(scenarios):
    #                 ax.scatter(
    #                     pv_idx,  # x-axis: PV index
    #                     value,  # y-axis: DC curtailment
    #                     color=colors[scenario_idx],
    #                     marker=markers[scenario_idx],
    #                     s=100,
    #                     edgecolors='k',
    #                     zorder=2  # Ensure markers are above gridlines
    #                 )
    #
    #         # Configure axes
    #         ax.set_title(f'Phase {phase}', fontsize=12)
    #         ax.set_ylabel('Curtailment (kWh)', fontsize=10)
    #         if phase == 'C':
    #             ax.set_xlabel('System No.', fontsize=10)
    #         ax.set_xticks(x_pos)
    #         ax.set_xticklabels(pv_systems_no, rotation=90, ha='right', fontsize=9)
    #         ax.grid(axis='y', alpha=0.3, zorder=1)
    #         ax.set_ylim(bottom=0)  # Start y-axis at 0
    #         ax.set_xlim(-0.5, len(pv_names) - 0.5)  # Add padding for x-axis
    #
    #     # Add unified legend inside the plot (upper center)
    #     from matplotlib.lines import Line2D
    #     # Handles
    #     handles = [
    #         Line2D([0], [0], marker=markers[i], color=colors[i], linestyle='',
    #                markersize=10, label=DAYS[i]) for i in range(len(DAYS))
    #     ]
    #     n = 4
    #     labels = DAYS
    #     if sum([0 if pv_name.split('_')[0] == 'pv' else 1 for pv_name in pv_names]) > 0:
    #
    #         # Add custom text-only item
    #         text_only_handle = Line2D([], [], color='none', label=r"H: Hybrid PV Battery System")
    #         handles.append(text_only_handle)
    #
    #         # Labels (match the order of handles)
    #         labels = DAYS + [r"H: Hybrid PV Battery System"]
    #         n = 5
    #     # Add to legend
    #     fig.legend(
    #         handles, labels,
    #         loc='upper center',
    #         ncol=n,
    #         bbox_to_anchor=(0.3, 0.8),
    #         frameon=True,
    #         fontsize=8
    #     )
    #
    #     # Adjust layout to accommodate legend
    #     plt.tight_layout(pad=3.0)
    #     plt.subplots_adjust(top=0.88)  # Reduce top margin for legend placement
    #
    #     if save_path:
    #         plt.savefig(save_path + '_All_AC_CURTAILMENT.svg', bbox_inches='tight')
    #         plt.close()
    #     else:
    #         plt.show()

    @classmethod
    def plot_dc_curtailment_from_csv(cls, csv_paths, save_path=None, DAYS=['Summer_Weekday', 'Summer_Weekend', 'Winter_Weekday', 'Winter_Weekend']):
        """Plot DC curtailment with flipped axes, adjusted layout, and internal legend"""
        # Load and process data (unchanged)
        formatting = 'pdf'
        scenario_data = {}
        for idx, csv_file in enumerate(csv_paths):
            df = pd.read_csv(csv_file)
            df = df.drop(columns=['Time'])
            step_size = 30
            if 'hourly' in csv_file:
                step_size = 60
            scenario_totals = df.sum(axis=0) * step_size / 60
            scenario_data[DAYS[idx]] = scenario_totals.to_dict()

        # Organize data by phase and PV (unchanged)
        phase_groups = {'A': {}, 'B': {}, 'C': {}}
        for day in DAYS:
            for pv_key, value in scenario_data[day].items():
                if '.1' in pv_key:
                    phase = 'A'
                    pv_name = pv_key.split('.')[0]
                elif '.2' in pv_key:
                    phase = 'B'
                    pv_name = pv_key.split('.')[0]
                elif '.3' in pv_key:
                    phase = 'C'
                    pv_name = pv_key.split('.')[0]
                else:
                    continue

                if pv_name not in phase_groups[phase]:
                    phase_groups[phase][pv_name] = []
                phase_groups[phase][pv_name].append(value)

        # Create plot with adjusted dimensions
        fig, axes = plt.subplots(3, 1, figsize=(18, 10))

        colors = [
            '#4E79A7',  # Blue
            '#F28E2B',  # Orange
            '#59A14F',  # Green
            '#E15759'  # Red
        ]
        markers = ['o', '+', '*', 'x']

        for phase, ax in zip(['A', 'B', 'C'], axes):
            if not phase_groups[phase]:
                ax.axis('off')
                continue

            pv_names = list(phase_groups[phase].keys())
            x_pos = np.arange(len(pv_names))
            # Remove LaTeX formatting for 'H'
            pv_systems_no = [
                pv_name.split('_')[1] + ' (H)'  # Plain text with (H)
                if pv_name.split('_')[0] != 'pv'
                else pv_name.split('_')[1]
                for pv_name in pv_names
            ]

            # Plot symbols with flipped axes (unchanged)
            for pv_idx, pv in enumerate(pv_names):
                scenarios = phase_groups[phase][pv]
                for scenario_idx, value in enumerate(scenarios):
                    ax.scatter(
                        pv_idx,  # x-axis: PV index
                        value,  # y-axis: DC curtailment
                        color=colors[scenario_idx],
                        marker=markers[scenario_idx],
                        s=100,
                        edgecolors='k',
                        zorder=2
                    )

            # Configure axes
            ax.set_title(f'Phase {phase}', fontsize=12)
            ax.set_ylabel('Curtailment (kWh)', fontsize=10)
            if phase == 'C':
                ax.set_xlabel('System No.', fontsize=10)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(pv_systems_no, rotation=90, ha='right', fontsize=9)

            # Manually color 'H' in x-ticks red
            for label in ax.get_xticklabels():
                if '(H)' in label.get_text():
                    label.set_color('red')

            ax.grid(axis='y', alpha=0.3, zorder=1)
            ax.set_ylim(bottom=0)
            ax.set_xlim(-0.5, len(pv_names) - 0.5)

        # Add unified legend with red 'H' explanation
        from matplotlib.lines import Line2D
        handles = [
            Line2D([0], [0], marker=markers[i], color=colors[i], linestyle='',
                   markersize=10, label=DAYS[i]) for i in range(len(DAYS))
        ]

        n = 4
        labels = DAYS.copy()
        if sum([0 if pv_name.split('_')[0] == 'pv' else 1 for pv_name in pv_names]) > 0:
            # Add custom text-only item
            text_only_handle = Line2D([], [], color='none', label=r"H: Hybrid PV Battery System")
            handles.append(text_only_handle)

            # Labels (match the order of handles)
            labels = DAYS + [r"H: Hybrid PV Battery System"]
            n = 5

        if any('(H)' in pv_name for pv_name in pv_names):
            # Add red 'H' legend entry using a proxy artist
            h_legend = Line2D([], [], color='red', marker='s', linestyle='None',
                              markersize=10, label='H: Hybrid PV Battery System')
            handles.append(h_legend)
            labels.append('H: Hybrid PV Battery System')

        # Add to legend
        # fig.legend(
        #     handles, labels,
        #     loc='upper center',
        #     ncol=n,
        #     bbox_to_anchor=(0.3, 0.80),
        #     frameon=True,
        #     fontsize=8
        # )
        fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, 0.90), ncol=n, frameon=False, fontsize=8)
        plt.tight_layout(pad=3.0)
        plt.subplots_adjust(top=0.85)

        if save_path:
            plt.savefig(save_path + f'_All_DC_CURTAILMENT.{formatting}', bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    # @classmethod
    # def plot_dc_curtailment_from_csv(cls, csv_paths, save_path=None, DAYS=['Summer_Weekday', 'Summer_Weekend', 'Winter_Weekday', 'Winter_Weekend']):
    #     """Plot DC curtailment with flipped axes, adjusted layout, and internal legend"""
    #     # Load and process data (unchanged)
    #     scenario_data = {}
    #     for idx, csv_file in enumerate(csv_paths):
    #         df = pd.read_csv(csv_file)
    #         df = df.drop(columns=['Time'])
    #         scenario_totals = df.sum(axis=0) * Results.STEP_SIZE / 60
    #         scenario_data[DAYS[idx]] = scenario_totals.to_dict()
    #
    #     # Organize data by phase and PV (unchanged)
    #     phase_groups = {'A': {}, 'B': {}, 'C': {}}
    #     for day in DAYS:
    #         for pv_key, value in scenario_data[day].items():
    #             if '.1' in pv_key:
    #                 phase = 'A'
    #                 pv_name = pv_key.split('.')[0]
    #             elif '.2' in pv_key:
    #                 phase = 'B'
    #                 pv_name = pv_key.split('.')[0]
    #             elif '.3' in pv_key:
    #                 phase = 'C'
    #                 pv_name = pv_key.split('.')[0]
    #             else:
    #                 continue
    #
    #             if pv_name not in phase_groups[phase]:
    #                 phase_groups[phase][pv_name] = []
    #             phase_groups[phase][pv_name].append(value)
    #
    #     # Create plot with adjusted dimensions
    #     fig, axes = plt.subplots(3, 1, figsize=(18, 10))  # Wider (18) and shorter (10)
    #
    #     colors = [
    #         '#4E79A7',  # Blue
    #         '#F28E2B',  # Orange
    #         '#59A14F',  # Green
    #         '#E15759'  # Red
    #     ]
    #     markers = ['o', '+', '*', 'x']
    #
    #     for phase, ax in zip(['A', 'B', 'C'], axes):
    #         if not phase_groups[phase]:
    #             ax.axis('off')
    #             continue
    #
    #         pv_names = list(phase_groups[phase].keys())
    #         x_pos = np.arange(len(pv_names))
    #         pv_systems_no = [pv_name.split('_')[1] if pv_name.split('_')[0] == 'pv' else pv_name.split('_')[1] + '$(H)$' for pv_name in pv_names]
    #         # Plot symbols with flipped axes
    #         for pv_idx, pv in enumerate(pv_names):
    #             scenarios = phase_groups[phase][pv]
    #             for scenario_idx, value in enumerate(scenarios):
    #                 ax.scatter(
    #                     pv_idx,  # x-axis: PV index
    #                     value,  # y-axis: DC curtailment
    #                     color=colors[scenario_idx],
    #                     marker=markers[scenario_idx],
    #                     s=100,
    #                     edgecolors='k',
    #                     zorder=2  # Ensure markers are above gridlines
    #                 )
    #
    #         # Configure axes
    #         ax.set_title(f'Phase {phase}', fontsize=12)
    #         ax.set_ylabel('Curtailment (kWh)', fontsize=10)
    #         if phase == 'C':
    #             ax.set_xlabel('System No.', fontsize=10)
    #         ax.set_xticks(x_pos)
    #         ax.set_xticklabels(pv_systems_no, rotation=90, ha='right', fontsize=9)
    #         ax.grid(axis='y', alpha=0.3, zorder=1)
    #         ax.set_ylim(bottom=0)  # Start y-axis at 0
    #         ax.set_xlim(-0.5, len(pv_names) - 0.5)  # Add padding for x-axis
    #
    #     # Add unified legend inside the plot (upper center)
    #     from matplotlib.lines import Line2D
    #     # Handles
    #     handles = [
    #         Line2D([0], [0], marker=markers[i], color=colors[i], linestyle='',
    #                markersize=10, label=DAYS[i]) for i in range(len(DAYS))
    #     ]
    #     n = 4
    #     labels = DAYS
    #     if sum([0 if pv_name.split('_')[0] == 'pv' else 1 for pv_name in pv_names]) > 0:
    #         # Add custom text-only item
    #         text_only_handle = Line2D([], [], color='none', label=r"H: Hybrid PV Battery System")
    #         handles.append(text_only_handle)
    #
    #         # Labels (match the order of handles)
    #         labels = DAYS + [r"H: Hybrid PV Battery System"]
    #         n = 5
    #     # Add to legend
    #     fig.legend(
    #         handles, labels,
    #         loc='upper center',
    #         ncol=n,
    #         bbox_to_anchor=(0.3, 0.85),
    #         frameon=True,
    #         fontsize=8
    #     )
    #
    #     # Adjust layout to accommodate legend
    #     plt.tight_layout(pad=3.0)
    #     plt.subplots_adjust(top=0.88)  # Reduce top margin for legend placement
    #
    #     if save_path:
    #         plt.savefig(save_path + '_All_DC_CURTAILMENT.svg', bbox_inches='tight')
    #         plt.close()
    #     else:
    #         plt.show()

    @classmethod
    def plot_irradiance_from_csv(cls, csv_path, save_path=None, days=['Summer_Weekday', 'Winter_Weekday']):
        plt.figure(figsize=(12, 6))

        # Define colors and styles for different seasons
        styles = {
            'Summer_Weekday': {'color': 'red', 'linestyle': '-'},
            'Winter_Weekday': {'color': 'blue', 'linestyle': '-'}
        }
        csv_paths = [csv_path + f'/irradiance_{day}.csv' for day in days]

        for csv_path, day_label in zip(csv_paths, days):
            df = pd.read_csv(csv_path)
            df['Time'] = df['Time'].str.replace(' ', '')  # Clean spacing from time strings
            plt.plot(df['Time'], df['Irradiance (W/m2)'], label=day_label, **styles.get(day_label, {}))

        # Create clean time ticks from the last dataframe
        time_ticks = df['Time'].values

        plt.title(' ', fontsize=14)
        plt.xlabel('Time (hours)', fontsize=20)
        plt.ylabel('Irradiance (kW/m2)', fontsize=20)
        plt.grid(True, alpha=0.3)
        plt.legend(['Summer', ' Winter'])
        plt.xticks(list(range(0, 48, 4)), [pd.to_datetime(time_ticks[i]).strftime('%H:%M') for i in list(range(0, 48, 4))], rotation=45, fontsize=14)
        plt.yticks(fontsize=14)

        # Save or show plot
        if save_path:
            os.makedirs(save_path, exist_ok=True)
            plt.savefig(os.path.join(save_path, 'irradiance_comparison.pdf'), bbox_inches='tight')
            plt.close()
        else:
            plt.tight_layout()
            plt.show()

    @classmethod
    def plot_temperature_from_csv(cls, csv_path, save_path=None, days=['Summer_Weekday', 'Winter_Weekday']):
        plt.figure(figsize=(12, 6))

        # Define colors and styles for different seasons
        styles = {
            'Summer_Weekday': {'color': 'red', 'linestyle': '-'},
            'Winter_Weekday': {'color': 'blue', 'linestyle': '-'}
        }
        csv_paths = [csv_path + f'/temperature_{day}.csv' for day in days]

        for csv_path, day_label in zip(csv_paths, days):
            df = pd.read_csv(csv_path)
            df['Time'] = df['Time'].str.replace(' ', '')  # Clean spacing from time strings
            plt.plot(df['Time'], df['Temperature (C)'], label=day_label, **styles.get(day_label, {}))

        # Create clean time ticks from the last dataframe
        time_ticks = df['Time'].values
        plt.title(' ', fontsize=14)
        plt.xlabel('Time (hours)', fontsize=20)
        plt.ylabel('Temperature (C)', fontsize=20)
        plt.grid(True, alpha=0.3)
        plt.legend(['Summer', ' Winter'])
        plt.xticks(list(range(0, 48, 4)), [pd.to_datetime(time_ticks[i]).strftime('%H:%M') for i in list(range(0, 48, 4))], rotation=45, fontsize=14)
        plt.yticks(fontsize=14)

        # Save or show plot
        if save_path:
            os.makedirs(save_path, exist_ok=True)
            plt.savefig(os.path.join(save_path, 'temperature_comparison.pdf'), bbox_inches='tight')
            plt.close()
        else:
            plt.tight_layout()
            plt.show()
