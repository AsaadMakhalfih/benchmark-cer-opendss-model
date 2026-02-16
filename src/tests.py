import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, ks_2samp


def run_comprehensive_comparison(your_model_voltages, opendss_voltages,
                                 your_model_currents, opendss_currents,
                                 your_model_active_pv_power=None, opendss_active_pv_power=None,
                                 your_model_reactive_pv_power=None, opendss_reactive_pv_power=None,
                                 save_plots_dir=None):
    """
    Perform all comparison tests between your model and OpenDSS results.

    Parameters:
    - your_model_voltages: Dictionary {bus: list_of_voltages}
    - opendss_voltages: Dictionary {bus: list_of_voltages}
    - your_model_currents: Dictionary {line: list_of_currents}
    - opendss_currents: Dictionary {line: list_of_currents}
    - save_plots_dir: (Optional) Directory to save comparison plots

    Returns:
    - Dictionary containing all comparison results and metrics
    """

    results = {
        'voltage_metrics': {},
        'current_metrics': {},
        'pv_active_power_metrics': {},
        'pv_reactive_power_metrics': {},
        'statistical_tests': {},
        'error_data': {}
    }

    # Helper function to ensure consistent lengths
    def _ensure_consistent_lengths(your_data, ref_data):
        """
        Ensure that all lists in the dictionaries have the same length.
        If not, truncate to the shortest length.
        """
        min_length = min(
            min(len(your_data[key]) for key in your_data),
            min(len(ref_data[key]) for key in ref_data)
        )

        your_data_consistent = {key: your_data[key][:min_length] for key in your_data}
        ref_data_consistent = {key: ref_data[key][:min_length] for key in ref_data}

        return your_data_consistent, ref_data_consistent

    # Ensure consistent lengths for voltages and currents
    your_model_voltages, opendss_voltages = _ensure_consistent_lengths(your_model_voltages, opendss_voltages)
    your_model_currents, opendss_currents = _ensure_consistent_lengths(your_model_currents, opendss_currents)

    # Helper function for error calculation
    def _calculate_errors(your_data, ref_data):
        if your_data is None or ref_data is None:
            return 0, 0
        abs_errors = {}
        rel_errors = {}
        for key in your_data:
            if key in ref_data:
                y_arr = np.array(your_data[key])
                r_arr = np.array(ref_data[key])
                abs_errors[key] = np.abs(y_arr - r_arr)
                with np.errstate(divide='ignore', invalid='ignore'):
                    rel_errors[key] = np.where(r_arr != 0, (abs_errors[key] / r_arr) * 100, np.nan)
        return abs_errors, rel_errors

    # Calculate errors
    voltage_abs, voltage_rel = _calculate_errors(your_model_voltages, opendss_voltages)
    current_abs, current_rel = _calculate_errors(your_model_currents, opendss_currents)
    pv_active_power_abs, pv_active_power_rel = _calculate_errors(your_model_active_pv_power, opendss_active_pv_power)
    pv_reactive_power_abs, pv_reactive_power_rel = _calculate_errors(your_model_reactive_pv_power, opendss_reactive_pv_power)

    results['error_data'] = {
        'voltage_abs': voltage_abs,
        'voltage_rel': voltage_rel,
        'current_abs': current_abs,
        'current_rel': current_rel,
        'pv_active_power_abs': pv_active_power_abs,
        'pv_active_power_rel': pv_active_power_rel,
        'pv_reactive_power_abs': pv_reactive_power_abs,
        'pv_reactive_power_rel': pv_reactive_power_rel
    }

    # Calculate RMSE
    def _calculate_rmse(errors_dict):
        if errors_dict is 0:
            return 0
        all_errors = []
        for err in errors_dict.values():
            all_errors.extend(err)
        return np.sqrt(np.mean(np.array(all_errors) ** 2))

    results['voltage_metrics']['rmse'] = _calculate_rmse(voltage_abs)
    results['current_metrics']['rmse'] = _calculate_rmse(current_abs)
    results['pv_active_power_metrics']['rmse'] = _calculate_rmse(pv_active_power_abs)
    results['pv_reactive_power_metrics']['rmse'] = _calculate_rmse(pv_reactive_power_abs)

    # Calculate mean errors
    def _calculate_mean_errors(abs_err, rel_err):
        if abs_err == 0:
            return {
            'mean_abs': 0,
            'max_abs': 0,
            'mean_rel': 0,
            'max_rel': 0
        }
        return {
            'mean_abs': np.nanmean([np.mean(v) for v in abs_err.values()]),
            'max_abs': np.nanmax([np.max(v) for v in abs_err.values()]),
            'mean_rel': np.nanmean([np.nanmean(v) for v in rel_err.values()]),
            'max_rel': np.nanmax([np.nanmax(v) for v in rel_err.values()])
        }

    results['voltage_metrics'].update(_calculate_mean_errors(voltage_abs, voltage_rel))
    results['current_metrics'].update(_calculate_mean_errors(current_abs, current_rel))
    results['pv_active_power_metrics'].update(_calculate_mean_errors(pv_active_power_abs, pv_active_power_rel))
    results['pv_reactive_power_metrics'].update(_calculate_mean_errors(pv_reactive_power_abs, pv_reactive_power_rel))

    # Statistical tests
    def _perform_tests(your_data, ref_data):
        if your_data is None:
            return {
            't_test': 0,
            'ks_test': 0
        }
        your_vals = []
        ref_vals = []
        for key in your_data:
            if key in ref_data:
                your_vals.extend(your_data[key])
                ref_vals.extend(ref_data[key])

        return {
            't_test': ttest_ind(your_vals, ref_vals),
            'ks_test': ks_2samp(your_vals, ref_vals)
        }

    results['statistical_tests']['voltage'] = _perform_tests(your_model_voltages, opendss_voltages)
    results['statistical_tests']['current'] = _perform_tests(your_model_currents, opendss_currents)
    results['statistical_tests']['pv_active_power'] = _perform_tests(your_model_active_pv_power, opendss_active_pv_power)
    results['statistical_tests']['pv_reactive_power'] = _perform_tests(your_model_reactive_pv_power, opendss_reactive_pv_power)

    # Generate comparison plots
    if save_plots_dir:
        os.makedirs(save_plots_dir, exist_ok=True)

        # Voltage plots
        for bus in your_model_voltages:
            if bus in opendss_voltages:
                plt.figure(figsize=(10, 4))
                plt.plot(your_model_voltages[bus], label='Your Model')
                plt.plot(opendss_voltages[bus], label='OpenDSS', alpha=0.7)
                plt.title(f'Voltage Comparison - {bus}')
                plt.xlabel('Time Step')
                plt.ylabel('Voltage (pu)')
                plt.legend()
                plt.savefig(os.path.join(save_plots_dir, f'voltage_{bus}.png'))
                plt.close()

        # # Current plots
        # for line in your_model_currents:
        #     if line in opendss_currents:
        #         plt.figure(figsize=(10, 4))
        #         plt.plot(your_model_currents[line], label='Your Model')
        #         plt.plot(opendss_currents[line], label='OpenDSS', alpha=0.7)
        #         plt.title(f'Current Comparison - {line}')
        #         plt.xlabel('Time Step')
        #         plt.ylabel('Current (A)')
        #         plt.legend()
        #         plt.savefig(os.path.join(save_plots_dir, f'current_{line}.png'))
        #         plt.close()

        # PV plots
        if your_model_active_pv_power is not None:
            for pv in your_model_active_pv_power:
                if pv in opendss_active_pv_power:
                    plt.figure(figsize=(10, 4))
                    plt.plot(your_model_active_pv_power[pv], label='Your Model')
                    plt.plot(opendss_active_pv_power[pv], label='OpenDSS', alpha=0.7)
                    plt.title(f'Current Comparison - {pv}')
                    plt.xlabel('Time Step')
                    plt.ylabel('Power (kW)')
                    plt.legend()
                    plt.savefig(os.path.join(save_plots_dir, f'active_power_{pv}.png'))
                    plt.close()

        # PV plots
        if your_model_reactive_pv_power is not None:
            for pv in your_model_reactive_pv_power:
                if pv in opendss_reactive_pv_power:
                    plt.figure(figsize=(10, 4))
                    plt.plot(your_model_reactive_pv_power[pv], label='Your Model')
                    plt.plot(opendss_reactive_pv_power[pv], label='OpenDSS', alpha=0.7)
                    plt.title(f'Current Comparison - {pv}')
                    plt.xlabel('Time Step')
                    plt.ylabel('Power (kVAr)')
                    plt.legend()
                    plt.savefig(os.path.join(save_plots_dir, f'reactive_power_{pv}.png'))
                    plt.close()
    return results


# Example usage
if __name__ == "__main__":
    # Example data structure
    your_volts = {'Bus1': [1.02, 1.01, 0.99], 'Bus2': [0.98, 1.0, 1.02]}
    dss_volts = {'Bus1': [1.01, 1.0, 1.0], 'Bus2': [0.99, 1.01, 1.01]}

    your_currents = {'Line1': [95, 100, 105], 'Line2': [50, 55, 60]}
    dss_currents = {'Line1': [98, 102, 103], 'Line2': [52, 54, 58]}

    # # Run comprehensive comparison
    # results = run_comprehensive_comparison(your_model_voltages=your_volts, opendss_voltages=dss_volts, your_model_currents=your_currents, opendss_currents=dss_currents,
    #                                        your_model_active_pv_power=, opendss_active_pv_power=, save_plots_dir='comparison_plots')
    #
    # # Print summary metrics
    # print("Voltage Metrics:")
    # print(f"RMSE: {results['voltage_metrics']['rmse']:.4f}")
    # print(f"Mean Absolute Error: {results['voltage_metrics']['mean_abs']:.4f}")
    # print(f"Mean Relative Error: {results['voltage_metrics']['mean_rel']:.2f}%")
    #
    # print("\nCurrent Metrics:")
    # print(f"RMSE: {results['current_metrics']['rmse'] / 100:.4f}")
    # print(f"Mean Absolute Error: {results['current_metrics']['mean_abs'] / 100:.4f}")
    # print(f"Mean Relative Error: {results['current_metrics']['mean_rel'] / 100:.2f}%")
