# -*- coding: utf-8 -*-
"""
Created on Wed May 22 13:21:51 2024

@author: dan
"""
import threading
import queue
import tkinter as tk
from tkinter import *
from experta import *

root = tk.Tk()

root.title("Experta GUI")

#main text box to display conversation
text_area = Text(root, height=15, width=50, state=DISABLED)
text_area.pack()

#input box for user to enter new text
input_area = Entry(root, width=50)
input_area.pack()

send = Button(root,  text="Commit", command=lambda: process_message())
send.pack()

class MyExpertSystem(KnowledgeEngine):

    @Rule(
        AS.user_input_fact << Fact("get_input", user_input=MATCH.user_input) 
        ) #I think this would have to include 'NOT(Fact(book_ticket)) etc when there's more than one fact
    def test_response(self, user_input_fact, user_input):
        self.retract(user_input_fact)
        if user_input.lower() == "hi":
            output = "hi!"
        else:
            output ="bye..."
        text_area.config(state=NORMAL)
        text_area.insert(END, f"user: {user_input}\n")
        text_area.insert(END, f"bot: {output}\n")
        #text_area.config(state=DISABLED)
        
engine = MyExpertSystem()
engine.reset()
engine.run()
    
def process_message():
    user_input = input_area.get()
    input_area.delete(0, END)
    print(user_input)
    engine.declare(Fact("get_input", user_input=user_input))
    engine.run()
    
root.mainloop()