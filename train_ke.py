from experta import *
import process_input as pi
from customer_chatbot import input_processing as ip
import problem as prob

class UserIntent(Fact):
    """Information about the user's intent."""
    pass

class Ticket(Fact):
    """Information about the ticket."""
    pass

class Delay(Fact):
    """Information about the train delay."""
    pass

class ProblemReport(Fact):
    """Information about the problem report."""
    pass


class TrainChatBot(KnowledgeEngine):

    @Rule(AS.book_initial << UserIntent(action='buy_ticket', initial_input=MATCH.ii), salience=7)
    def get_initial_booking_info(self, ii, book_initial):
        # Process the initial message to extract as much information as possible
        departure, destination, time, date, adults, children = ip.process_booking_input(ii)

        results = f"Initial Results: {departure}, {destination}, {date}, {time}, {adults}, {children}\n"
        print(results)

        if destination and destination != 'unclear':
            self.declare(Ticket(destination=destination))
        if departure and departure != 'unclear':
            self.declare(Ticket(departure=departure))
        if date and date != 'unclear':
            self.declare(Ticket(date=date))
        if time and time != 'unclear':
            self.declare(Ticket(time=time))
        if adults and adults != 0:
            self.declare(Ticket(adults=adults))
        if children and children != 0:
            self.declare(Ticket(children=children))

    @Rule(AS.book_dest << (UserIntent(action='buy_ticket')) & NOT(Ticket(destination=W())),
          salience=6)
    def ask_destination(self, book_dest):
        print('destination query')
        destination_input = input("trainAI: Please enter the destination station: ")
        departure, destination, current = ip.process_station(destination_input)

        # Handle if there is no suitable input
        while not destination or destination == "unclear":
            destination_input = input("trainAI: Please provide an acceptable departure station name.")
            departure, destination, current = ip.process_station(destination_input)
        print(f"Destination: {destination}")
        self.declare(Ticket(destination=destination))

    @Rule(AS.book_depart << (UserIntent(action='buy_ticket')) & NOT(Ticket(departure=W())),
          salience=5)
    def ask_departure(self, book_depart):
        departure_input = input("trainAI: Please enter the departure station: ")
        departure = ip.process_single_station(departure_input)

        # Handle if there is no suitable input
        while not departure or departure == "unclear":
            departure_input = input("trainAI: Please provide an acceptable departure station name.")
            departure = ip.process_single_station(departure_input)

        print(f"Departure: {departure}")
        self.declare(Ticket(departure=departure))

    @Rule(AS.book_date << (UserIntent(action='buy_ticket')) & NOT(Ticket(date=W())),
          salience=4)
    def ask_date(self, book_date):
        date_input = input("trainAI: Please enter the date of travel: ")
        date = ip.process_date(date_input)

        # Handle if there is no suitable input
        while not date or date == "unclear":
            date_input = input("trainAI: Please provide an acceptable date.")
            date = ip.process_station(date_input)

        print(f"Date: {date}")
        self.declare(Ticket(date=date))

    @Rule(AS.book_time << (UserIntent(action='buy_ticket')) & NOT(Ticket(time=W())),
          salience=3)
    def ask_time(self,book_time):
        time_input = input("trainAI: Please enter the departure time: ")
        time = ip.process_time(time_input)

        # Handle if there is no suitable input
        while not time or time == "unclear":
            time_input = input("trainAI: Please provide an acceptable time.")
            time = ip.process_station(time_input)

        print(time)
        self.declare(Ticket(time=time))

    @Rule(AS.book_pass << (UserIntent(action='buy_ticket')) &
        (NOT(Ticket(adults=0) | Ticket(children=0))),
        salience=2)
    def ask_passenger_info(self, book_pass):
        passenger_input = input("trainAI: Please enter the number of passengers: ")
        adults, children = pi.extract_passenger_numbers(passenger_input)

        # Handle if there is no suitable input
        while (not adults or adults == 0) and (not children or children == 0):
            passenger_input = input("trainAI: Please enter the number of passengers: ")
            adults, children = pi.extract_passenger_numbers(passenger_input)

        print(f"Adults: {adults}, Children: {children}")
        self.declare(Ticket(adults=adults, children=children))

    @Rule(AS.book_report << UserIntent(action='buy_ticket') & Ticket(destination=MATCH.d) & Ticket(departure=MATCH.de) & Ticket(date=MATCH.dt)
           & Ticket(time=MATCH.t) & Ticket(adults=MATCH.a) & Ticket(children=MATCH.c), 
            salience=1)
    def print_report(self, d, de, dt, t, a, c):
        print("trainAI: Ticket information:")
        print(f"Destination: {d}")
        print(f"Departure: {de}")
        print(f"Date: {dt}")
        print(f"Time: {t}")
        print(f"Passengers: {a} Adults, {c} Children")
        
    @Rule(AS.delay_initial << UserIntent(action='check_delay', initial_input=MATCH.ii), salience=5)
    def gather_delay_info(self, ii, delay_initial):
        # Process the initial message to extract as much information as possible
        destination, current, minutes_late = ip.process_delay_input(ii)

        results = f"Initial Results: {destination}, {current}, {minutes_late}\n"
        print(results)

        if destination and destination != 'unclear':
            self.declare(Ticket(destination=destination))
        if current and current != 'unclear':
            self.declare(Ticket(current=current))
        if minutes_late and minutes_late != 'unclear':
            self.declare(Ticket(minutes_late=minutes_late))

    @Rule(AS.delay_dest << (UserIntent(action='check_delay')) & NOT(Ticket(destination=W())),
          salience=4)
    def ask_destination(self, delay_dest):
        print('destination query')
        destination_input = input("trainAI: Please enter the destination station: ")
        destination = ip.process_single_station(destination_input)

        # Handle if there is no suitable input
        while not destination or destination == "unclear":
            destination_input = input("trainAI: Please provide an acceptable destination station name.")
            destination = ip.process_single_station(destination_input)

        print(f"Destination: {destination}")
        self.declare(Ticket(destination=destination))

    @Rule(AS.delay_current << (UserIntent(action='check_delay')) & NOT(Ticket(destination=W())),
          salience=3)
    def ask_current(self, delay_current):
        print('current query')
        current_input = input("trainAI: Please enter the current station: ")
        current = ip.process_single_station(current_input)

        # Handle if there is no suitable input
        while not current or current == "unclear":
            current_input = input("trainAI: Please provide an acceptable current station name.")
            current = ip.process_single_station(current_input)

        print(f"Current: {current}")
        self.declare(Ticket(current=current))

    @Rule(AS.delay_current << (UserIntent(action='check_delay')) & NOT(Ticket(destination=W())),
          salience=2)
    def ask_lateness(self, delay_current):
        print('lateness query')
        lateness_input = input("trainAI: Please enter how late you are: ")
        minutes_late = ip.process_lateness(lateness_input)

        # Handle if there is no suitable input
        while not minutes_late or minutes_late == "unclear":
            lateness_input = input("trainAI: Please provide how late you are.")
            minutes_late = ip.process_lateness(lateness_input)

        print(f"Lateness: {minutes_late}")
        self.declare(Ticket(minutes_late=minutes_late))

    @Rule(UserIntent(action='check_delay') & Ticket(destination=MATCH.d) & Ticket(current=MATCH.c) & Ticket(
        minutes_late=MATCH.ml),
          salience=1)
    def print_report(self, d, c, ml):
        print("trainAI: Ticket information:")
        print(f"Destination: {d}")
        print(f"Current Station: {c}")
        print(f"Minutes Late: {ml}")

    @Rule(UserIntent(action='report_problem'))
    def gather_problem_info(self):
        print("trainAI: Okay, please describe the problem.")
        problem_description = input("trainAI: Please state the problem: ")

        problem = prob.check_problem_by_similarity(problem_description)

        if problem:
            self.declare(ProblemReport(problem_type=problem))

        location = input("trainAI: Please enter the location of the problem: ")

        self.declare(ProblemReport(description=problem_description, location=location))
        print("trainAI: Problem report information:")
        print(f"Description: {problem}")
        print(f"Location: {location}")
    
    @Rule(ProblemReport(problem_type='blockage'))
    def blockage_info(self):
        print('BLOCKAGE ADVICE')

    @Rule(ProblemReport(problem_type='disruption'))
    def disruption_info(self):
        print('DISRUPTION ADVICE')
