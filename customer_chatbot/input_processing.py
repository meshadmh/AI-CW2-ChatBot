"""
Input Processing Functions:
Uses SPACY NLP to handle the extraction of relevant entities from a given input

@author Jenna
26.05.24
"""
# Import Packages
import spacy
from spacy.matcher import Matcher
from word2number import w2n
import dateparser
from datetime import datetime


# Import Files
import stations
import intentions_cdb as intent
import problemtype_cbd as problem
import railcard_cdb as rc

# Load language model
nlp = spacy.load('en_core_web_lg')

""" Functions for extracting targeted entity information"""


def process_intention(input_intent):
    # Identify intention of message
    intention = intent.get_similar_intention(input_intent)
    return intention


def process_station(input_station):
    # Initialize the Matcher
    matcher = Matcher(nlp.vocab)

    # Set up matching patterns for departure and destination
    departure_pattern = [{"LOWER": {"IN": ["from", "departing", "depart", "leaving"]}}, {"POS": "PROPN"}]
    destination_pattern = [{"LOWER": {"IN": ["to", "heading", "towards"]}}, {"POS": "PROPN"}]
    current_pattern = [{"LOWER": {"IN": ["at"]}}, {"POS": "PROPN"}]

    # Add patterns to the Matcher
    matcher.add("DEPARTURE", [departure_pattern])
    matcher.add("DESTINATION", [destination_pattern])
    matcher.add("CURRENT", [current_pattern])

    # Compare extracted text to matcher patterns
    doc = nlp(input_station)
    matches = matcher(doc)

    departure = None
    destination = None
    current = None

    for token in doc:
        if token.text.lower() in ["from", "departing", "depart", "leaving"]:
            departure = stations.check_station_name(token.nbor().text)
        elif token.text.lower() in ["to", "heading", "towards"]:
            destination = stations.check_station_name(token.nbor().text)
        elif token.text.lower() == "at":
            current = stations.check_station_name(token.nbor().text)


    # # Iterate over the matcher results
    # for match_id, start, end in matches:
    #     label = nlp.vocab.strings[match_id]
    #     print("Matched label:", label, "Start:", start, "End:", end)
    #     token = doc[start]
    #     if label == "DEPARTURE":
    #         if token.i < len(doc) - 1:  # Ensure there is a next token
    #             departure = stations.check_station_name(token.nbor().text)
    #     elif label == "DESTINATION":
    #         if token.i < len(doc) - 1:  # Ensure there is a next token
    #             destination = stations.check_station_name(token.nbor().text)
    #     elif label == "CURRENT":
    #         if token.i < len(doc) - 1:  # Ensure there is a next token
    #             current = stations.check_station_name(token.nbor().text)

    return departure, destination, current

def process_single_station(input_single_station):
    station = stations.check_station_name(input_single_station)
    return station


def process_date(input_date):
    doc = nlp(input_date)
    date_ent = ""

    for ent in doc.ents:
        if ent.label_ == "DATE":
            date_ent = ent.text
    # Parse the input date string
    parsed_date = dateparser.parse(date_ent)

    # Extract and format time
    if parsed_date is not None:
        ddmm_date = parsed_date.strftime("%d/%m/%Y")
        return ddmm_date
    else:
        return 'unclear'


def process_time(input_time):
    doc = nlp(input_time)
    time_ent = ""

    for ent in doc.ents:
        if ent.label_ == "TIME":
            time_ent = ent.text

    # Parse the input time string
    parsed_date = dateparser.parse(time_ent)

    # Extract and format time
    if parsed_date is not None:
        parsed_time = parsed_date.time()
        hhmm_time = parsed_time.strftime("%H%M")
        return hhmm_time
    else:
        return 'unclear'

def process_hour(input_hour):
    doc = nlp(input_hour)
    time_ent = ""

    for ent in doc.ents:
        if ent.label_ == "TIME":
            time_ent = ent.text

    # Parse the input time string
    parsed_date = dateparser.parse(time_ent)

    # Extract and format time
    if parsed_date is not None:
        parsed_time = parsed_date.time()
        hhmm_time = parsed_time.strftime("%H")
        return hhmm_time
    else:
        return 'unclear'


def process_passengers(input_passengers):
    doc = nlp(input_passengers)

    # Initialise counters for adults and children
    adult_count = 0
    child_count = 0

    # Loop through each token in the processed text
    i = 0
    while i < len(doc):
        token = doc[i]

        # Check if the token is a number
        if token.is_digit or token.like_num:
            # convert written number to integer if needed
            try:
                number = w2n.word_to_num(token.text) if token.like_num else int(token.text)
            except ValueError:
                # If conversion fails, move to the next token
                i += 1
                continue

            # Check if the next token represents "adult" or "child" variations
            # If no age signifier is given, assume adults
            if i < len(doc) - 1:
                if token.nbor().text.lower() in ('adult', 'adults', 'passenger', 'passengers', 'ticket', 'tickets',
                                                 'people', 'person'):
                    adult_count += number
                elif token.nbor().text.lower() in ('child', 'children', 'kid', 'kids'):
                    child_count += number
                # Move to next token, skipping over 'adult/child' token
                i += 2
            else:
                break
        else:
            i += 1

    # Return the counts of adults and children
    return adult_count, child_count


def process_lateness(input_lateness):
    doc = nlp(input_lateness)

    # Initialise counters for minutes
    minutes_late = 0

    # Loop through each token in the processed text
    i = 0

    # Handle cases where 'hour' is part of a larger phrase
    skip_next_hour = False

    while i < len(doc):
        token = doc[i]

        # Handle non-plural hour, half, quarter and minute
        if token.text.lower() == "hour":
            if skip_next_hour:
                skip_next_hour = False
                break
            else:
                minutes_late += 60
        elif token.text.lower() == "minute":
            minutes_late += 1
        elif token.text.lower() == "quarter":
            skip_next_hour = True
            minutes_late += 15
        elif token.text.lower() == "half":
            skip_next_hour = True
            minutes_late += 30

        # handle three quarters of an hour - assumption this is the only instance to use plural 'quarters'
        elif token.text.lower() == "quarters":
            skip_next_hour = True
            minutes_late += 45

        # Handle of hours and minutes
        # Check if the token is a number
        elif token.is_digit or token.like_num:
            # convert written number to integer if needed
            try:
                number = w2n.word_to_num(token.text) if token.like_num else int(token.text)
            except ValueError:
                # If conversion fails, move to the next token
                i += 1
                continue

            # Check if the next token represents "minutes" or "hour"
            if i < len(doc) - 1:
                if token.nbor().text.lower() == "minutes":
                    minutes_late += number
                elif token.nbor().text.lower() == "hours":
                    if skip_next_hour:
                        skip_next_hour = False
                        break
                    else:
                        minutes_late += (60 * number)
            else:
                break

        i += 1

    return minutes_late


def process_problem(input_problem):
    # Identify problem type
    problem_type = problem.get_blockage_type(input_problem)
    return problem_type


def process_staff(input_staff):
    # Initialize the Matcher
    matcher = Matcher(nlp.vocab)

    # Set up matching patterns for departure and destination
    manager_pattern = [{"LOWER": {"IN": ["manager", "head"]}}, {"POS": "PROPN"}]
    rail_staff_pattern = [{"LOWER": "rail"}, {"LOWER": "staff"}, {"POS": "PROPN"}]
    signaller_pattern = [{"LOWER": {"IN": ["signaller", "controller"]}}, {"POS": "PROPN"}]

    # Add patterns to the Matcher
    matcher.add("DEPARTURE", [manager_pattern])
    matcher.add("DESTINATION", [rail_staff_pattern])
    matcher.add("CURRENT", [signaller_pattern])

    # Compare extracted text to matcher patterns
    doc = nlp(input_staff)
    matches = matcher(doc)
    staff_type = None

    for token in doc:
        if token.text.lower() in ["manager", "head"]:
            staff_type = "manager"
        elif token.text.lower() in ["rail", "station"] and token.nbor().text in ["staff", "employee"]:
            staff_type = "rail staff"
        elif token.text.lower() in ["signaller", "controller"]:
            staff_type = "signaller"

    # # Identify problem type
    # staff_type = staff.get_staff_type(input_staff)
    return staff_type


def process_railcard(input_railcard):
    doc1 = nlp(input_railcard)
    railcard = 0
    for token in doc1:
        if token.text.lower() in ["railcard", "card"]:
            railcard = rc.get_railcard(input_railcard)
        if railcard != 0:
            break

    return railcard


""" Functions for extracting as much information as possible from an initial input """


def process_booking_input(initial_input):
    departure, destination, current = process_station(initial_input)
    # time = process_time(initial_input)
    time = process_hour(initial_input)
    date = process_date(initial_input)
    adults, children = process_passengers(initial_input)
    railcard = process_railcard(initial_input)

    return departure, destination, time, date, adults, children, railcard


def process_delay_input(initial_input):
    departure, destination, current = process_station(initial_input)
    minutes_late = process_lateness(initial_input)

    return destination, current, minutes_late


def process_problem_input(initial_input):
    problem_type = problem.get_blockage_type(initial_input)
    staff_type = process_staff(initial_input)
    departure, destination, current = process_station(initial_input)

    time = datetime.now().time()
    hhmm_time = time.strftime("%H%M")

    return problem_type, staff_type, current, hhmm_time


""" Function for cleaning inputs """


def lemmatize_and_clean(input):
    doc = nlp(input.lower())
    out = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return " ".join(out)


if __name__ == "__main__":
    # TESTING INPUTS HERE
    input = "i have a dcg railcard."
    print("\nInput: ", input)
    print("Railcard: ", process_railcard(input))

    # input = "3 adults and two children for Norwich"
    # print("\nInput: ", input)
    # print("Passengers: ", process_passengers(input))
    #
    # input = "3rd of May"
    # print("\nInput: ", input)
    # print("Date: ", process_date(input))
    #
    # input = "seven am"
    # print("\nInput: ", input)
    # print("Time: ", process_time(input))
    #
    # input = "I'm seven minutes and half an hour late."
    # print("\nInput: ", input)
    # print("Minutes Late: ", process_lateness(input))
    #
    # input = "I want to check a delay going from ipswich to colchester"
    # print("\nInput: ", input)
    # print("Intention: ", process_intention(input))
    # print("Stations: ", process_station(input))
    #
    # input = "I would like to buy a ticket from norwich to ipswich for four passengers at 7 am on the 3rd of May"
    # print("\nInput: ", input)
    # print("Intention: ", process_intention(input))
    # print("Booking Info: ", process_booking_input(input))
    #
    # input = "I am delayed by forty minutes at colchester heading  to stratford"
    # print("\nInput: ", input)
    # print("Intention: ", process_intention(input))
    # print("Delay Info: ", process_delay_input(input))
    #
    # input = "I am a rail staff looking for help. There's a rock blocking part of the line at Norwich."
    # print("\nInput: ", input)
    # print("Intention: ", process_problem(input))
    # print("Delay Info: ", process_problem_input(input))



