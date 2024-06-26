# -*- coding: utf-8 -*-
"""
Created on Wed May  1 10:25:35 2024

@author: dan
"""
import chromadb
import loading_json
from experta.watchers import RULES, AGENDA
from datetime import datetime, timedelta
from experta import *
import numpy as np
import pandas as pd
from tkinter import *
import process_schedule_all

BG_GRAY = "gainsboro"
BG_COLOUR = "lavender"
TEXT_COLOUR = "black"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

train_schedules = loading_json.import_json()
relevant_stations = []
for train in train_schedules[0]['schedule_locations']:

    relevant_stations.append(train['tiploc_code'])
    
#print(process_schedule_all.get_all_schedule_advice("LIVST",700, train_schedules))


#%%

df = pd.read_csv('conversation_records.csv')
df = pd.DataFrame(df)

chroma_client = chromadb.PersistentClient(path="/chroma_docs")

collection = chroma_client.get_or_create_collection(name="my_collection")

documents = df["message"].tolist()
#%%
collection.add(
    documents=documents,
    ids=[f"{i}" for i in range(len(documents))]
)

def query_chroma(query_text):
    results = collection.query(
        query_texts=[query_text], # Chroma will embed this for you
        n_results=3 # how many results to return
    )
    closest_match = int(results["ids"][0][0])

    station = df['station'][closest_match]
    full_or_part = df['full_or_part'][closest_match]

    professions = ["train staff","passenger","signaller"]

    for prof in professions:
        if df[prof][closest_match]:
            customer = prof
            
    print(station, full_or_part, customer)
    return station, full_or_part, customer


#%%

class ChatBot:
    def __init__(self):
        self.window = Tk()
        self._setup_main_window()
        self.initial_message()

    def run(self):
        self.window.mainloop()

    def _setup_main_window(self):
        self.window.title("Chatbot")
        self.window.resizable(width=False, height=False)
        self.window.geometry("500x600")

    #head label

        head_label = Label(self.window, bg=BG_COLOUR,fg=TEXT_COLOUR,
                       text = "Welcome!", font=FONT, pady=10)
        head_label.pack(fill=X)
#divider
        line = Label(self.window, width=500, bg=BG_GRAY)
        line.pack(fill=X)
#text widget
        self.text_widget = Text(self.window,width=20, height=2, bg=BG_COLOUR, fg=TEXT_COLOUR,
                                font=FONT,padx=5,pady=5)
        self.text_widget.pack(fill=BOTH, expand=True)
        self.text_widget.configure(cursor="arrow", state=DISABLED)
#scrollbar
        scrollbar = Scrollbar(self.text_widget)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text_widget.see(CURRENT)
        scrollbar.configure(command=self.text_widget.yview)
        print("scrollbar")

#Bottom label

        bottom_label = Label(self.window,bg=BG_COLOUR, height=80)
        bottom_label.pack(fill=X)
        print("bottom label")

#messaage frame
        message_frame = Frame(bottom_label, bg=BG_COLOUR, pady=5)
        message_frame.pack(fill=X)
        print("message frame")
#message label
        message_label = Label(message_frame, text="Type your message here: ", font=FONT, fg="white")
        message_label.pack(side=LEFT)
        print("message label")
#messages
        self.message_entry = Entry(bottom_label, bg="lavender", fg=TEXT_COLOUR, font=FONT)
        self.message_entry.pack(side=LEFT, fill=X, expand=True)
        self.message_entry.focus_set()
        self.message_entry.bind("<Return>", self.on_enter_pressed)

        send_button = Button(bottom_label, text="Send", font=FONT_BOLD, width=25, bg=BG_GRAY,
                             command=lambda: self.on_enter_pressed(None))
        print("send button")
        send_button.pack(side=RIGHT)
    def kill(self):
        app.destroy() 
        #TODO destroy doesnt actually work
    def parse_message(self,msg):
        #Take in chroma input
        if expert.knowledge.get('question') == 'ask_if_blockage':
            station, full_or_part, customer = query_chroma(msg)
            expert.reset()
            expert.dictionary
            expert.declare(Fact(location = station))
            expert.declare(Fact(full_or_part = full_or_part))
            expert.declare(Fact(customer = customer))
            expert.declare(Service(service = "check_inputs"))
            #expert.knowledge['question'] = 'check_inputs'
        #Check the chromaDB has worked
        if expert.knowledge.get('question') == 'check_inputs':
            #Should be 'positive intention'
            if msg=="yes":

                #expert.reset()
                expert.declare(Fact(location_provided=True))
                expert.declare(Fact(full_or_part_provided=True))
                expert.declare(Fact(customer_provided=True))
                #expert.modify(Service(service='check_inputs'), service='blocked_line')
                expert.declare(Service(service = "line_blockage"))
            else:
                #Some how get back on track
                expert.reset()
                expert.declare(Service(service = "line_blockage"))
        #IF the bot has recieved input, ask to recieve more line blockage problems 
        if expert.knowledge.get('question') =="check_for_another_input":
            #Should be 'positive intention' THIS IS ALL HARD CODED ATM SHOULD BE NLP OR WHATEVER
            if msg=="yes":
                expert.knowledge['question'] ="asking_for_problem"
            else:
                self.insert_messages("Bye!", "Chatbot")
                expert.halt()
                self.kill()
        if expert.knowledge.get('question') == 'get_location':
            if msg=="blocked line":
                expert.declare(Service(service = "line_blockage"))
        if expert.knowledge.get('question') == 'ask_time':
            if msg=="700":
                expert.dictionary['time']=700
                expert.declare(Fact(time = 700))
                expert.declare(Fact(isQuestion = False))
                expert.declare(Fact(time_provided=True))
        if expert.knowledge.get('question') == 'ask_location':
            if msg == 'colchester':
                expert.dictionary['location']="CLCHSTR"
                expert.declare(Fact(location = 'CLCHSTR'))
                expert.declare(Fact(isQuestion = False))
                expert.declare(Fact(location_provided=True))
        if expert.knowledge.get('question') == 'ask_full_or_part':        
            if msg == 'partial':
                expert.dictionary['full_or_part']="partial"
                expert.declare(Fact(full_or_part = 'partial'))
                expert.declare(Fact(isQuestion = False))
                expert.declare(Fact(full_or_part_provided=True))
        if expert.knowledge.get('question') == 'ask_customer':
            if msg == 'train staff':
                expert.dictionary['customer']="train staff"
                expert.declare(Fact(customer = 'train staff'))
                expert.declare(Fact(isQuestion = False))
                expert.declare(Fact(customer_provided=True))

    def on_enter_pressed(self, event):
        msg = self.message_entry.get()
        self.insert_messages(msg, "You ")
        self.parse_message(msg)
        expert.declare(Fact("get_input", user_input=msg))
        expert.run()

    def initial_message(self):
        message = "Welcome to the train service chatbot!\nWhat can I help you with today? \n" 
        self.text_widget.configure(cursor="arrow", state=NORMAL)
        self.text_widget.insert(END, message)
        self.text_widget.configure(state=DISABLED)
        self.text_widget.see(END)

    def insert_messages(self, msg, sender):
        if not msg:
            return

        self.message_entry.delete(0,END)
        msg1 = f"{sender}: {msg} \n"
        self.text_widget.configure(cursor="arrow", state=NORMAL)
        self.text_widget.insert(END, msg1)
        self.text_widget.see(CURRENT)
        self.text_widget.configure(state=DISABLED)


#%%


def find_intention(user_input, dictionary, knowledge):
    "Get value based on conditions"
    
    if user_input == "blocked":
        knowledge['question'] = 'ask_location'
        return 'line_block'
    
def get_value(df, full_or_part, location, target_column):
    if target_column == "csd":
        output_target_column = "customer service staff deployment advice"
        
    elif target_column == "alt_transport":
        output_target_column = "alternative transport advice"
    elif target_column == "signallers":
        output_target_column = "signaller advice"
    else:
        output_target_column = target_column
    out_str = ""
    out_str += "\n--------------------------------------------------------------------\n"
    out_str += "Here is the " + output_target_column + " for a " + full_or_part + " blockage at " + location +"\n"
    full_or_part = df['full_or_part'] == full_or_part
    location = df['station'] == location
    filtered_row = df[full_or_part & location]
    out_str += filtered_row[target_column].values[0]
    out_str += "\n--------------------------------------------------------------------\n"
    return out_str



#get the advice
advice = pd.read_csv('contingency_advice.csv')
advice = advice.replace(r'\\n', '\n', regex=True)
moose = get_value(advice, "partial","CLCHSTR", "alt_transport")

def format_output(target_variables, location, full_or_part, time):
    output = ""
    output += "\n--------------------------------------------------------------------\n"
    for target_var in target_variables:
        output += get_value(advice, full_or_part,location, target_var)
    #print relvant advice then check to see if we can do more:
    output += "\n--------------------------------------------------------------------\n"
    if location in relevant_stations and (full_or_part=="full"):
        output += "Also, here is the amended timetable, given adjustments for special services and delays, making sure all services run in the correct order\n"
        output += process_schedule_all.get_all_schedule_advice(location,time, train_schedules)

    return output

#%%
class line_blockage(Fact):
    "Contains all info about the event"
    pass

class location(Fact):
    "contains 2 station names that has a line blockage"
    pass
class isQuestion(Fact):
    "contains 2 station names that has a line blockage"
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
class Service(Fact):
    "Who is the bot talking to?"
    pass
class customer(Fact):
    "Who is the bot talking to?"
    pass
class location_provided(Fact):
    "Who is the bot talking to?"
    pass
class contingency_expert(KnowledgeEngine):


    # @DefFacts()
    # def _initial_action(self):
    #     if 'reset' in self.dictionary:
    #         if self.dictionary.get('reset') == 'true':
    #             self.knowledge = {}
    #             self.dictionary['service'] = 'chat'
    #         service = self.dictionary.get('service')
            
    #     yield Fact(service = self.knowledge.get('service'))

    #     # Set knowledge
    #     if not 'question' in self.knowledge:
    #         self.knowledge['question'] = str()

    #     if 'full_or_part' in self.knowledge:
    #         yield Fact(full_or_part = self.knowledge.get('full_or_part'))
    #     if 'time' in self.knowledge:
    #         yield Fact(time = self.knowledge.get('time'))
    #     if 'location' in self.knowledge:
    #         yield Fact(location = self.knowledge.get('location'))
    #     if 'customer' in self.knowledge:
    #         yield Fact(customer = self.knowledge.get('customer'))
    def reset_bot(self):
        self.reset()
        self.knowledge.clear()
        self.dictionary.clear()
        self.knowledge['question'] = 'given_input'
        self.declare(Service(service = "chat"))
        self.declare(Fact(location_provided=False))
    
    @Rule(
        AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input),
        NOT(Service(service="chat")),
        NOT(Service(service="check_inputs")),
        NOT(Service(service="line_blockage"))
        ) 
    def greeting(self, user_input_fact, user_input):
        self.retract(user_input_fact)
        self.dictionary.clear()
        self.knowledge.clear()
        self.knowledge['question'] ="greeting"
        
        if user_input.lower() == "hi":
            output = "hi! Is there currently a problem?"
            self.declare(Service(service="chat"))
            self.knowledge['question'] ="asking_for_problem"
        else:
            output ="Is there currently a line blockage?"
        app.insert_messages(output, "ChatBot")
        
    @Rule(
        AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input),
        #AS.serv << Fact("chat", service=MATCH.service),
        Service(service = 'chat'),
        NOT(Fact(location_provided=True))
        ) 
    def ask_if_blockage(self, user_input_fact, user_input):
        self.retract(user_input_fact)
        if self.knowledge['question'] =="asking_for_problem":
            if self.knowledge["question"] == 'ask_if_blockage':
                output = "Sorry I don't get what you mean"
            else:
                self.knowledge['question'] = 'ask_if_blockage'
                output ="Please tell me as much about the problem as possible."
        elif self.knowledge['question'] =="given_input":
            print(expert.facts)
            output = "Is there another line blockage I can help you with?"
            self.knowledge['question'] ="check_for_another_input"
        else:
            output = "Sorry I don't get what you mean"
            self.knowledge['question'] = 'ask_if_blockage'
            
        app.insert_messages(output, "ChatBot")
    #Check that chromaDB has worked (probably hasn't)
    @Rule(AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input),
        #AS.serv << Fact("check_inputs", service=MATCH.service),
        Service(service = 'check_inputs'),
        Fact(full_or_part = MATCH.full_or_part),
        Fact(location = MATCH.location),
        Fact(customer = MATCH.customer),
        NOT(Fact(location_provided=True))
        )
    def check_inputs(self, user_input_fact, user_input,customer,location,full_or_part):
        self.retract(user_input_fact)
        #self.retract(serv)
        self.knowledge['question'] = 'check_inputs'
        output = f'There is a {full_or_part} blockage, which is at {location}, and you are a {customer}.\n Is this correct?'
        app.insert_messages(output, "ChatBot")
    #IF it has worked, ask for time. If it hasn't, get back on track asking more precise questions
    # @Rule(AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input),
    #     #AS.serv << Fact("check_inputs", service=MATCH.service),
    #     Service(service = 'go_slower'),
    #     NOT(Fact(location_provided=True))
    #     )
    # def apologise_and_go_slower(self, user_input_fact, user_input,customer,location,full_or_part):
    #     self.retract(user_input_fact)
    #     #self.retract(serv)
    #     self.knowledge['question'] = 'check_inputs'
    #     output = f'There is a {full_or_part} blockage, which is at {location}, and you are a {customer}.\n Is this correct?'
    #     app.insert_messages(output, "ChatBot")
        
    #Ask location
    @Rule(
        AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input),
        Service(service= "line_blockage"),
        NOT(Fact(location_provided=True)),salience=99
        ) 
    def get_location(self, user_input_fact, user_input):
        self.retract(user_input_fact)
        if 'location' in self.dictionary:
            location = self.dictionary.get('location')
            self.declare(Fact(location = location))
            self.knowledge['location'] = location
            self.declare(Fact(location_provided=True))
        else:
            #if it's already asked the question and can't comprehend it
            if self.knowledge['question'] == 'ask_location':
                output = "Sorry I don't understand" 
            elif self.knowledge['question'] == 'check_inputs':
                self.knowledge['question'] = 'ask_location'
                output = "Aplogies, let's go a bit slower. Firstly, what is your location?"
            else:
                self.knowledge['question'] = 'ask_location'
                output = "Pls give location"
            self.knowledge['question'] = 'ask_location'
            app.insert_messages(output, "ChatBot")
            #self.declare(Fact(isQuestion = True))
            
   #ask time      
    @Rule(
        AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input),
        Service(service= "line_blockage"),
        NOT(Fact(time_provided=True)),
        NOT(Fact(isQuestion)),salience=98
        ) 
    def get_time(self, user_input_fact, user_input):
        self.retract(user_input_fact)
        if 'time' in self.dictionary:
            time = self.dictionary.get('time')
            self.declare(Fact(time = time))
            self.knowledge['time'] = time
            self.declare(Fact(time_provided=True))
        else:
            #if it's already asked the question and can't comprehend it
            if self.knowledge['question'] == 'ask_time':
                output = "Sorry I don't understand" 
            else:
                self.knowledge['question'] = 'ask_time'
                output= "What's the time?"
            #self.declare(Fact(isQuestion = True))
            self.knowledge['question'] = 'ask_time'
            app.insert_messages(output, "ChatBot: ")
       #ask full or part      hi
    @Rule(
        AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input),
        Service(service= "line_blockage"),
        NOT(Fact(full_or_part_provided=True)),
        NOT(Fact(isQuestion)),salience=97
        ) 
    def get_full_or_part(self, user_input_fact, user_input):
        self.retract(user_input_fact)
        if 'full_or_part' in self.dictionary:
            full_or_part = self.dictionary.get('full_or_part')
            self.declare(Fact(full_or_part = full_or_part))
            self.knowledge['full_or_part'] = full_or_part
            self.declare(Fact(time_provided=True))
        else:
            #if it's already asked the question and can't comprehend it
            if self.knowledge['question'] == 'ask_full_or_part':
                output = "Sorry I don't understand" 
            else:
                self.knowledge['question'] = 'ask_full_or_part'
                output= "Is it a full or partial blockage?"
            #self.declare(Fact(isQuestion = True))
            self.knowledge['question'] = 'ask_full_or_part'
            app.insert_messages(output, "ChatBot")
    #FULL OR PARTIAL?
    @Rule(
        AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input),
        Service(service= "line_blockage"),
        NOT(Fact(customer_provided=True)),
        NOT(Fact(isQuestion)),salience=96
        ) 
    def get_customer(self, user_input_fact, user_input):
        self.retract(user_input_fact)
        if 'customer' in self.dictionary:
            customer = self.dictionary.get('customer')
            self.declare(Fact(customer = customer))
            self.knowledge['customer'] = customer
            self.declare(Fact(customer_provided=True))
        else:
            #if it's already asked the question and can't comprehend it
            if self.knowledge['question'] == 'ask_customer':
                output = "Sorry I don't understand" 
            else:
                self.knowledge['question'] = 'ask_customer'
                output= "What is your profession?"
            #self.declare(Fact(isQuestion = True))

            self.knowledge['question'] = 'ask_customer'
            app.insert_messages(output, "ChatBot")
    #--------------------------------------------------------------------------  
    #Once all the info is there, calculate the schedule amendments
    @Rule(AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input),
        Service(service = 'line_blockage'),
        Fact(full_or_part = 'partial'),
        Fact(location = MATCH.location),
        Fact(time = MATCH.time),
        Fact(customer = "train staff")
        )
    def advise_train_staff_part(self,  location,time, user_input_fact, user_input):
        self.retract(user_input_fact)
        
        output = format_output(["alt_transport","csd"], location, "partial", time)
        self.reset_bot()
        app.insert_messages(output, "ChatBot")
        
        
    #Once all the info is there, calculate the schedule amendments
    @Rule(AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input),
        Service(service = 'line_blockage'),
        Fact(full_or_part = 'partial'),
        Fact(location = MATCH.location),
        Fact(time = MATCH.time),
        Fact(customer = "signaller")
        )
    def advise_signaller_part(self, user_input_fact, location,time):
        self.retract(user_input_fact)
        self.reset_bot()
        output = format_output(["signallers"], location, "partial", time)
        app.insert_messages(output, "ChatBot")

        
    @Rule(AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input),
        Service(service = 'line_blockage'),
        Fact(full_or_part = 'partial'),
        Fact(location = MATCH.location),
        Fact(time = MATCH.time),
        Fact(customer = "passenger")
        )
    def advise_passenger_part(self,user_input_fact,  location,time):
        self.retract(user_input_fact)
        self.reset_bot()
        output = format_output(["alt_transport"], location, "partial", time)
        app.insert_messages(output, "ChatBot")

        
    @Rule(AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input),
        Service(service = 'line_blockage'),
        Fact(full_or_part = 'full'),
        Fact(location = MATCH.location),
        Fact(time = MATCH.time),
        Fact(customer = "passenger")
        )
    def advise_passenger_full(self,user_input_fact,  location,time):
        self.retract(user_input_fact)
        self.reset_bot()
        output = format_output(["alt_transport"], location, "full", time)
        app.insert_messages(output, "ChatBot")
        
    @Rule(AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input),
        Service(service = 'line_blockage'),
        Fact(full_or_part = 'full'),
        Fact(location = MATCH.location),
        Fact(time = MATCH.time),
        Fact(customer = "signaller")
        )
    def advise_signaller_full(self,user_input_fact,  location,time):
        self.retract(user_input_fact)
        self.reset_bot()
        output = format_output(["signallers"], location, "full", time)
        app.insert_messages(output, "ChatBot")
        
    @Rule(AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input),
        Service(service = 'line_blockage'),
        Fact(full_or_part = 'full'),
        Fact(location = MATCH.location),
        Fact(time = MATCH.time),
        Fact(customer = "train staff")
        )
    def advise_train_staff_full(self,user_input_fact,  location,time):
        self.retract(user_input_fact)
        self.reset_bot()
        output = format_output(["alt_transport","csd"], location, "full", time)
        app.insert_messages(output, "ChatBot")
        
#Init the expert
expert = contingency_expert()
expert.dictionary = {}
expert.knowledge = {}
expert.reset()

# Run the knowledge base 
expert.run()


app = ChatBot()
app.run()
