import datetime
import pickle
import numpy as np
import warnings

warnings.filterwarnings('ignore')


def load_models():
    loaded_station_names = ['LIVST', 'STFD', 'SHENFLD', 'CHLMSFD', 'CLCHSTR', 'MANNGTR', 'IPSWICH', 'STWMRKT', 'DISS']
    # Load the models from files
    loaded_model_dict = {}
    for station_name in loaded_station_names:
        with open(f'{station_name}_model_knn_not_imputed_NEW.pkl', 'rb') as model_file:
            loaded_model_dict[station_name] = pickle.load(model_file)

    return loaded_model_dict


# MANUALLY CHANGE THE OPENING NAME
loaded_models = load_models()
print(loaded_models)




def parameterise(lateness, hour, day_of_week):
    "Encodes the input params into machine-readable format"

    def group_hours(hour_func):
        for i, (start, end) in enumerate(ranges):
            if start <= hour_func <= end:
                return f'Group_{i + 1}'
        return 'Other'

    is_weekend = 0
    is_offpeak = 0

    if (day_of_week == 'SAT') or (day_of_week == 'SUN'):
        is_weekend = 1
        is_offpeak = 1
    if (hour >= 9) or (hour <= 2):
        is_offpeak = 1
    ranges = [(6, 9), (10, 15), (16, 19), (20, 23), (0, 5)]
    group = group_hours(hour)

    one_hot_array = [0] * (len(ranges))  # Initialize array with zeros
    if group != 'Other':
        group_index = int(group.split('_')[1]) - 1
        one_hot_array[group_index] = 1  # Set the corresponding index to 1
    else:
        one_hot_array[-1] = 1  # Set the last index to 1 for 'Other' group

    days_of_week = ['FRI', 'MON', 'SAT', 'SUN', 'THURS', 'TUES', 'WEDS']
    one_hot_day = [0] * len(days_of_week)  # Initialize array with zeros
    if day_of_week in days_of_week:
        index = days_of_week.index(day_of_week)
        one_hot_day[index] = 1  # Set the corresponding index to 1
    output = [lateness, is_weekend, is_offpeak]
    for val in one_hot_array:
        output.append(val)
    for val in one_hot_day:
        output.append(val)
    output = np.array(output)
    output = output.reshape(1, -1)
    return output


print(parameterise(-10, 10, 'SAT'))


def predict_lateness(current_station, target, lateness):
    stations = ['LIVST', 'STFD', 'SHENFLD', 'CHLMSFD', 'CLCHSTR', 'MANNGTR', 'IPSWICH', 'STWMRKT', 'DISS', 'NRCH']
    starting_index = stations.index(current_station)
    # starting_index = starting_index + 1
    # parameters = np.array([600,1,1,2,2]) # lateness-weekend-offpeak-day-hour

    hour = datetime.datetime.now().hour
    weekday = datetime.datetime.now().weekday()

    match weekday:
        case 0:
            day = "MON"
        case 1:
            day = "TUE"
        case 2:
            day = "WED"
        case 3:
            day = "THU"
        case 4:
            day = "FRI"
        case 5:
            day = "SAT"
        case 6:
            day = "SUN"
        case _:
            day = "MON"

    parameters = parameterise(lateness, hour, day)

    models = loaded_models

    next_station = stations[starting_index]

    while next_station != target:  # Stop when you reach target
        # Predict lateness at the next station
        next_lateness = models[next_station].predict(parameters)
        parameters[0][0] = next_lateness

        starting_index = starting_index + 1
        next_station = stations[starting_index]

        # Print the predicted lateness for the next station
        print(f"Predicted lateness at {next_station}: ", parameters[0][0], "minutes")

if __name__ == "__main__":

    target = 'NRCH'
    current_station = 'LIVST'
    lateness = 60
    hour = 18
    day = 'SAT'
    predict_lateness(current_station, target, lateness)