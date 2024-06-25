import requests
from tkinter import *
import tkinter as tk
from tkinter import messagebox

window = Tk()
window.title("Typing Speed Test")
window.geometry("850x350")
window.config(pady=5, padx=5, background="black")
FONT_NAME = "Roboto Mono"

# To add customised icon to your app
icon = tk.PhotoImage(file="icon.png")
window.wm_iconphoto(False, icon)


class Text_Class:
    def __init__(self):
        self.txt_list = self.text_generator()
        self.pressed_let = None
        self.counter = 0
        self.corr_cpm = 0
        self.offset = 0
        self.coefficient = 1
        self.first_time = True

    def text_generator(self):
        response = requests.get(url="https://random-word-api.vercel.app/api?words=150")
        self.text_to_type = " ".join(response.json())
        return response.json()


text_machine = Text_Class()



def start_timer():
    if text_machine.first_time:
        text_machine.first_time = False
    # resetting writing field if starter triggered another time than first time
    else:
        window.after_cancel(text_machine.tmr)

        text_machine.txt_list = text_machine.text_generator()
        shown_text.config(state='normal')
        shown_text.delete('1.0', 'end')
        shown_text.insert('1.0', text_machine.text_to_type)
        shown_text.tag_add("center-text", "1.0", "end")
        shown_text.config(state='disabled')
        window.update_idletasks()

        entry_wgt.delete(0, tk.END)
        entry_wgt.focus_set()
        shown_text.tag_remove("redd", 1.0, 'end')
        shown_text.tag_remove("prpl", 1.0, 'end')
        text_machine.pressed_let = None
        text_machine.counter = 0
        text_machine.corr_cpm = 0
        text_machine.offset = 0
        text_machine.coefficient = 1

    entry_wgt.delete(0, tk.END)
    entry_wgt.focus_set()
    count_down(60)
    cpm_display.config(text=0)
    wpm_display.config(text=0)
    entry_wgt.bind("<KeyRelease>", click)


def click(event):
    shown_text.tag_remove("redd", f"1.{text_machine.offset}",
                          f"1.{text_machine.offset + len(text_machine.txt_list[text_machine.counter])}")
    shown_text.tag_remove("prpl", f"1.{text_machine.offset}",
                          f"1.{text_machine.offset + len(text_machine.txt_list[text_machine.counter])}")

    text_machine.pressed_let = event.char
    written_text_str = entry_wgt.get()

    if len(written_text_str) > len(text_machine.txt_list[text_machine.counter]):
        length = len(text_machine.txt_list[text_machine.counter])
    else:
        length = len(written_text_str)
    #here we compare each entry with shown word from line, letter after letter
    for i in range(0, length):
        if written_text_str[i] == text_machine.txt_list[text_machine.counter][i]:
            # this condition is just for app tweak so it doesn't show any red color when just spaces are typed
            if written_text_str != " ":
                shown_text.tag_remove("redd", f"1.{i + text_machine.offset}", f"1.{i + 1 + text_machine.offset}")
                shown_text.tag_add("prpl", f"1.{i + text_machine.offset}", f"1.{i + 1 + text_machine.offset}")

        else:
            if written_text_str != " ":
                shown_text.tag_remove("prpl", f"1.{i + text_machine.offset}", f"1.{i + 1 + text_machine.offset}")
                shown_text.tag_add("redd", f"1.{i + text_machine.offset}", f"1.{i + 1 + text_machine.offset}")
    # this condition is just for app tweak so when just spaces are accidentaly typed nothing happens and writer can type further
    if text_machine.pressed_let == " ":
        if written_text_str == " ":
            entry_wgt.delete(0, tk.END)

        else:
            print("space was pressed")
            written_text_str = written_text_str[:-1]

            # here code compares typed word with shown one
            if text_machine.txt_list[text_machine.counter] == written_text_str:
                #if typed word matches its correct CPM is counted and shown matching word will be signed with green color
                text_machine.corr_cpm = text_machine.corr_cpm + len(written_text_str)
                print(text_machine.corr_cpm)
                shown_text.tag_remove("redd", f"1.{text_machine.offset}",
                                      f"1.{text_machine.offset + len(text_machine.txt_list[text_machine.counter])}")
                shown_text.tag_add("good", f"1.{text_machine.offset}",
                                   f"1.{text_machine.offset + len(text_machine.txt_list[text_machine.counter])}")
            else:
                #incorrect word will be signed with red after typing SPACE
                shown_text.tag_remove("prpl", f"1.{text_machine.offset}",
                                      f"1.{text_machine.offset + len(text_machine.txt_list[text_machine.counter])}")
                shown_text.tag_add("bad", f"1.{text_machine.offset}",
                                   f"1.{text_machine.offset + len(text_machine.txt_list[text_machine.counter])}")

            text_machine.offset = text_machine.offset + len(text_machine.txt_list[text_machine.counter]) + 1
            text_machine.counter += 1
            print(text_machine.counter)
            print(text_machine.offset)
            entry_wgt.delete(0, tk.END)

            #part for checking on which line we are and when to scroll the text according of what is being typed
            lines = shown_text.count('1.0', 'end', 'displaylines')
            chars = len(shown_text.get('1.0', 'end'))
            average_char_per_line = chars / lines[0]

            if text_machine.offset > (average_char_per_line + 7) * text_machine.coefficient:
                shown_text.yview_scroll(1, 'units')
                text_machine.coefficient += 1


def count_down(count):
    timer_display.config(text=count)

    if count < 10:
        timer_display.config(text=count, fg="red")

    if count == 0:
        entry_wgt.unbind("<KeyRelease>")

        timer_display.config(text=count, fg="white")

        cpm_display.config(text=text_machine.corr_cpm)
        wpm_display.config(text=text_machine.corr_cpm / 5)

        return

    text_machine.tmr = window.after(1000, count_down, count - 1)


def helper():
    tk.messagebox.showinfo(title="Help",
                           message="Hello\n\nThis is one-minute typing test to find out\nhow many words do you type "
                                   "in one minute:\n\n- 'raw CPM'"
                                   "is the actual number of characters you type per minute, including all the mistakes."
                                   "\n- 'Corrected CPM' scores count only characters of correctly typed words."
                                   "\n- 'WPM' is just the corrected CPM divided by 5.\n- press Start to trigger the "
                                   "timer and start to type\n- only word finished with SPACE counts!"
                                   "\n\n Good Luck!")

def reset():
    shown_text.config(state='normal')
    shown_text.delete('1.0', 'end')
    shown_text.config(state='disabled')
    window.update_idletasks()

    entry_wgt.delete(0, tk.END)
    entry_wgt.focus_set()
    shown_text.tag_remove("redd", 1.0, 'end')
    shown_text.tag_remove("prpl", 1.0, 'end')
    text_machine.pressed_let = None
    text_machine.counter = 0
    text_machine.corr_cpm = 0
    text_machine.offset = 0
    text_machine.coefficient = 1
    cpm_display.config(text=0)
    wpm_display.config(text=0)
    entry_wgt.bind("<KeyRelease>", click)

    window.after_cancel(text_machine.tmr)
    timer_display.config(text=60)



################################################## GUI part ############################################################

start_button = tk.Button(text="Start", width=8, font=(FONT_NAME, 15, "bold"), command=start_timer, bg="black",
                         highlightthickness=0, borderwidth=0)
start_button.grid(row=0, column=0, sticky="W", padx=(15, 15))

empty_label = tk.Label(text="Typing Speed Test", width=15, font=("System", 25, "bold", "underline"), bg="black")
empty_label.grid(row=0, column=1, padx=(10, 0))

timer_sign = tk.Label(text="Time Left:", font=(FONT_NAME, 15, "normal"), bg="black")
timer_sign.grid(row=0, column=3, sticky="E", padx=(0, 30))

timer_display = tk.Label(text="60", font=(FONT_NAME, 15, "normal"), width=2, fg="white", bg="black")
timer_display.grid(row=0, column=3, sticky="E", )

######################################## TABLE FOR PRINTING THE TEXT TO BE TYPED #######################################

shown_text = tk.Text(width=100, height=10, font=(FONT_NAME, 12, "normal"), wrap="word")
shown_text.insert("1.0", text_machine.text_to_type)
shown_text.config(state="disabled")

shown_text.tag_configure("prpl", foreground="#7A316F")
shown_text.tag_configure("redd", foreground="red")
shown_text.tag_configure("good", font=(FONT_NAME, 10, "italic"), foreground="#7A316F")
shown_text.tag_configure("bad", font=(FONT_NAME, 10, "italic", "underline"), foreground="#CD6688")
shown_text.tag_configure("center_text", justify="center")
shown_text.tag_add("center_text", "1.0", "end")

shown_text.grid(row=1, columnspan=5, pady=(20, 10), padx=(15, 15))

######################################### WINDOW WHERE USER TYPES TEXT #################################################

entry_wgt = tk.Entry(width=40, font=(FONT_NAME, 10, "normal"), justify="center")
entry_wgt.focus_set()
entry_wgt.grid(row=2, columnspan=5, pady=(10, 15))

################################################################################################################

cpm_label = tk.Label(text="Corrected CPM:", font=(FONT_NAME, 10, "normal"), bg="black")
cpm_label.grid(row=3, column=1, sticky="E")

cpm_display = tk.Label(width=4, font=(FONT_NAME, 10, "bold"), bg="black", )
cpm_display.grid(row=3, column=2, sticky="W")

wpm_label = tk.Label(text="WPM:", font=(FONT_NAME, 10, "normal"), bg="black")
wpm_label.grid(row=3, column=3, sticky="E")

wpm_display = tk.Label(width=4, font=(FONT_NAME, 10, "bold"), bg="black", )
wpm_display.grid(row=3, column=4, sticky="W")

reset = tk.Button(text="Reset", font=(FONT_NAME, 15, "bold"), width=8, bg="black", highlightthickness=0, borderwidth=0,
                  command=reset)
reset.grid(row=3, column=0, sticky="W", padx=(15, 15))

help_button = tk.Button(text="Help", width=6, bg="black", font=(FONT_NAME, 10, "bold"), command=helper,
                        highlightthickness=0, borderwidth=0)
help_button.grid(row=4, column=4, pady=(10, 0))

window.mainloop()
