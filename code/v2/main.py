import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

# USER LIBRARIES
from realtimeSignal import Signal
from constants import songList


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        # extra constants
        self.filename = "None chosen..."

        # window setup
        self.title("Automatic Recorder")
        self.state("zoomed")

        # configure rows and columns for auto-scaling
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # setup notebook
        self.book = ttk.Notebook(self)
        self.book.grid(row=0, column=0, sticky="nsew")

        # make frames
        self.hardFrame = ttk.Frame(self.book)
        self.hardFrame.pack(fill='both', expand=True)
        self.realFrame = ttk.Frame(self.book)
        self.realFrame.pack(fill='both', expand=True)

        # hard frame config
        ttk.Label(self.hardFrame, text="Hardcoded Song List", font=("", 20)).place(relx=0.5, rely=0.15, anchor="center")
        songListItems = tk.Variable(value=list([songList[i].name for i in range(len(songList))]))
        songListBox = tk.Listbox(self.hardFrame, listvariable=songListItems, height=len(songList), width=30, font=("", 20), selectmode=tk.SINGLE)
        songListBox.place(relx=0.5, rely=0.45, anchor='center')
        tk.Button(self.hardFrame, text="Click to Play Selected Song",
                                width=75,
                                height=4,
                                command=lambda: songList[songListBox.curselection()[0]].SongPlayback()).place(relx=0.5, rely=0.775, anchor="center")
        
        # real frame config
        ttk.Label(self.realFrame, text="Play Custom Song", font=("", 20)).place(relx=0.5, rely=0.15, anchor="center")
        self.label = ttk.Label(self.realFrame, text=self.filename, font=("", 15))
        self.label.place(relx=0.5,rely=0.3, anchor="center")
        tk.Button(self.realFrame, text="Click to Choose MP3 File", width=75, height=4,command=self.selectFile).place(relx=0.5, rely=0.475, anchor="center")
        tk.Button(self.realFrame, text="Click to Play Song", width=75, height=4,command=self.playCustomSong).place(relx=0.5, rely=0.575, anchor="center")

        # add to notebook
        self.book.add(self.hardFrame, text="Hardcoded Songs")
        self.book.add(self.realFrame, text="Custom Songs")
        

    # other functions
    def selectFile(self):
        filetypes = (
            ("MP3 Files", "*.mp3"),
            ("All Files", "*.*")
        )
        self.filename = fd.askopenfilename(title="Choose an MP3 file...",
                                           initialdir="/dev",
                                           filetypes=filetypes)
        self.label.config(text=self.filename)

        
    def playCustomSong(self):
        if self.filename == "None chosen...":
            return
        Signal.RunFFT(self.filename)


def main():
    root = GUI()    
    root.mainloop() # setting screen into mainloop


if __name__ == '__main__':
    main()
