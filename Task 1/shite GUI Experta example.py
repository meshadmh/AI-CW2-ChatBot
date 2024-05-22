# -*- coding: utf-8 -*-
"""
Created on Tue May 21 15:30:50 2024

@author: dan
"""

import threading
import queue
from tkinter import *
from experta import *



class Symptom(Fact):
    """Symptoms exhibited by the patient."""
    pass

class Worried(Fact):
    """Binary is the patient worried."""
    pass

class Illness(Fact):
    """Diagnosed illness."""
    pass

class MyExpertSystem(KnowledgeEngine):
    @Rule(AS.Symptom << Symptom(feel=L('fever') & L('cough')))
    def diagnose_flu(self, Symptom):
        self.declare(Illness("flu"))
        self.output_queue.put(f"YOU GOT THE FLU!? because {Symptom['feel']}")

    @Rule(Symptom(feel=L('fever')), Symptom(feel='sore_throat'))
    def diagnose_flu_or_strep_throat(self):
        self.declare(Illness("flu or strep throat"))
        self.output_queue.put("FLU OR STREP??????????!!!")

    @Rule(Symptom(feel='rash'))
    def diagnose_measles(self):
        self.declare(Illness("measles"))
        self.output_queue.put("OH SHIT MEASLES")

    @Rule(OR(Symptom(feel='nausea'), Symptom(feel='vomiting'), Worried(is_worried=1)))
    def diagnose_gastroenteritis(self):
        self.declare(Illness("gastroenteritis"))
        self.output_queue.put("GASTRO")

def start_expert_system(expert_system_input_queue, output_queue):
    my_expert_system = MyExpertSystem()
    my_expert_system.output_queue = output_queue
    my_expert_system.reset()

    def process_expert_system_inputs():
        while True:
            if not expert_system_input_queue.empty():
                input_values = expert_system_input_queue.get()
                my_expert_system.reset()

                for input_value in input_values:
                    my_expert_system.declare(Symptom(feel=input_value))
                my_expert_system.run()

    #start processing expert system inputs
    threading.Thread(target=process_expert_system_inputs, daemon=True).start()

# Function to retrieve input from the user and send it to the expert system
def retrieve_input():
    inputValue = input_box.get("1.0", "end-1c")
    if inputValue.strip():
        #append the user input to the main text box
        textBox.configure(state=NORMAL)
        textBox.insert(END, "User: " + inputValue + "\n")
        textBox.see(END)  # Ensure the latest input is visible
        textBox.configure(state=DISABLED)
        
        #add the user input to the knowledge base
        knowledge_base.append(inputValue)
        #RIGHT NOW THIS SENDS THE INPUT QUEUE TO EXPERTA AFTER 2 INPUTS. THIS NEEDS TO BE SOMETHING MORE CLEVER
        if len(knowledge_base) >= 2:  
            expert_system_input_queue.put(knowledge_base.copy())
            knowledge_base.clear()

        #clear the input area
        input_box.delete("1.0", END)

def update_output():
    while True:
        if not output_queue.empty():
            output = output_queue.get()
            textBox.configure(state=NORMAL)
            textBox.insert(END, "System: " + output + "\n")
            textBox.see(END)  # Ensure the latest output is visible
            textBox.configure(state=DISABLED)

#store inputs
knowledge_base = []

root = Tk()
root.title("Shite GUI Experta example")

#main text box to display conversation
textBox = Text(root, height=15, width=50, state=DISABLED)
textBox.pack()

#input box for user to enter new text
input_box = Text(root, height=2, width=50)
input_box.pack()

buttonCommit = Button(root, height=1, width=10, text="Commit", command=retrieve_input)
buttonCommit.pack()

#queue for passing inputs from the GUI to the expert system
expert_system_input_queue = queue.Queue()
output_queue = queue.Queue()

#start expert system thread
expert_system_thread = threading.Thread(target=start_expert_system, args=(expert_system_input_queue, output_queue))
expert_system_thread.start()

#start output update thread
output_update_thread = threading.Thread(target=update_output, daemon=True)
output_update_thread.start()

root.mainloop()