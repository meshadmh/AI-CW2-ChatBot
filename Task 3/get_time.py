# -*- coding: utf-8 -*-
"""
Created on Fri May 31 11:15:18 2024

@author: dan
"""

import spacy.cli
import warnings
import dateparser
from datetime import datetime
import re
# Filter out specific warning
warnings.filterwarnings("ignore")

nlp = spacy.load('en_core_web_lg')

def process_time(input_time):
    # Check if the input is already in HHMM format
    hhmm_pattern = re.compile(r'^\d{3,4}$')
    if hhmm_pattern.match(input_time):
        # Parse the HHMM input directly
        # if len(input_time) == 3:
        #     input_time = "0" + input_time  # Prepend a zero if the input is in HMM format

        try:
            hhmm_time = int(input_time)
            return hhmm_time
        except ValueError:
            return 'unclear'

    doc = nlp(input_time)
    time_ent = ""

    for ent in doc.ents:
        if ent.label_ == "TIME":
            time_ent = ent.text

    # Parse the input time string
    parsed_date = dateparser.parse(time_ent, settings={'PREFER_DATES_FROM': 'future'})

    # Extract and format time
    if parsed_date is not None:
        parsed_time = parsed_date.time()
        hhmm_time = parsed_time.strftime("%H%M")
        return int(hhmm_time)
    else:
        return 'unclear'
    
# print(process_time("Seven o'clock"))
# print(process_time("7:00 AM"))
# print(process_time("midnight"))
# print(process_time("noon"))
# print(process_time("half past six in the morning"))
# print(process_time("quarter to nine in the evening"))
# print(process_time("761"))

# print(process_time("700"))     
# print(process_time("1700"))    
# print(process_time("7:00 AM")) 
# print(process_time("5 PM"))    
# print(process_time("noon"))    