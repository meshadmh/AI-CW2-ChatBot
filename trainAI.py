# Import Packages
import spacy.cli

# Import Functions
import intention_spacy
import lemmatize
import train_ke as ke
import process_input as pi
import intentions_cdb


# nlp = spacy.load('en_core_web_lg')

# Create an instance of the rule engine
agent = ke.TrainChatBot()



chatbot_status = True

while chatbot_status:
    # Take and clean user input
    user_input = input("USER: ")
    processed_input = pi.process_input(user_input)

    # Identify intention of message
    intention_result = intentions_cdb.get_similar_intention(processed_input)

    
    match intention_result:
        case 'greeting':
            print("Hello, welcome to the TrainAI chatbot. I can help you book a ticket, monitor a delay, or give guidance on a train issue.")
        
        case 'goodbye':
            print('trainAI: Goodbye! Thank you for using this service.')
            chatbot_status = False
        
        case 'thanks':
            print('trainAI: I\'m glad I was useful. Let me know if you need anything else.')
        
        case 'booking':
            print('BOOKING FUNCTION')
            agent.reset()
            agent.declare(ke.UserIntent(action='buy_ticket', initial_input=user_input))
            # agent.declare(ke.UserIntent(action='buy_ticket'))
            # agent.declare(ke.UserIntent(initial_input=processed_input))
            agent.run()

        case 'delay':
            print('DELAY FUNCTION')
            agent.reset()
            agent.declare(ke.UserIntent(action='check_delay', initial_input=user_input))
            agent.run()

        case 'guidance':
            print('GUIDANCE FUNCTION')
            agent.reset()
            agent.declare(ke.UserIntent(action='report_problem'))
            agent.run()
        case 'unclear':
            print('trainAI: Please try rephrasing your request. I can help you book a ticket, monitor a delay, or give guidance on a train issue.')

