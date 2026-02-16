from dataclasses import dataclass
import numpy as np
import os
import pandas as pd


def import_txt_file_as_numpy(txt_path, delimiter=",", dtype=float, skip_header=0):
    """
    Load a text file as a NumPy array.

    Parameters:
    - txt_path (str): Path to the text.
    - delimiter (str): Delimiter used in the file (default: ',').
    - dtype (data-type): Desired data type of the array (default: float).
    - skip_header (int): Number of lines to skip at the beginning of the file (default: 0).

    Returns:
    - numpy.ndarray: NumPy array containing the data.
    """
    try:
        data = np.genfromtxt(txt_path, delimiter=delimiter, dtype=dtype, skip_header=skip_header)
        return data
    except Exception as e:
        print(f"An error occurred while loading the file: {e}")
        return None


@dataclass
class ModelInputData:
    """
    Represents external input data for models, such as demand power, irradiance, temperature, etc.
    """
    demand_power: {int: [float]}
    irradiance: [float]
    temperature: [float]
    step_size: int
    time_range: [float, float]
    ev_behaviour: {int: [[tuple], int, [tuple], [tuple]]}


if __name__ == '__main__':
    load_data_path = os.path.dirname(__file__) + "/data/load-data/summer-weekday"
    irrad_data_path = os.path.dirname(__file__) + "/data/pv-data/summer-weekday"
    temp_data_path = os.path.dirname(__file__) + "/data/pv-data/summer-weekday"
    ev_behaviour_data_path = os.path.dirname(__file__) + "/data/ev-data"
    circuit_labels = list(range(1, 166))
    demand_power = {circuit_label: None for circuit_label in circuit_labels}
    for label in circuit_labels:
        demand_power[label] = import_txt_file_as_numpy(load_data_path + f'/Load{1}.txt')

    irradiance = import_txt_file_as_numpy(irrad_data_path + f'/solar.txt')
    temperature = import_txt_file_as_numpy(temp_data_path + f'/temp.txt')
    model_data = ModelInputData(demand_power, irradiance, temperature, 30)

    print(model_data.demand_power[5][24])
    print(model_data.irradiance[24])
    print(model_data.temperature[24])
