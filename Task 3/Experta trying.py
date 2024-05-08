# -*- coding: utf-8 -*-
"""
Created on Wed May  1 08:15:36 2024

@author: dan
"""

from random import choice
from experta import *


class Light(Fact):
    """Info about the traffic light."""
    pass


class RobotCrossStreet(KnowledgeEngine):
    @Rule(Light(color='green'))
    def green_light(self):
        print("Walk")

    @Rule(Light(color='red'))
    def red_light(self):
        print("Don't walk")

    @Rule(AS.light << Light(color=L('yellow') | L('blinking-yellow')))
    def cautious(self, light):
        print("Be cautious because light is", light["color"])
        
engine = RobotCrossStreet()
        
engine.reset()
engine.declare(Light(color='blinking-yellow'))
engine.run()


class Symptom(Fact):
    """Symptoms exhibited by the patient."""
    pass

# Define a Illness fact class to represent diagnosed illnesses
class Illness(Fact):
    """Diagnosed illness."""
    pass

# Define the DiagnosisExpert class inheriting from KnowledgeEngine
class DiagnosisExpert(KnowledgeEngine):
    # Rule to diagnose flu when patient has fever and cough
    @Rule(AS.Symptom << Symptom(feel =L('fever') & L('cough')))
    def diagnose_flu(self, Symptom):
        self.declare(Illness("flu"))
        print("YOU GOT THE FLU MUTHAFUCKA because", Symptom["feel"])
        

    # Rule to diagnose flu or strep throat when patient has fever and sore throat
    @Rule(Symptom(feel =L('fever')), Symptom(feel ='sore_throat'))
    def diagnose_flu_or_strep_throat(self):
        self.declare(Illness("flu or strep throat"))
        print("wank")

    # Rule to diagnose measles when patient has rash
    @Rule(Symptom(feel ='rash'))
    def diagnose_measles(self):
        self.declare(Illness("measles"))
        print("OH SHIT MEASLES")

    # Rule to diagnose gastroenteritis when patient has nausea or vomiting
    @Rule(OR(Symptom(feel ='nausea'), Symptom(feel ='vomiting')))
    def diagnose_gastroenteritis(self):
        self.declare(Illness("gastroenteritis"))
        print("GASTRO")

# Create an instance of the DiagnosisExpert knowledge base
diagnosis_expert = DiagnosisExpert()
diagnosis_expert.reset()
# Add symptoms as facts to the knowledge base
diagnosis_expert.declare(Symptom(feel='fever'))
diagnosis_expert.declare(Symptom(feel='sore_throat'))
diagnosis_expert.declare(Symptom(feel='nausea'))

# Run the knowledge base to diagnose the illness
diagnosis_expert.run()



#%%
class rock_pap_scis(KnowledgeEngine):
    
    @Rule(Fact(name1=MATCH.name23, against__scissors=1, against__paper=-1))
    def what_wins_to_scissors_and_losses_to_paper(self, name23):
        print(name23)
rps = rock_pap_scis()
rps.reset()
rps.declare(Fact(name1="scissors", against={"scissors": 0, "rock": -1, "paper": 1}))
rps.declare(Fact(name1="paper", against={"scissors": -1, "rock": 1, "paper": 0}))
rps.declare(Fact(name1="rock", against={"scissors": 1, "rock": 0, "paper": -1}))
rps.run()
