# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 09:02:11 2024

@author: dan
"""
import json

def import_json():
    # Initialize list to store train schedules
    train_schedules = []
    # Load JSON data from file
    with open('livst-nrch.json', 'r') as file:
        for line in file:
            data = json.loads(line)
            
            # Extracting information from JSON
            for schedule_info in data.values():
                # Create dictionary to store schedule information
                schedule_dict = {}
                schedule_dict['train_uid'] = schedule_info['CIF_train_uid']
                schedule_dict['schedule_start_date'] = schedule_info['schedule_start_date']
                schedule_dict['schedule_end_date'] = schedule_info['schedule_end_date']
                schedule_dict['train_status'] = schedule_info['train_status']
                
                # Initialize list to store schedule locations
                schedule_dict['schedule_locations'] = []
                
                # Accessing schedule locations
                for location in schedule_info['schedule_segment']['schedule_location']:
                    location_dict = {}
                    location_dict['tiploc_code'] = location['tiploc_code']
                    location_dict['arrival_time'] = location.get('arrival')
                    location_dict['departure_time'] = location.get('departure')
                    location_dict['platform'] = location.get('platform')
                    location_dict['pass'] = location.get('pass')
                    
                    # Append location dictionary to schedule locations list
                    schedule_dict['schedule_locations'].append(location_dict)
                
                # Append schedule dictionary to train schedules list
                train_schedules.append(schedule_dict)
    return train_schedules
#train_schedules = import_json()
# Print the train schedules (for demonstration purposes)
# for schedule in train_schedules:
#     schedule_locations = schedule["schedule_locations"]
#     if schedule_locations[0]["departure_time"] == "2130":
#         print(schedule_locations[0]["departure_time"], schedule_locations[-1]["arrival_time"], schedule["schedule_start_date"])
    
