import time
import math

class HardcodeSong:
	def __init__(self, name, tempo, notes, rhythm):
		self.name = str (name) #Name of the Song
		#converting tempo from [Beats per Minute] to [Seconds per Beat]
		self.tempo = math.pow((tempo/60), -1)
		#Lists of Notes (To be Converted to GPIO) & Note Lengths
		self.notes = list (notes) 
		self.rhythm = list (rhythm)

	def SongPlayback(self):
		print("Playing Hardcoded Song: " + self.name)
		for i in range(len(self.notes)):
			# Reset after each loop
			Note = ""
			Value = 0
			# Pop a note and rhythm off the two lists
			Note = self.notes[i]
			Value = (self.rhythm[i])*self.tempo
			# Play/Print True note (Find GPIO Pin Input) [[Will eventually become a program to recode the string inputs as GPIO outputs]]
			print(Note)
			# Wait = (Multiply Rhythm by tempo: Note Len) [[Will use a wait program to send that specific found pitch to the GPIO pins]]
			timer = time.time()
			while time.time() - timer <= Value:
				# send GPIO signal corresponding to note for that length of time
				#! need to know which GPIO pins are connected to which solenoid
				continue