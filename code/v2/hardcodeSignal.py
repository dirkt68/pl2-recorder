import math
from notes import Notes

class HardcodeSong:
	def __init__(self, name, tempo, notes, rhythm):
		self.name = name #Name of the Song
		#converting tempo from [Beats per Minute] to [Seconds per Beat]
		self.tempo = math.pow((tempo/60), -1)
		#Lists of Notes (To be Converted to GPIO) & Note Lengths
		self.notes = notes 
		self.rhythm = rhythm

	def SongPlayback(self, noteObj:Notes):
		print("Playing Hardcoded Song: " + self.name)
		noteObj.spoolFan()
		Note = ""
		Value = 0
		for i in range(len(self.notes)):
			# Pop a note and rhythm off the two lists
			Note = self.notes[i]
			Value = (self.rhythm[i])*self.tempo
			# Play/Print True note (Find GPIO Pin Input) [[Will eventually become a program to recode the string inputs as GPIO outputs]]
			# print(Note)
			# Wait = (Multiply Rhythm by tempo: Note Len) [[Will use a wait program to send that specific found pitch to the GPIO pins]]
			noteObj.playNote(Note, Value)

		noteObj.GPIOClean()
		