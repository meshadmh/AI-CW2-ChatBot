# -*- coding: utf-8 -*-
"""
Created on Fri May 24 18:08:42 2024

@author: dan
"""
import loading_json
from experta.watchers import RULES, AGENDA
from datetime import datetime, timedelta
from experta import *
import numpy as np
import pandas as pd
from tkinter import *


train_schedules = loading_json.import_json()

def unique_dict(list1):

    frozensets = [frozenset(d.items()) for d in list1]
    # Use a set to remove duplicates
    unique_frozensets = set(frozensets)
    # Convert frozensets back to dictionaries
    unique_dicts = [dict(f) for f in unique_frozensets]
    return unique_dicts


def unique_list(list1):
 
    # initialize a null list
    unique_list = []
 
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    return unique_list

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

def add_minutes_to_time_2(time, minutes):
    # Adds minutes to a time in HHMM format
    total_minutes = time_to_minutes(time) + minutes
    return minutes_to_time(total_minutes)

def subtract_minutes_from_time(time, minutes):
    # Subtracts minutes from a time in HHMM format
    total_minutes = time_to_minutes(time) - minutes
    return minutes_to_time(total_minutes)



def filter_schedule(train_schedules, date="2022-12-12"):
    filtered_data = []
    for schedule in train_schedules:
        if schedule["schedule_start_date"] == date:
            filtered_data.append(schedule)
    return filtered_data
    
def get_inbetween_stations(train_schedule, first_station, second_station):
    schedule_locs = train_schedule["schedule_locations"]
    tiploc_codes = [item['tiploc_code'] for item in schedule_locs]
    try:
        start_index = tiploc_codes.index(first_station)
        end_index = tiploc_codes.index(second_station)
    except ValueError:
        print("no such stations in this schedule")
    #if not found, return an empty list
        return []
    return schedule_locs[start_index:end_index+1]

def add_minutes_to_time(time_str, minutes_to_add):
    # Parse the input time string into a datetime object
    if time_str[-1] == 'H':
        time_str = time_str[:-1] 
    time_obj = datetime.strptime(time_str, '%H%M')
    
    # Add the specified number of minutes using timedelta
    new_time_obj = time_obj + timedelta(minutes=minutes_to_add)
    
    # Format the new datetime object back into 'HHMM' format
    new_time_str = new_time_obj.strftime('%H%M')
    
    return new_time_str

def convert_to_number(string):
    if string ==None:
        return 0
    if string[-1] == 'H':
        string = string[:-1]  # Remove the last character if it's 'H'
    return int(string)


def convert_all_to_time(schedules):
    for scheds in schedules:
        locations = scheds['schedule_locations']
        for locs in locations:
            if isinstance(locs['arrival_time'], str):
                locs['arrival_time'] = convert_to_number(locs['arrival_time'])
            # elif locs['arrival_time']is None:
            #     locs['arrival_time'] = 200
            if isinstance(locs['departure_time'], str):
                locs['departure_time'] = convert_to_number(locs['departure_time'])
            # elif locs['departure_time']is None:
            #     locs['departure_time'] = 200
            if isinstance(locs['pass'], str):
                locs['pass'] = convert_to_number(locs['pass'])
            # elif locs['pass']is None:
            #     locs['pass'] = 200
    return schedules

def check_journey_loc(locations, station):
    "Quickly checks whether a schedule has a certain station and is actually stopping there"
    #if locations["tiploc_code"] == station and (locations["departure_time"] is not None):
    if locations["tiploc_code"] == station:
        return True
    else:
        return False
    
def check_near_time(query_time, target_time, range_value):
    "Check whether a given station time is within the bounds of another "
    "as the station schedules are stupid and don't line up with the documents "
    if query_time["arrival_time"] is not None:
        query_time = query_time["arrival_time"]
    elif query_time["departure_time"] is not None:
        query_time = query_time["departure_time"]
    else:
        query_time = query_time["pass"]
    #target_time = convert_to_number(target_time["arrival_time"])
    lower_bound = subtract_minutes_from_time(target_time, range_value)
    upper_bound = add_minutes_to_time_2(target_time, range_value)
    return lower_bound <= query_time <= upper_bound

def check_between_time(query_time, start_time, end_time):
    "Check whether a given station time is within the bounds of another "
    "as the station schedules are stupid and don't line up with the documents "
    if query_time["arrival_time"] is not None:
        query_time = query_time["arrival_time"]
    else:
        query_time = query_time["departure_time"]
    #target_time = convert_to_number(target_time["arrival_time"])
    return start_time <= query_time <= end_time 


def oh_god_why(variable):
    if variable is None:
        return 0
    else:
        return variable

def get_possible_affected_journeys(input_time, train_schedules,line_block_loc):
    possible_journeys = [] # journeys that take place after the input time
    definitely_cancelled = [] #STOPS that are definitely cancelled
    schedules_affected = [] # schedules that take place after or during the input time
    schedules_cancelled = [] # schedules that have at least one cancelled stop
    #Function that takes in the time. Outputs all trains with arr/dep times proceeding this date
    # for schedule in train_schedules:

    #For trains that have yet to leave today, if the line_block_loc is that station, add it to the CANCELLED list             
    for schedule in train_schedules:
        schedule_locations = schedule["schedule_locations"]
        #Check departure time is before the input time
        if oh_god_why(schedule_locations[0]["departure_time"]) > input_time:
            possible_journeys.append(schedule_locations)
            schedules_affected.append(schedule)
            for locations in schedule_locations:
                if locations["tiploc_code"] == line_block_loc[0]:
                    definitely_cancelled.append(locations)
                    schedules_cancelled.append(schedule)
    return possible_journeys, schedules_affected,definitely_cancelled,schedules_cancelled


def get_inbetween_stations(train_schedule, first_station, second_station):
    schedule_locs = train_schedule["schedule_locations"]
    tiploc_codes = [item['tiploc_code'] for item in schedule_locs]
    try:
        start_index = tiploc_codes.index(first_station)
        end_index = tiploc_codes.index(second_station)
    except ValueError:
        print("no such stations in this schedule")
    #if not found, return an empty list
        return []
    return schedule_locs[start_index:end_index+1]

def new_arange(start, end, num):
    def time_to_minutes(time):
        hours = time // 100
        minutes = time % 100
        return hours * 60 + minutes

    def minutes_to_time(minutes):
        hours = minutes // 60
        minutes = minutes % 60
        return hours * 100 + minutes

    start_minutes = time_to_minutes(start)
    end_minutes = time_to_minutes(end)


    times_in_minutes = np.linspace(start_minutes, end_minutes, num)
    times_in_hhmm = [minutes_to_time(t) for t in times_in_minutes]
    
    return times_in_hhmm

def check_cancellation_is_between(start_time,end_time, start_station, end_station, cancellation, range_val=15):

    station_names = get_inbetween_stations(train_schedules[0],start_station, end_station)
    name_list = []

    for station in station_names:
        name_list.append(station['tiploc_code'])
    time_range = new_arange(start_time, end_time, len(name_list))
    for name,time in zip(name_list,time_range):
        if check_journey_loc(cancellation, name) and check_near_time(cancellation, time,range_val):
            return 1

    return 0

def evaluate_affected_journeys(cancelled_stops, schedules_cancelled, line_block_loc=("LIVST","STRAT"),time=1030, full_or_part="full"):

    #CHECK GOLDEN STATIONS:
    golden = []  
    golden_uids = [] 
    school_uids = []        
    for stop,schedu in zip(cancelled_stops,schedules_cancelled):
        #if stop is a golden stop AND it is within the timeframe - consider it a golden service and flag it
        #TODO make this a pandas DF OR SQL?
        #1Y08
        if check_cancellation_is_between(750,930,'LIVST','IPSWICH', stop):
            print("1Y08 SCHOOL TRAIN")
            golden.append(stop)
            school_uids.append(schedu['train_uid'])
        #1F08
        if check_cancellation_is_between(720,835,'LIVST','CLCHSTR', stop):
            print("1F08 SCHOOL TRAIN")
            golden.append(stop) 
            school_uids.append(schedu['train_uid'])
        #1F30
        if check_cancellation_is_between(1548,1607,'LIVST','WITHAME', stop,10):
            print("1F30 SCHOOL TRAIN")
            golden.append(stop) 
            school_uids.append(schedu['train_uid'])
        #PASSENGER LOADINGS    
        #1F34
        if check_cancellation_is_between(1634,1720,'LIVST','WITHAME', stop,10):
            print("1F34 PASSENGERS TO BRAINTREE")
            print("Buses need to be ordered for Witham, including a minibus for Cressing/White Notley")
            golden.append(stop)
            golden_uids.append(schedu['train_uid'])
        #1F42
        if check_cancellation_is_between(1720,1808,'LIVST','WITHAME', stop,10):
            print("1F42 PASSENGERS TO BRAINTREE")
            print("Buses need to be ordered for Witham, including a minibus for Cressing/White Notley")
            golden.append(stop)
            golden_uids.append(schedu['train_uid'])
        #1F48
        if check_cancellation_is_between(1800,1843,'LIVST','WITHAME', stop,10):
            print("1F48 PASSENGERS TO BRAINTREE")
            print("Buses need to be ordered for Witham, including a minibus for Cressing/White Notley")
            golden.append(stop)
            golden_uids.append(schedu['train_uid'])
        
        #1J44
        if check_journey_loc(stop, "LIVST") and check_near_time(stop, 1722,10):
            print("1J44 PASSENGERS TO SOUTHMINSTER")
            print("A minimum of 4 buses need to be requested for Wickford")
            golden.append(stop) 
            golden_uids.append(schedu['train_uid'])
        #1J46
        if check_journey_loc(stop, "LIVST") and check_near_time(stop, 1802,10):
            print("1J46 PASSENGERS TO SOUTHMINSTER")
            print("A minimum of 4 buses need to be requested for Wickford")
            golden.append(stop) 
            golden_uids.append(schedu['train_uid'])
        #These are all the golden services that are relevant specifically from LIVST TO NRWCH
        
    special = []
    special_delays = []      
    delay_seventeenhundred = 0     
    for stop in cancelled_stops:
        
        #Wherever a mainline service is cancelled, terminated short of its booked destination, or started at other
#          than its booked origin special stop orders will generally be issued to the subsequent next service
        #1P44
        if check_cancellation_is_between(1630,1759,'LIVST','DISS', stop,15):
            print("DELAY 1P46 1700 LIVST - NORWICH TRAIN AND CALL ADDITIONALLY AT STOWMARKET 1809")
            delay_seventeenhundred = 1  
            special.append(stop)
            special_delays.append("seventeen_hundred")
        #1Y24
        if check_cancellation_is_between(1602,1707,'LIVST','IPSWICH', stop,15):
            print("DELAY 1N38 16.14 to Clacton TRAIN AND CALL ADDITIONALLY at Hatfield Peverel 16.53 and Witham 16.57")
            special.append(stop)
        #1N38
        if check_cancellation_is_between(1602,1707,'LIVST','CLCHSTR', stop,15):
            print("DELAY 1Y26 16.32 to Ipswich  TRAIN AND CALL ADDITIONALLY at Kelvedon 17.17 and Marks Tey 17:22")
            special.append(stop)
            special_delays.append("sixteen_thirty")
            
        #TODO There's loads left :) 
            
        #GE MAINLINE OFFPEAK SPECIAL STOP ORDERS As all stations except Hatfield Peverel now have two trains per hour off peak, no stop orders should be
        #issued where the next service is known to be running EXCEPT as shown below for Hatfield Peverel.
        #hat_field needs an extra stop from '1Nxx xx.18 Liverpool Street to Clacton each hour'if any of these trains are cancelled (see p9 of spec stop orders)
    hat_field = []
    for x in np.arange(1000,2300,100):
        if check_journey_loc(stop, "LIVST") and check_near_time(stop, x,10):
            hat_field.append(stop)
        elif check_journey_loc(stop, "CLCHSTR") and check_near_time(stop, x,15):
            hat_field.append(stop)
        elif check_journey_loc(stop, "MANNGTR") and check_near_time(stop,x,20):
            hat_field.append(stop)
        elif check_journey_loc(stop, "IPSWICH") and check_near_time(stop, x,15):
            hat_field.append(stop)
    #Possible stranded? If it's the last train of the day and it's cancelled then possibly?
    #If there's not replacement service for >60 minutes then call in alt transport
    alternative_transport = []
    #CHECK: IS THERE A SERVICE RUNNING AFTER THIS ONE? AND IF SO, HOW LONG A WAIT IS IT?
    last_train = []  # connectional policy: if the train is the last one of the day then hold it for longer if trains which have booked connections with other services

    return golden, special, hat_field, special_delays, golden_uids, school_uids



def clean_schedules(train_schedules):
    #REMOVE SCHEDULE LOCATIONS THAT ARE JUST PASSING LOCATIONS - THIS MIGHT ACTUALLY BE USEFUL ACTUALLY BUT WHATEVER
    for schedules in train_schedules:
        schedules["schedule_locations"] = [
            sched_locs for sched_locs in schedules["schedule_locations"]
            if not (sched_locs["arrival_time"] is None and sched_locs["departure_time"] is None)
        ]

    return train_schedules

def get_shuttle_stations(train_schedules, line_bloc_loc):
    #Break the line based on the blockage into the shuttle runs - only for full blockage
    new_schedules = []
    for train_schedule in train_schedules:
        schedule_locs = train_schedule["schedule_locations"]
        tiploc_codes = [item['tiploc_code'] for item in schedule_locs]
        former_stations = []
        latter_stations = []
        line_breakage = 0
        new_former_train_schedule = {}
        new_latter_train_schedule = {}
        for station_data in schedule_locs:
            if (station_data['tiploc_code'] ==line_bloc_loc) and line_breakage == 0:
                line_breakage = 1
                former_stations.append(station_data)
            #if station is blocked, split the jouney
            #All proceeding stations in the for loop
            elif line_breakage:
                latter_stations.append(station_data)
            if line_breakage == 0:
                former_stations.append(station_data)
            
                
        new_former_train_schedule['schedule_locations'] = former_stations 
        new_former_train_schedule['train_uid'] = train_schedule["train_uid"]
          
        new_latter_train_schedule['schedule_locations'] = latter_stations 
        new_latter_train_schedule['train_uid'] = train_schedule["train_uid"] 
        new_schedules.append(new_former_train_schedule)
        new_schedules.append(new_latter_train_schedule)
          
    return new_schedules
        
    #take in line block location and split the journey into the 2 shuttle services UNLESS there's a special circumstance
    #Only for FULL BLOCKAGE

def find_specific_train(schedules, station_name, station_time):
    #Find a train and the matching uids for a given name and time
    matching_schedules = []
    for schedule in schedules:
        schedule_locs = schedule['schedule_locations']

        for loc in schedule_locs:
            if loc['tiploc_code'] == station_name and check_near_time(loc, station_time,10):
                #matching_schedules.append(schedule)
                correct_uid = schedule['train_uid']
    return correct_uid
    

def add_ammended_times(schedules, additional_time, ammend_uid):
    #Add 2 additional keys to each schedule: the new ammended times given an increase in time
    for schedule in schedules:
        schedule_locs = schedule['schedule_locations']
        train_uid = schedule['train_uid']
        for loc in schedule_locs:
            if train_uid == ammend_uid:
                if loc['arrival_time'] is not None:
                    loc['ammended_arr_time'] = add_minutes_to_time_2(loc['arrival_time'],additional_time)
                if loc['departure_time'] is not None:
                    loc['ammended_dep_time'] = add_minutes_to_time_2(loc['departure_time'],additional_time)
    return schedules

def has_amendments(destination):
    """Check if a destination has amended arrival and departure times."""
    return 'ammended_arr_time' in destination or 'ammended_dep_time' in destination
#prev_departure, amended_arrival, prev_departure, amended_departure


def is_overlap(amended_arrival, next_arrival, orig_arrival):
    #Check that the later services are not overlapping with the delayed service
    if amended_arrival is None:
        amended_arrival = 1
    if next_arrival is None:
        next_arrival = 1.01
    if orig_arrival is None:
        orig_arrival = 1.03
    return amended_arrival >= next_arrival and (orig_arrival<=next_arrival)

def is_overlap_previous(amended_arrival, next_arrival, orig_arrival):
    #Checking if the previous jouney now arrives after because delays
    if amended_arrival is None:
        amended_arrival = 1
    if next_arrival is None:
        next_arrival = 1.01
    if orig_arrival is None:
        orig_arrival = 1.03
    return amended_arrival <= next_arrival and (orig_arrival<=next_arrival)


def check_schedules_for_overlaps(schedules):
    """Check for overlaps in the amended schedules."""
    uids_to_change = []
    for j, schedule in enumerate(schedules):
        schedule_locations = schedule.get('schedule_locations', [])
        
        if (j >0):
            prev_schedule = schedules[j-1]
            prev_schedule_locations = prev_schedule.get('schedule_locations', [])
            #If the journies have been split into shuttles the previous jounrey will match 2 schedules away
            if (prev_schedule_locations[0]['tiploc_code'] != schedule_locations[0]['tiploc_code']) and (j>1):
                prev_schedule = schedules[j-2]
                prev_schedule_locations = prev_schedule.get('schedule_locations', [])   
            #CHECK PREVIOUS JOURNEY
            if (j < len(schedules) -1 ):
                next_schedule = schedules[j+1]
                next_schedule_locations = next_schedule.get('schedule_locations', [])
            for destination in schedule_locations:
                for prev_destination in prev_schedule_locations:
                    if has_amendments(destination) and (prev_destination['tiploc_code']==destination['tiploc_code']):
                        # Parse amended times
                        amended_arrival = destination.get('ammended_arr_time',destination['arrival_time'])
                        amended_departure = destination.get('ammended_dep_time',destination['departure_time'])
                        orig_arrival = destination['arrival_time']
                        orig_departure = destination['departure_time']
                        prev_arrival = prev_destination.get('ammended_arr_time',prev_destination['arrival_time'])
                        prev_departure = prev_destination.get('ammended_dep_time',prev_destination['departure_time'])
                        if is_overlap_previous(amended_arrival,prev_arrival,orig_arrival):
                            prev_destination['ammended_arr_time'] = add_minutes_to_time_2(amended_arrival,-5)
                            #print(amended_arrival, prev_arrival, destination['tiploc_code'], "prev")
                            uids_to_change.append(prev_schedule["train_uid"])
                        elif is_overlap_previous(amended_departure,prev_departure,orig_departure):
                            uids_to_change.append(prev_schedule["train_uid"])
                            prev_destination['ammended_dep_time'] = add_minutes_to_time_2(amended_departure,-5)
                            #print(amended_departure, prev_departure, destination['tiploc_code'], "prevd")
            #CHECK NEXT JOURNEY
            if (next_schedule_locations[0]['tiploc_code'] != schedule_locations[0]['tiploc_code']) and (j < len(schedules) - 2):
                next_schedule = schedules[j+2]
                next_schedule_locations = next_schedule.get('schedule_locations', [])    
            for destination in schedule_locations:
                for next_destination in next_schedule_locations:

                    if has_amendments(destination) and (next_destination['tiploc_code']==destination['tiploc_code']):
                        # Parse amended times
                        amended_arrival = destination.get('ammended_arr_time',destination['arrival_time'])
                        amended_departure = destination.get('ammended_dep_time',destination['departure_time'])
                        orig_arrival = destination['arrival_time']
                        orig_departure = destination['departure_time']
                        next_arrival = next_destination.get('ammended_arr_time',next_destination['arrival_time'])
                        next_departure = next_destination.get('ammended_dep_time',next_destination['departure_time'])
                        if is_overlap(amended_arrival,next_arrival,orig_arrival):
                            #Make next_arrival 5 min after amended arrival
                            uids_to_change.append(next_schedule["train_uid"])
                            next_destination['ammended_arr_time'] = add_minutes_to_time_2(amended_arrival,5)
                            #print("new revised schedule",next_destination['ammended_arr_time'])
                            #print(amended_arrival, next_arrival, destination['tiploc_code'])
                        elif is_overlap(amended_departure,next_departure,orig_departure):
                            #uids_to_change.append(next_schedule["train_uid"])
                            uids_to_change.append(next_schedule["train_uid"])
                            next_destination['ammended_dep_time'] = add_minutes_to_time_2(amended_departure,5)
                            #print(amended_departure, next_departure, destination['tiploc_code'])
    return schedules, uids_to_change
         
def adjust_schedule(schedule, train, train_time, time_to_adjust):

    ammend_uid = find_specific_train(schedule, 'LIVST', train_time)
    #Takes that UID and adds 'ammended_depature_time' and 'ammended_arr_time'  to the specific train schedules
    ammended_schedules = add_ammended_times(schedule,time_to_adjust, ammend_uid) 
    new_ammended_schedule, changed_uids = check_schedules_for_overlaps(ammended_schedules)
    print("---------------------")
    return new_ammended_schedule, changed_uids, ammend_uid

def identify_uid(schedules, uid):
    journeys_relevant = []
    for schedule in schedules:
        schedule_uid_loop = schedule['train_uid']
        if schedule_uid_loop == uid:
            journeys_relevant.append(schedule['schedule_locations'])

    return journeys_relevant

#TODO make these ammended
def print_affected_journey(journeys, line_block_loc):
    print_str = []
    for journey in journeys:
        leg_one = 0
        if journey[-1]['tiploc_code'] == line_block_loc:
            leg_one = 1

        if journey[0]['departure_time'] is not None and leg_one:

            print_statement = f"Station: {journey[0]['tiploc_code']} --> {line_block_loc} | Leaving: {journey[0]['departure_time']}"
            print_str.append(print_statement)
                    
        elif journey[0]['departure_time'] is not None:
            print_statement = f"Station: {journey[0]['tiploc_code']} --> {journey[-1]['tiploc_code']} | Leaving: {journey[0]['departure_time']}"
            print_str.append(print_statement)
            next_important_station = journey[0]['tiploc_code']
            print(f"Alternative transport required from {line_block_loc} to {next_important_station}")
            print_statement = f"Alternative transport required from {line_block_loc} to {next_important_station}"
            print_str.append(print_statement)
        else:
            for destination in journey:
                if destination['departure_time'] is not None:
                    print_statement = f"Station: {destination['tiploc_code']} --> {journey[-1]['tiploc_code']} | Leaving: {destination['departure_time']}"
                    print_str.append(print_statement)
                    next_important_station = destination['tiploc_code']
                    print(f"Alternative transport required from {line_block_loc} to {next_important_station}")
                    print_statement = f"Alternative transport required from {line_block_loc} to {next_important_station}"
                    print_str.append(print_statement)
                    break

                    
    return print_str

def print_affected_journey_special(journeys, line_block_loc):
    out_str = ""
    print_str = []
    for journey in journeys:
        leg_one = 0
        if journey[-1]['tiploc_code'] == line_block_loc:
            leg_one = 1

        if journey[0]['departure_time'] is not None and leg_one:

            out_str += f"I've changed the journey:\nStation: {journey[0]['tiploc_code']} --> {line_block_loc} | Leaving: {journey[0]['departure_time']}\nTo:\nStation: {journey[0]['tiploc_code']} --> {line_block_loc} | Leaving: {journey[0]['ammended_dep_time']}\n"
            print_statement = f"I've changed the journey:\nStation: {journey[0]['tiploc_code']} --> {line_block_loc} | Leaving: {journey[0]['departure_time']}\nTo:\nStation: {journey[0]['tiploc_code']} --> {line_block_loc} | Leaving: {journey[0]['ammended_dep_time']}"
            print_str.append(print_statement)
        #leg 2            
        elif journey[0]['departure_time'] is not None:
            out_str +=f"I've changed the journey:\nStation: {journey[0]['tiploc_code']} --> {journey[-1]['tiploc_code']} | Leaving: {journey[0]['departure_time']}\nTo:\nStation: {journey[0]['tiploc_code']} --> {journey[-1]['tiploc_code']} | Leaving: {journey[0]['ammended_dep_time']}\n"
            print_statement = f"I've changed the journey:\nStation: {journey[0]['tiploc_code']} --> {journey[-1]['tiploc_code']} | Leaving: {journey[0]['departure_time']}\nTo:\nStation: {journey[0]['tiploc_code']} --> {journey[-1]['tiploc_code']} | Leaving: {journey[0]['ammended_dep_time']}"
            next_important_station = journey[0]['tiploc_code']
            out_str += f"Alternative transport required  from {line_block_loc} to {next_important_station}\n"
            print(f"Alternative transport required  from {line_block_loc} to {next_important_station}")
            print_str.append(print_statement)
            print_statement = f"Alternative transport required from {line_block_loc} to {next_important_station}\n"
            print_str.append(print_statement)
        else:
            for destination in journey:
                if destination['departure_time'] is not None:
                    out_str +=f"I've changed the journey:\nStation: {destination['tiploc_code']} --> {journey[-1]['tiploc_code']} | Leaving: {destination['departure_time']}\nTo:\nStation: {destination['tiploc_code']} --> {journey[-1]['tiploc_code']} | Leaving: {destination['ammended_dep_time']}\n"
                    print_statement = f"I've changed the journey:\nStation: {destination['tiploc_code']} --> {journey[-1]['tiploc_code']} | Leaving: {destination['departure_time']}\nTo:\nStation: {destination['tiploc_code']} --> {journey[-1]['tiploc_code']} | Leaving: {destination['ammended_dep_time']}"
                    print_str.append(print_statement)
                    next_important_station = destination['tiploc_code']
                    out_str += f"Alternative transport required from {line_block_loc} to {next_important_station}\n"
                    print_statement = f"Alternative transport required from {line_block_loc} to {next_important_station}\n"
                    print_str.append(print_statement)
                    print(f"Alternative transport required from {line_block_loc} to {next_important_station}")
                    break
    return print_str #,out_str

def adjust_all_schedules(schedule, special_delays):
    changed_uids = []
    original_special_journey = [] # journey that's held
    for delay in special_delays:
        if delay== 'seventeen_hundred':
            schedule, new_uids, ammend_uid = adjust_schedule(schedule, 'LIVST', 1700,35)
            changed_uids.append(new_uids)
            original_special_journey.append(ammend_uid)
        if delay =='sixteen_thirty':
            schedule, new_uids, ammend_uid = adjust_schedule(schedule, 'LIVST', 1630,35)
            changed_uids.append(new_uids)
            original_special_journey.append(ammend_uid)
            #TODO add more here for each special stop
    return changed_uids, original_special_journey




def get_summary_advice(new_schedules,school_uids, golden_uids,special_uids,original_special_uids, line_block_location):
    out_string = ""
    if len(school_uids) > 0:
        out_string +="Below are the affected School journeys - These will have many school children on!\n"
        out_string +="--------------------------------------------------------------------\n"
        print("Below are the affected School journeys - These will have many school children on!")
        for uid in school_uids:
            journey = identify_uid(new_schedules, uid)
            #print("This journey is a heavy school loading train: starting",journey[0][0]['tiploc_code'], "at time",journey[0][0]['departure_time'])
            statement = print_affected_journey(journey,line_block_location)
            
            for stat in statement:
                out_string += stat
                out_string += '\n'
                print(stat)
            out_string += "--------------------------------------------------------------------\n"
            print("--------------------------------------------------------------------")
        out_string +="Please consider informing the school and how the children will be guided.\n"
        print("Please consider informing the school and how the children will be guided. ")
        out_string +="--------------------------------------------------------------------\n"
        print("--------------------------------------------------------------------")
    #PASSENGER LOADINGS
    if len(golden_uids) > 0:
        out_string +="Shown below are the affected services that are know for heavy passenger loadings:\n"
        out_string +="--------------------------------------------------------------------\n"
        print("Shown below are the affected services that are know for heavy passenger loadings:")
        for uid in golden_uids:
            journey = identify_uid(new_schedules, uid)
            #print("This journey is a heavy school loading train: starting",journey[0][0]['tiploc_code'], "at time",journey[0][0]['departure_time'])
            statement = print_affected_journey(journey,line_block_location)
            
            for stat in statement:
                out_string += stat
                out_string += '\n'
                print(stat)
            out_string += "--------------------------------------------------------------------\n"
            print("--------------------------------------------------------------------")
        out_string += "Please consider how the high number of passengers will be dealt with.\n"
        out_string +="--------------------------------------------------------------------\n"
        print("Please consider how the high number of passengers will be dealt with.")
        
    if len(original_special_uids) > 0:
        out_string +="Shown below are SPECIAL services that will be disrupted. Since an important journey is being disrupted, the following stations must be held until shown:\n"
        out_string +="--------------------------------------------------------------------\n"
        print("Shown below are SPECIAL services that will be disrupted. Since an important journey is being disrupted, the following stations must be held until shown:\n")
        for uid in original_special_uids:
            journey = identify_uid(new_schedules, uid)
            #print("This journey is a heavy school loading train: starting",journey[0][0]['tiploc_code'], "at time",journey[0][0]['departure_time'])
            statement = print_affected_journey_special(journey,line_block_location)
            #out_string += output
            out_string +='\n'
            for stat in statement:
                out_string += stat
                out_string += '\n'
                print(stat)
            out_string +="--------------------------------------------------------------------\n"
            print("--------------------------------------------------------------------")
        out_string +="Please consider how the high number of passengers will be dealt with.\n"
        out_string +="--------------------------------------------------------------------\n"
        print("Please consider how the high number of passengers will be dealt with.\n")
        #TODO print statement here checking if there not all empty, in which case say 'great' or whatver
    return out_string 
    # if len(special_uids) > 0:
        # print("Shown below are SPECIAL services that will be disrupted. Since an important journey is being disrupted, the next:")
        # for uid in original_special_uids:
        #     journey = identify_uid(new_schedules, uid)
        #     #print("This journey is a heavy school loading train: starting",journey[0][0]['tiploc_code'], "at time",journey[0][0]['departure_time'])
        #     statement = #PRINT THE AMENDED SERVICES HERE
        # print("Please consider how the high number of passengers will be dealt with.")
    #Needs to identify which journeys are special, and how they have been amended

def get_all_schedule_advice(line_block_location, time, train_schedules):
                                 
    train_schedules = filter_schedule(train_schedules)
    train_schedules = convert_all_to_time(train_schedules)

    new_schedules = get_shuttle_stations(train_schedules,line_block_location)

    possible_journeys, possible_schedules_affected, definitely_cancelled_stops, schedules_cancelled = get_possible_affected_journeys(
        time,new_schedules,(line_block_location,"ILFORD"))

    golden, special, hat_field, special_delays, golden_uids, school_uids = evaluate_affected_journeys(
        definitely_cancelled_stops, schedules_cancelled)

    special_affected_uids, special_journey_uids = adjust_all_schedules(new_schedules,special_delays)
    special_affected_uids = unique_list(special_affected_uids)
    special_journey_uids = unique_list(special_journey_uids)
    golden_uids = unique_list(golden_uids)

    out_str = get_summary_advice(new_schedules,school_uids, golden_uids, special_affected_uids, special_journey_uids, line_block_location)
    
    return out_str