# -*- coding: utf-8 -*-
"""
@author: Jenna, adapted from code from Dan (KE)  and Mesha (GUI)
"""

# IMPORT LIBRARIES
from experta import *
import tkinter as tk
import warnings
import time as tm
import re
import webbrowser

# IMPORT PACKAGES
import intentions_cdb as intentions
import input_processing as ip
import Webscraping
import predict_delay

# Filter out specific warning
warnings.filterwarnings("ignore")

# DEFINE CHATBOT APP
BG_GRAY = "gainsboro"
BG_COLOUR = "lavender"
TEXT_COLOUR = "black"
FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

class ChatBot:
    def __init__(self):
        self.reinput = False   # Flag for handling cases where unclear information is given
        self.window = tk.Tk()
        self._setup_main_window()
        self.initial_message()

    def run(self):
        self.window.mainloop()

    def _setup_main_window(self):
        self.window.title("Chatbot")
        self.window.resizable(width=False, height=False)
        self.window.geometry("800x600")

        # head label
        head_label = tk.Label(self.window, bg=BG_COLOUR, fg=TEXT_COLOUR,
                           text="Welcome!", font=FONT, pady=10)
        head_label.pack(fill=tk.X)

        # divider
        line = tk.Label(self.window, width=500, bg=BG_GRAY)
        line.pack(fill=tk.X)

        # Text widget frame
        text_frame = tk.Frame(self.window, bg=BG_COLOUR)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Text widget
        self.text_widget = tk.Text(text_frame, width=20, height=2, bg=BG_COLOUR, fg=TEXT_COLOUR,
                                font=FONT, padx=5, pady=5, wrap=tk.WORD)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_widget.configure(cursor="arrow", state=tk.DISABLED)

        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame, command=self.text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget['yscrollcommand'] = scrollbar.set

        # Bottom label
        bottom_label = tk.Label(self.window, bg=BG_COLOUR, height=80)
        bottom_label.pack(fill=tk.X)
        print("bottom label")

        # message frame
        message_frame = tk.Frame(bottom_label, bg=BG_COLOUR, pady=5)
        message_frame.pack(fill=tk.X)
        print("message frame")

        # message label
        message_label = tk.Label(message_frame, text="Type your message here: ", font=FONT, fg="black")
        message_label.pack(side=tk.LEFT)
        print("message label")

        # messages
        self.message_entry = tk.Entry(bottom_label, bg="lavender", fg=TEXT_COLOUR, font=FONT)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_entry.focus_set()
        self.message_entry.bind("<Return>", self.on_enter_pressed)

        send_button = tk.Button(bottom_label, text="Send", font=FONT_BOLD, width=25, bg=BG_GRAY,
                             command=lambda: self.on_enter_pressed(None))
        print("send button")
        send_button.pack(side=tk.RIGHT)

    def kill(self):
        self.window.destroy()

    def parse_message(self, msg):
        """
        When a rule is triggered in Experta, it adds two tags to indicate to the RE how to process the resulting user response.
        expert.type --> indicates the overall goal of the current message path (booking or delay) and indicates when complete.
        expert.request --> indicates the specific piece of information the user has been asked to provide.
        self.reinput --> indicates unclear information has been given. skips the running of the ke to ask for the information again.
        """

        if expert.type == "completed":  # Once a request is fulfilled, reset engine to allow another request cycle
            expert.reset()

        if expert.type == "booking":    # Process inputs that are tied to the booking pathway
            if expert.request == "get_destination":
                destination = ip.process_single_station(msg)
                print(destination)
                if destination and destination != 'unclear':
                    expert.declare(Ticket(destination=destination))
                    expert.request = ""
                else:
                    self.insert_messages("Sorry, I didn't get that. Please re-enter your destination station.", "Chatbot")
                    self.reinput = True
            elif expert.request == "get_departure":
                departure = ip.process_single_station(msg)
                print(departure)
                if departure and departure != 'unclear':
                    expert.declare(Ticket(departure=departure))
                    expert.request = ""
                else:
                    self.insert_messages("Sorry, I didn't get that. Please re-enter your departure station.", "Chatbot")
                    self.reinput = True
            elif expert.request == "get_date":
                date = ip.process_date(msg)
                print(date)
                if date and date != 'unclear':
                    expert.declare(Ticket(date=date))
                    expert.request = ""
                else:
                    self.insert_messages("Sorry, I didn't get that. Please re-enter your date of travel.", "Chatbot")
                    self.reinput = True
                expert.declare(Ticket(date=date))
                expert.request = ""
            elif expert.request == "get_time":
                train_time = ip.process_hour(msg)
                print(train_time)
                if train_time and train_time != 'unclear':
                    expert.declare(Ticket(time=train_time))
                    expert.request = ""
                else:
                    self.insert_messages("Sorry, I didn't get that. Please re-enter the time of your travel.", "Chatbot")
                    self.reinput = True
            elif expert.request == "get_passengers":
                adults, children = ip.process_passengers(msg)
                print(adults, children)
                passenger_check = 0
                if adults and adults != 0:
                    expert.declare(Ticket(adults=adults))
                    expert.request = ""
                    passenger_check += 1
                if children and children != 0:
                    expert.declare(Ticket(children=children))
                    expert.request = ""
                    passenger_check += 1
                if passenger_check < 1:
                    self.insert_messages("Sorry, I didn't get that. Please re-enter the number of adult and child passengers.", "Chatbot")
                    self.reinput = True
            elif expert.request == "get_railcard":
                railcard = ip.process_railcard(msg)
                print(railcard)
                if railcard and railcard != 'unclear':
                    expert.declare(Ticket(railcard=railcard))
                    expert.request = ""
                else:
                    self.insert_messages("Sorry, I didn't get that. If you have a railcard, please enter its type. Otherwise, reply 'No'.",
                                         "Chatbot")
                    self.reinput = True

        elif expert.type == 'delay':    # Process inputs that are tied to the delay pathway
            if expert.request == "get_destination":
                destination = ip.process_single_station(msg)
                print(destination)
                expert.declare(Ticket(destination=destination))
                expert.request = ""
            elif expert.request == 'get_current':
                current = ip.process_single_station(msg)
                print(current)
                expert.declare(Ticket(current=current))
                expert.request = ""
            elif expert.request == 'get_lateness':
                minutes_late = ip.process_lateness(msg)
                print(minutes_late)
                expert.declare(Ticket(minutes_late=minutes_late))
                expert.request = ""

        else:
            # If this is the first input, identify user's overall intention (booking, delay etc)
            intention_result = intentions.get_similar_intention(msg)
            match intention_result:
                case 'greeting':
                    self.insert_messages("Hello! I can help you book a ticket or monitor a delay.", "Chatbot")
                case 'goodbye':
                    self.insert_messages("Goodbye! Thank you for using this service.", "Chatbot")
                    tm.sleep(2)
                    self.kill()
                case 'thanks':
                    self.insert_messages("I'm glad I was useful. Let me know if you need anything else.", "Chatbot")
                case 'booking':
                    expert.reset()
                    expert.type = 'booking'     # Set the pathway type

                    # Process the initial message to extract as much information as possible
                    departure, destination, time, date, adults, children, railcard = ip.process_booking_input(msg)
                    results = f"Initial Results: {departure}, {destination}, {date}, {time}, {adults}, {children}, {railcard}\n"
                    print(results)
                    # app.insert_messages(results, "Chatbot")

                    # Keep track of whether all information is gathered from initial input
                    completion_counter = 0
                    passenger_check = 0

                    # Declare results if they returned a relevant value
                    if destination and destination != 'unclear':
                        expert.declare(Ticket(destination=destination))
                        completion_counter += 1
                    if departure and departure != 'unclear':
                        expert.declare(Ticket(departure=departure))
                        completion_counter += 1
                    if date and date != 'unclear':
                        expert.declare(Ticket(date=date))
                        completion_counter += 1
                    if time and time != 'unclear':
                        expert.declare(Ticket(time=time))
                        completion_counter += 1
                    if adults and adults != 0:
                        expert.declare(Ticket(adults=adults))
                        passenger_check += 1
                    if children and children != 0:
                        expert.declare(Ticket(children=children))
                        passenger_check += 1
                    if railcard and railcard != 0:
                        expert.declare(Ticket(railcard=railcard))
                        completion_counter += 1

                    # Mark as complete if all information given in one input
                    # if (completion_counter == 5) and (passenger_check >= 1):
                    #     expert.type = "complete"

                    expert.declare(UserIntent(action='buy_ticket'))

                case 'delay':
                    expert.reset()
                    expert.type = 'delay'

                    destination, current, minutes_late = ip.process_delay_input(msg)

                    if destination and destination != 'unclear':
                        expert.declare(Ticket(destination=destination))
                    if current and current != 'unclear':
                        expert.declare(Ticket(current=current))
                    if minutes_late and minutes_late != 'unclear':
                        expert.declare(Ticket(minutes_late=minutes_late))
                    expert.declare(UserIntent(action='check_delay'))

                case 'unclear':
                    self.insert_messages(
                        "Please try rephrasing your request. I can help you book a ticket or monitor a delay.",
                        "Chatbot")

    def on_enter_pressed(self, event):
        msg = self.message_entry.get()
        self.insert_messages(msg, "You")
        self.parse_message(msg)

        """
            self.reinput handles cases where a user inputs poor information.
            If True, the knowledge engine is not run, allowing the information to be re-entered.
            Once the KE is skipped, the self.reinput is set to false to end the cycle.
        """

        if not self.reinput:
            expert.declare(Fact("get_input", user_input=msg))
            expert.run()
        else:
            self.reinput = False

    def initial_message(self):
        message = "Welcome to the train service chatbot!\nWhat can I help you with today? \n"
        self.text_widget.configure(cursor="arrow", state=tk.NORMAL)
        self.text_widget.insert(tk.END, message)
        self.text_widget.configure(state=tk.DISABLED)
        self.text_widget.see(tk.END)

    def insert_messages(self, msg, sender):
        if not msg:
            return

        self.message_entry.delete(0, tk.END)
        msg1 = f"{sender}: {msg} \n"
        self.text_widget.configure(cursor="arrow", state=tk.NORMAL)
        self.text_widget.insert(tk.END, msg1)

        # Check if the message contains a URL
        str_msg = str(msg)
        urls = re.findall(r'(https?://\S+)', str_msg)
        for url in urls:
            self.text_widget.insert(tk.END, url, ('link', url))
            self.text_widget.tag_config('link', foreground='blue', underline=True)
            self.text_widget.tag_bind('link', '<Button-1>', lambda event, url: webbrowser.open_new(url))

        self.text_widget.see(tk.END)
        self.text_widget.configure(state=tk.DISABLED)


class UserIntent(Fact):
    pass


class Ticket(Fact):
    pass


class Delay(Fact):
    pass


class ProblemReport(Fact):
    pass


class CustomerExpert(KnowledgeEngine):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.type = ""
        self.request = ""
        self.knowledge = {}

    def reset_bot(self):
        self.reset()
        self.knowledge.clear()
        self.type = ""
        self.request = ""

    ###### BOOKING RULES

    @Rule(UserIntent(action='buy_ticket') & NOT(Ticket(destination=W())), salience=7)
    def ask_book_destination(self):
        self.request = "get_destination"
        app.insert_messages("Please enter the destination station:", "Chatbot")
        self.halt()

    @Rule(UserIntent(action='buy_ticket') & NOT(Ticket(departure=W())), salience=6)
    def ask_departure(self):
        self.request = "get_departure"
        app.insert_messages("Please enter the departure station:", "Chatbot")
        self.halt()

    @Rule(UserIntent(action='buy_ticket') & Ticket(departure=MATCH.de) & NOT(Ticket(date=W())), salience=5)
    def ask_date(self):
        self.request = "get_date"
        app.insert_messages("Please enter the date of travel:", "Chatbot")
        self.halt()

    @Rule(UserIntent(action='buy_ticket') & Ticket(date=MATCH.dt) & NOT(Ticket(time=W())), salience=4)
    def ask_time(self):
        self.request = "get_time"
        app.insert_messages("Please enter the departure time:", "Chatbot")
        self.halt()

    @Rule(UserIntent(action='buy_ticket') & Ticket(time=MATCH.t) & (NOT(Ticket(adults=W()) | Ticket(children=W()))), salience=3)
    def ask_passenger_info(self):
        self.request = "get_passengers"
        app.insert_messages("Please enter the number of passengers:", "Chatbot")
        self.halt()

    @Rule(UserIntent(action='buy_ticket') & Ticket(time=MATCH.t) & NOT(Ticket(railcard=W())),
          salience=2)
    def ask_railcard_info(self):
        self.request = "get_railcard"
        app.insert_messages("Do you have a railcard?:", "Chatbot")
        self.halt()

    @Rule(UserIntent(action='buy_ticket') & Ticket(destination=MATCH.d) & Ticket(departure=MATCH.de) & Ticket(
        date=MATCH.dt) & Ticket(time=MATCH.t) & Ticket(adults=MATCH.a) & Ticket(children=MATCH.c) & Ticket(railcard=MATCH.r), salience=1)
    def print_book_report(self, d, de, dt, t, a, c, r):
        self.request = ""
        self.type = "completed"
        report = f"Ticket information:\nDestination: {d}\nDeparture: {de}\nDate: {dt}\nTime: {t}\nPassengers: {a} Adults, {c} Children\nRailcard: {r}"
        app.insert_messages(report, "Chatbot")
        tm.sleep(1)

        ticket_links = Webscraping.main(d, de, dt, t, [a, c], r)
        if ticket_links:
            for link in ticket_links:
                app.insert_messages(f"Ticket Link: {link}", "Chatbot")
        else:
            app.insert_messages("There were no available tickets for your request.", "Chatbot")

        app.insert_messages("Thank you for using the chatbot. If you have another request, let me know!", "Chatbot")
        self.halt()

    # DELAY RULES

    @Rule(AS.delay_dest << (UserIntent(action='check_delay')) & NOT(Ticket(destination=W())),
          salience=4)
    def ask_delay_destination(self):
        self.request = "get_destination"
        app.insert_messages("Please enter the destination station:", "Chatbot")
        self.halt()

    @Rule(AS.delay_current << (UserIntent(action='check_delay')) & NOT(Ticket(current=W())),
          salience=3)
    def ask_current(self):
        self.request = "get_current"
        app.insert_messages("Please enter the current station:", "Chatbot")
        self.halt()

    @Rule(AS.delay_current << (UserIntent(action='check_delay')) & NOT(Ticket(minutes_late=W())),
          salience=2)
    def ask_lateness(self):
        self.request = "get_lateness"
        app.insert_messages("Please enter how late you are: ", "Chatbot")
        self.halt()

    @Rule(UserIntent(action='check_delay') & Ticket(destination=MATCH.d) & Ticket(current=MATCH.c) & Ticket(
        minutes_late=MATCH.ml),
          salience=1)
    def print_delay_report(self, d, c, ml):
        self.request = ""
        self.type = "completed"
        report = f"Destination: {d}\nCurrent Station: {c}\nMinutes Late: {ml}"
        app.insert_messages(report, "Chatbot")

        delay_report = predict_delay.predict_lateness(c, d, ml)
        app.insert_messages(delay_report, "Chatbot")

        tm.sleep(1)
        app.insert_messages("Thank you for using the chatbot. If you have another request, let me know!", "Chatbot")
        self.halt()


# RUN THE CHATBOT
app = ChatBot()
expert = CustomerExpert(app)
app.run()
