# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 13:33:45 2024

@author: dan
"""


from datetime import datetime, timedelta
import pickle
import numpy as np
import warnings

warnings.filterwarnings('ignore')


def load_models():
    loaded_station_names = ['LIVST', 'STFD', 'SHENFLD', 'CHLMSFD', 'CLCHSTR', 'MANNGTR', 'IPSWICH', 'STWMRKT', 'DISS']
    # Load the models from files
    loaded_model_dict = {}
    for station_name in loaded_station_names:
        with open(f'Task_2/{station_name}_model_knn_not_imputed_NEW.pkl', 'rb') as model_file:
            loaded_model_dict[station_name] = pickle.load(model_file)

    return loaded_model_dict

def time_to_minutes(time):
    # Converts a time in HHMM format to the total number of minutes since midnight
    hours = time // 100
    minutes = time % 100
    return hours * 60 + minutes

def minutes_to_time(minutes):
    # Converts the total number of minutes since midnight to a time in HHMM format
    hours = minutes // 60
    minutes = minutes % 60
    return hours * 100 + minutes


def add_minutes_to_time(time_str, minutes_to_add):
    # Parse the input time string into a datetime object
    if time_str[-1] == 'H':
        time_str = time_str[:-1] 
    time_obj = datetime.strptime(time_str, '%H%M')
    
    # Add the specified number of minutes using timedelta
    new_time_obj = time_obj + timedelta(minutes=minutes_to_add)
    
    # Format the new datetime object back into 'HHMM' format
    new_time_str = new_time_obj.strftime('%H:%M')
    
    return new_time_str



#%%
# MANUALLY CHANGE THE OPENING NAME
loaded_models = load_models()





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

def convert_station(current_station):
    
    if current_station =="STRATFORD":
        current_station = "STFD"
    if current_station =="SHENFIELD":
        current_station = "SHNFLD"
    if current_station =="CHELMSFORD":
        current_station = "CHLMSFD"
    if current_station =="COLCHESTER":
        current_station = "CLCHSTR"
    if current_station =="MANNINGTREE":
        current_station = "MANNGTR"
    if current_station =="DERBY ROAD":
        current_station = "IPSWICH"
    if current_station =="STOWMARKET":
        current_station = "STWMRKT"

    if current_station =="NORWICH":
        current_station = "NRCH"
    if current_station =="LIVERPOOL STREET":
        current_station = "LIVST"
        
    return current_station

def predict_lateness(current_station, target, lateness):
    current_station = convert_station(current_station)
    stations = ['LIVST', 'STFD', 'SHENFLD', 'CHLMSFD', 'CLCHSTR', 'MANNGTR', 'IPSWICH', 'STWMRKT', 'DISS', 'NRCH']
    starting_index = stations.index(current_station)
    time_between_stations = [20,10,30,15,18,19,20,10,9] #TODO  FILL THESE IN WITH CORRECT VALUES
    end_index = stations.index(target)
    time_of_journey = sum(time_between_stations[starting_index:end_index])
    # starting_index = starting_index + 1
    # parameters = np.array([600,1,1,2,2]) # lateness-weekend-offpeak-day-hour

    hour = datetime.now().hour
    weekday = datetime.now().weekday()


    if weekday == 0:
        day = "MON"
    elif weekday == 1:
        day = "TUES"
    elif weekday == 2:
        day = "WEDS"
        
    elif weekday == 3:
        day = "THURS"
    elif weekday == 4:
        day = "FRI"
    elif weekday == 5:
        day = "SAT"
    elif weekday == 6:
        day = "SUN"
    else:
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
        if next_station == target:
            c = datetime.now()
            current_time = c.strftime('%H%M')
            arr_time = add_minutes_to_time(current_time, parameters[0][0] +time_of_journey)
            out_string = f"Your train will be {parameters[0][0]} minutes late, and will arrive at {arr_time}."
            print(arr_time)
            return out_string

        # Print the predicted lateness for the next station
        #print(f"Predicted lateness at {next_station}: ", parameters[0][0], "minutes")

if __name__ == "__main__":
    
    
    target = 'NRCH'
    current_station = 'LIVST'
    lateness = 60
    hour = 18
    day = 4
    predict_lateness(current_station, target, lateness)