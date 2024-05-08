# -*- coding: utf-8 -*-
"""
Created on Wed May  1 10:25:35 2024

@author: dan
"""
import loading_json
from experta import *
import numpy as np
train_schedules = loading_json.import_json()

def convert_to_number(string):
    if string ==None:
        return 0
    if string[-1] == 'H':
        string = string[:-1]  # Remove the last character if it's 'H'
    return int(string)

def check_journey_loc(locations, station):
    "Quickly checks whether a schedule has a certain station and is actually stopping there"
    if locations["tiploc_code"] == station and (locations["departure_time"] is not None):
        return True
    else:
        return False
    
def check_near_time(query_time, target_time, range_value):
    "Check whether a given station time is within the bounds of another "
    "as the station schedules are stupid and don't line up with the documents "
    if query_time["arrival_time"] is not None:
        query_time = convert_to_number(query_time["arrival_time"])
    else:
        query_time = convert_to_number(query_time["departure_time"])
    #target_time = convert_to_number(target_time["arrival_time"])
    return target_time - range_value <= query_time <= target_time + range_value

def get_possible_affected_journeys(input_time, line_block_loc=("LIVST","STRAT")):
    possible_journeys = [] # journeys that take place after the input time
    definitely_cancelled = [] #STOPS that are definitely cancelled
    schedules_affected = [] # schedules that take place after or during the input time
    schedules_cancelled = [] # schedules that have at least one cancelled stop
    #Function that takes in the time. Outputs all trains with arr/dep times proceeding this date
    # for schedule in train_schedules:

    #For trains that have yet to leave today, if the line_block_loc is that station, add it to the CANCELLED list             
    for schedule in train_schedules:
        schedule_locations = schedule["schedule_locations"]

        for locations in schedule_locations:
            #Check departure time is before the input time
            if convert_to_number(locations["departure_time"]) > input_time:
                possible_journeys.append(locations)
                schedules_affected.append(schedule)
                if locations["tiploc_code"] == line_block_loc[0]:
                    definitely_cancelled.append(locations)
                    schedules_cancelled.append(schedule)
    return possible_journeys, schedules_affected,definitely_cancelled,schedules_cancelled
      

              
def evaluate_affected_journeys(cancelled_stops, schedules_cancelled, line_block_loc=("LIVST","STRAT"),time=1030, full_or_part="full"):
    what = []
    for schedule in schedules_cancelled:
        schedule_locations = schedule["schedule_locations"]
        #IF LINEBLOCK OCCURS 
        for locations in schedule_locations:
            if check_journey_loc(locations, "SHENFLD"):
                what.append(schedule_locations)
    #CHECK GOLDEN STATIONS:
    golden = []           
    for stop in cancelled_stops:
        #if stop is a golden stop AND it is within the timeframe - consider it a golden service and flag it
        if check_journey_loc(stop, "SHENFLD") and check_near_time(stop, 806,30):
            print("1Y08 SCHOOL TRAIN")
            golden.append(stop)
        elif check_journey_loc(stop, "SHENFLD") and check_near_time(stop, 736,30):
            print("1F08 SCHOOL TRAIN")
        elif check_journey_loc(stop, "WITHAME") and check_near_time(stop, 1634,30):
            print("1F34 PASSENGERS TO BRAINTREE")
            golden.append(stop) 
        elif check_journey_loc(stop, "WITHAME") and check_near_time(stop, 1720,30):
            print("1F42 PASSENGERS TO BRAINTREE")
            golden.append(stop) 
        elif check_journey_loc(stop, "WITHAME") and check_near_time(stop, 1800,30):
            print("1F48 PASSENGERS TO BRAINTREE")
            golden.append(stop) 
        elif check_journey_loc(stop, "LIVST") and check_near_time(stop, 1722,3):
            print("1J44 PASSENGERS TO SOUTHMINSTER")
            golden.append(stop) 
        elif check_journey_loc(stop, "LIVST") and check_near_time(stop, 1802,3):
            print("1J46 PASSENGERS TO SOUTHMINSTER")
            golden.append(stop) 
        #These are all the golden services that are relevant specifically from LIVST TO NRWCH
        
        special = []           
        for stop in cancelled_stops:
            
            #FILL THIS IN WITH ALL OF THE SPECIAL STOP ORDERS (SEE SECOND DOC) - MAYBE DO A CLEVERER WAY
            if check_journey_loc(stop, "IPSWICH") and check_near_time(stop, 1602,30):
                print("1Y08 SCHOOL TRAIN")
                special.append(stop)
            if check_journey_loc(stop, "IPSWICH") and check_near_time(stop, 1602,30):
                print("1Y08 SCHOOL TRAIN")
                special.append(stop)
            if check_journey_loc(stop, "IPSWICH") and check_near_time(stop, 1602,30):
                print("1Y08 SCHOOL TRAIN")
                special.append(stop)     
            if check_journey_loc(stop, "IPSWICH") and check_near_time(stop, 1602,30):
                print("1Y08 SCHOOL TRAIN")
                special.append(stop)
            if check_journey_loc(stop, "IPSWICH") and check_near_time(stop, 1602,30):
                print("1Y08 SCHOOL TRAIN")
                special.append(stop)  
    return what, golden, special
        #are stranded customers involved? 
        #are the journeys special stop orders?
        #Is the journey a golden service?

        
possible_journeys, possible_schedules_affected, definitely_cancelled_stops, schedules_cancelled = get_possible_affected_journeys(600)

what,golden, special = evaluate_affected_journeys(definitely_cancelled_stops, schedules_cancelled)
#%%
"""
Obtain info:
    It is a full or partial blockage?
    Which station you at?
    What time is it? 
    Who am I talking to? e.g. Manager, signallers, railstaff, passenger etc
    
Output:
    Advice i,e,
    Amended services:
    1 per hour: Greater Anglia Braintree Shuttle--<Operates as Braintree - Witham shuttle>
    1 per hour: Greater Anglia Harwich Shuttle--<Operates as Manningtree-Harwich shuttle>
    

"""

class status(Fact):
    "Contains all info about the event"
    pass

class line_block_loc(Fact):
    "contains 2 station names that has a line blockage"
    pass

class full_or_part(Fact):
    "Full or partial line blockage?"
    pass
    
class time(Fact):
    "Time for the required advice"
    pass

class customer(Fact):
    "Who is the bot talking to?"
    pass
class is_gold(Fact):

    pass
class is_special(Fact):

    pass
class is_stranded_customer(Fact):

    pass

class contingency_expert(KnowledgeEngine):
    #FULL AND TRAINSTAFF
    """
    @Rule(AS.full_or_part << full_or_part(f_or_p =L('full')),
          AS.customer << customer(cust =L('train_staff')))
    def advise_train_staff_full(self, full_or_part, customer):
        print("There is a", full_or_part["f_or_p"], "blockage, and you are a", customer["cust"])
        
    #PARTIAL and TRAIN_STAFF
    @Rule(AS.full_or_part << full_or_part(f_or_p =L('partial')),
          AS.customer << customer(cust =L('train_staff')))
    def advise_train_staff_part(self, full_or_part, customer):
        print("There is a", full_or_part["f_or_p"], "blockage, and you are a", customer["cust"])
    
    """
    #Have a rule that's like 'get the current time and output the possible affected journeys'
    @Rule(status(full_or_part='partial',
                 customer='train_staff'))
    def advise_train_staff_part(self):
        print("There is a partial blockage, and you are a train_staff.")
    
    @Rule(status(full_or_part='full',
                 customer='train_staff'))
    def advise_train_staff_part(self):
        print("There is a full blockage, and you are a train_staff.")
        

#Gather information here:
# Create an instance of the DiagnosisExpert knowledge base
status_data = {
    "full_or_part" : "full",
    "customer" : "train_staff"
    }

#Init the expert
expert = contingency_expert()
expert.reset()


# Add symptoms as facts to the knowledge base
status(status_data=status_data)
expert.declare(status(**status_data))
#expert.declare(full_or_part(f_or_p='full'))
#expert.declare(customer(cust='train_staff'))


# Run the knowledge base to diagnose the illness
expert.run()
