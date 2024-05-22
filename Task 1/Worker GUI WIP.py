from tkinter import *

BG_GRAY = "gainsboro"
BG_COLOUR = "lavender"
TEXT_COLOUR = "black"

FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

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

    def on_enter_pressed(self, event):
        msg = self.message_entry.get()
        self.insert_messages(msg, "You ")

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


if __name__ == "__main__":
    app = ChatBot()
    app.run()
