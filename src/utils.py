import pandas as pd
import ast


def remove_sublist(main_list, sublist):
    return [item for item in main_list if item not in sublist]


def intersection(main_list, sublist):
    return list(set(main_list) & set(sublist))


def get_ev_behaviour(label, data_path):
    ev_behaviour_data = pd.read_csv(data_path).set_index('Label')
    driving_intervals = ast.literal_eval(ev_behaviour_data.loc[label].values[0])
    driving_distance = int(ev_behaviour_data.loc[label].values[1])
    return {'driving_distance': driving_distance, 'driving_intervals': driving_intervals}
