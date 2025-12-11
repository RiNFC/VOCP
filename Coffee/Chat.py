import tkinter as tk
import os
import subprocess
import sys
import time

colortext = "white"

log_file = open("bin/log.txt", "w")

chat_process = subprocess.Popen([sys.executable, "Core.py"], stdout=log_file, stderr=subprocess.STDOUT)

def on_input_change(*args):
    current_text = entry_var.get()
    
    with open("bin/chatboxcontent", "w") as file:
        file.write(current_text)



def afk_toggle():
    with open("bin/afk", "r+") as file:
        if file.read() == "False": 
            file.seek(0)
            file.write("True")
        else: 
            file.seek(0)
            file.write("False")

root = tk.Tk()
root.title("Coffee's Chatbox")
root.geometry("200x175")
root.config(bg="black")
root.iconbitmap("bin/icon.ico")
root.attributes('-topmost', True) 


label = tk.Label(root, text="", fg=colortext)
label.pack(pady=10)
label.config(bg="black")

def update_label():
    if os.path.exists("bin/chatboxcurrent"):
        with open("bin/chatboxcurrent", "r", encoding="utf-8") as f:
            current_text = f.read()
        label.config(text=current_text)
    root.after(500, update_label)

entry_var = tk.StringVar()
entry_var.trace_add("write", on_input_change)

afkbutton = tk.Button(root, text="AFK", bg="black", fg=colortext, command=afk_toggle)
afkbutton.pack(pady=0)

entry = tk.Entry(root, textvariable=entry_var, width=30)
entry.pack(pady=7)
entry.config(bg="black", fg=colortext)

update_label()

root.mainloop()

chat_process.terminate()
chat_process.wait()
log_file.close()

with open("bin/chatboxcontent", "w") as file: file.write("")
