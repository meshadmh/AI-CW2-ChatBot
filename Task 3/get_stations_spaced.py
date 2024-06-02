# -*- coding: utf-8 -*-
"""
Created on Fri May 31 09:00:52 2024

@author: dan
"""
import spacy.cli
import warnings
import csv
# Filter out specific warning
warnings.filterwarnings("ignore")

nlp = spacy.load('en_core_web_lg')


#%%
# Load station names from station_names.csv
stations = {
    'STFD': [],
    'SHENFLD': [],
    'CHLMSFD': [],
    'CLCHSTR': [],
    'MANNGTR': [],
    'IPSWICH': [],
    'STWMRKT': [],
    'DISS': [],
    'HAGHLYJ': [],
    'LIVST': []
}

with open("station_names.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        station_code, station_name = row
        station_name = station_name.strip().lower()
        if "STFD" in station_code:
            stations['STFD'].append(station_name)
        elif "SHENFLD" in station_code:
            stations['SHENFLD'].append(station_name)
        elif "CHLMSFD" in station_code:
            stations['CHLMSFD'].append(station_name)
        elif "CLCHSTR" in station_code:
            stations['CLCHSTR'].append(station_name)
        elif "MANNGTR" in station_code:
            stations['MANNGTR'].append(station_name)
        elif "IPSWICH" in station_code:
            stations['IPSWICH'].append(station_name)
        elif "STWMRKT" in station_code:
            stations['STWMRKT'].append(station_name)
        elif "DISS" in station_code:
            stations['DISS'].append(station_name)
        elif "HAGHLYJ" in station_code:
            stations['HAGHLYJ'].append(station_name)
        elif "LIVST" in station_code:
            stations['LIVST'].append(station_name)

#%%
def get_best_station(input_string):
    input_doc = nlp(input_string.lower())
    best_match = None
    highest_similarity = 0

    for station, variations in stations.items():
        for variation in variations:
            variation_doc = nlp(variation)
            similarity = input_doc.similarity(variation_doc)
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = station

    return best_match if best_match else 'unclear'
    
print(get_best_station("colchester"))
# print(get_best_station("ipswitch"))
# print(get_best_station("colchstr"))
# print(get_best_station("shnfield"))
# print(get_best_station("shenfield"))
# print(get_best_station("diss"))
# print(get_best_station("HAGHLYJ"))
# print(get_best_station("clemsford"))
# print(get_best_station("Clemsford "))
# print(get_best_station("liverpol stret "))