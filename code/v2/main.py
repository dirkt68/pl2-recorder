import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import os

# USER LIBRARIES
from realtimeSignal import Signal
from constants import songList

FILENAME = "None Chosen.."

def selectFile():
    global FILENAME
    filetypes = (
        ("MP3 Files", "*.mp3"),
        ("All Files", "*.*")
    )
    FILENAME = fd.askopenfilename(title="Choose an MP3 file...",
                                  initialdir="/dev",
                                  filetypes=filetypes)


def main():
    root = tk.Tk()
    root.title("Automatic Recorder")
    root.state("zoomed")

    # configure rows and columns for auto-scaling
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # notebook setup
    mainBook = ttk.Notebook(root)
    mainBook.grid(row=0, column=0, sticky="nsew")

    # frame setup
    hardcodeFrame = ttk.Frame(mainBook)
    hardcodeFrame.pack(fill='both',expand=True)
    FFTFrame = ttk.Frame(mainBook)
    FFTFrame.pack(fill='both',expand=True)
    pianoFrame = ttk.Frame(mainBook)
    pianoFrame.pack(fill='both',expand=True)

    # hardcoded songs set up
    ttk.Label(hardcodeFrame, text="Hardcoded Song List", font=("", 20)).place(relx=0.5, rely=0.15, anchor="center")
    songListItems = tk.Variable(value=list([songList[i].name for i in range(len(songList))]))
    songListBox = tk.Listbox(hardcodeFrame, listvariable=songListItems, height=12, width=30, font=("", 20), selectmode=tk.SINGLE)
    songListBox.place(relx=0.5, rely=0.45, anchor='center')
    tk.Button(hardcodeFrame, text="Click to Play Selected Song",
                             width=75,
                             height=4,
                             command=lambda: songList[songListBox.curselection()[0]].SongPlayback()).place(relx=0.5, rely=0.775, anchor="center")

    # custom song zone
    # choose file then send it through the fft
    ttk.Label(FFTFrame, text="Play Custom Song", font=("", 20)).place(relx=0.5, rely=0.15, anchor="center")
    tk.Button(FFTFrame, text="Click to Choose MP3 File", width=75, height=4,command=selectFile).place(relx=0.5, rely=0.775, anchor="center")
    ttk.Label(FFTFrame, text=FILENAME, font=("", 15)).place(relx=0.5,rely=0.3, anchor="center")

    mainBook.add(hardcodeFrame, text="Hardcoded Songs")
    mainBook.add(FFTFrame, text="Custom Songs")
    mainBook.add(pianoFrame, text="Piano Input")

    root.mainloop() # setting screen into mainloop

    
if __name__ == '__main__':
    main()
